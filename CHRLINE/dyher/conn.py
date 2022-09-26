import time
import socket
import ssl
import struct
import h2.connection

from .connManager import ConnManager


class Conn(object):
    def __init__(self, manager: ConnManager):
        self.manager = manager
        self.conn = None
        self.writer = None
        self.h2_headers = []
        self.is_not_finished = False
        self.cache_data = b""
        self.notFinPayloads = {}

        self._last_send_time = 0
        self._closed = False

    def new(self, host, port, path, headers: dict = {}):
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(["h2"])
        s = socket.create_connection((host, port))
        self.writer = ctx.wrap_socket(s, server_hostname=host)
        self.conn = h2.connection.H2Connection()
        self.h2_headers = [
            (":method", "POST"),
            (":authority", host),
            (":scheme", "https"),
            (":path", path),
        ]
        for h in headers.keys():
            self.h2_headers.append((h, headers[h]))
        self.conn.initiate_connection()
        self.conn.send_headers(1, self.h2_headers)
        self.send()

    def send(self):
        send_data = self.conn.data_to_send()
        self.writer.sendall(send_data)
        self._last_send_time = time.time()

    def writeByte(self, data: bytes):
        self.conn.send_data(stream_id=1, data=data, end_stream=False)
        self.send()

    def wirteRequest(self, requestType: int, data: bytes):
        self.writeByte(self.manager.buildRequest(requestType, data))

    def read(self):
        try:
            response_stream_ended = False
            self.send()
            while not response_stream_ended and self.manager.line_client.is_login:
                data = self.writer.recv(65536 * 1024)
                if not data:
                    break
                events = self.conn.receive_data(data)
                for event in events:
                    if isinstance(event, h2.events.DataReceived):
                        # update flow control so the server doesn't starve us
                        self.conn.acknowledge_received_data(
                            event.flow_controlled_length, event.stream_id
                        )

                        _data = event.data
                        if len(_data) < 4:
                            print(f"[CONN] Invalid Packet: {_data.hex()}")
                            continue
                        self.onDataReceived(_data)
                    elif isinstance(event, h2.events.StreamEnded):
                        # response body completed, let's exit the loop
                        response_stream_ended = True
                        break
                    elif isinstance(event, h2.events.StreamReset):
                        raise RuntimeError("Stream reset: %d" % event.error_code)
                # send any pending data to the server
                self.send()
            self.conn.close_connection()
            self.send()
        except Exception as e:
            self.manager.line_client.log(f"[CONN] task disconnect: {e}")
            raise e
        self._closed = True
        # close the socket
        self.writer.close()

    def IsAble2Request(self):
        if self.manager.line_client.is_login and not self._closed:
            if time.time() - self._last_send_time > 0.5:
                return True
        return False

    def readPacketHeader(self, data):
        (_dl,) = struct.unpack("!H", data[:2])
        _dt = data[2]
        _dd = data[3:]
        return _dt, _dd, _dl

    def onDataReceived(self, data):
        # long data received
        if self.is_not_finished:
            data = self.cache_data + data

        # more response body data received
        _dt, _dd, _dl = self.readPacketHeader(data)
        if _dl > len(_dd):
            self.is_not_finished = True
            self.cache_data = data
            return
        else:
            self.is_not_finished = False
            if len(_dd) > _dl:
                self.onPacketReceived(_dt, _dd[:_dl])
                data = _dd[_dl:]
                self.manager.line_client.log(
                    f"[PUSH] extra data {data.hex()[:50]}...", True
                )
                return self.onDataReceived(data)
        self.onPacketReceived(_dt, _dd)

    def onPacketReceived(self, _dt, _dd):
        if _dt == 1:
            _pingType = _dd[0]
            (_pingId,) = struct.unpack("!H", _dd[1:3])
            self.manager.line_client.log(
                f"[PUSH] receives ping frame. pingId:{_pingId}", True
            )

            if _pingType == 2:
                self.writeByte(bytes([0, 3, 1, 1]) + struct.pack("!H", _pingId))
                self.manager.line_client.log(
                    f"[PUSH] send ping ack. pingId:{_pingId}", True
                )
                self.manager.OnPingCallback(_pingId)
            else:
                raise NotImplementedError(f"ping type not Implemented: {_pingType}")
        elif _dt == 3:
            (I,) = struct.unpack("!H", _dd[0:2])
            _requestId = I & 32767
            # Android using 32768, CHRLINE use (32768 / 2)
            _isFin = (I & 32768) != 0
            _responsePayload = _dd[2:]
            if _isFin:
                if _requestId in self.notFinPayloads:
                    _responsePayload = (
                        self.notFinPayloads[_requestId] + _responsePayload
                    )
                    del self.notFinPayloads[_requestId]
                self.manager.OnSignOnResponse(_requestId, _isFin, _responsePayload)
            else:
                self.manager.line_client.log(
                    f"[PUSH] receives long data. requestId: {_requestId}, I={I}", True
                )
                if _requestId not in self.notFinPayloads:
                    self.notFinPayloads[_requestId] = b""
                self.notFinPayloads[_requestId] += _responsePayload
        elif _dt == 4:
            _pushType = _dd[0]
            _serviceType = _dd[1]
            (_pushId,) = struct.unpack("!i", _dd[2:6])
            self.manager.line_client.log(
                f"[PUSH] receives push frame. service:{_serviceType}", True
            )
            if _pushType in [0, 2]:
                _pushPayload = _dd[6:]

                if _pushType == 2:
                    # SEND ACK FOR PUSHES
                    _PushAck = (
                        bytes([1] + [_serviceType]) + struct.pack("!i", _pushId) + b""
                    )
                    _DATA = struct.pack("!H", len(_PushAck)) + bytes([4]) + _PushAck
                    self.conn.send_data(stream_id=1, data=_DATA, end_stream=False)
                    self.manager.line_client.log(
                        f"[PUSH] send push ack. service:{_serviceType}", True
                    )

                # Callback
                self.manager.OnPushResponse(_serviceType, _pushId, _pushPayload)
            else:
                raise NotImplementedError(f"push type not Implemented: {_pushType}")
        else:
            raise NotImplementedError(
                f"PUSH not Implemented: type:{_dt}, payloads:{_dd[:30]}, len:{len(_dd)}"
            )
