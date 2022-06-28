
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
    
    def new(self, host, port, path, headers: dict = {}):
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['h2'])
        s = socket.create_connection((host, port))
        self.writer = ctx.wrap_socket(s, server_hostname=host)
        self.conn = h2.connection.H2Connection()
        self.h2_headers = [
            (':method', 'POST'),
            (':authority', host),
            (':scheme', 'https'),
            (':path', path),
        ]
        for h in headers.keys():
            self.h2_headers.append(
                (h, headers[h])
            )
        self.conn.initiate_connection()
        self.conn.send_headers(1, self.h2_headers)
        self.send()

    def send(self):
        self.writer.sendall(self.conn.data_to_send())

    def writeByte(self, data: bytes):
        self.conn.send_data(stream_id=1, data=data, end_stream=False)
        self.send()

    def read(self):
        response_stream_ended = False
        self.writer.sendall(self.conn.data_to_send())
        while not response_stream_ended:
            data = self.writer.recv(65536 * 1024)
            if not data:
                break
            events = self.conn.receive_data(data)
            for event in events:
                if isinstance(event, h2.events.DataReceived):
                    # update flow control so the server doesn't starve us
                    self.conn.acknowledge_received_data(
                        event.flow_controlled_length, event.stream_id)
                        
                    # more response body data received
                    _data = event.data
                    if len(_data):
                        _dl, = struct.unpack("!h", _data[:2])
                        _dt = _data[2]
                        _dd = _data[3:(3+_dl)]
                        if _dt == 1:
                            _pingType = _dd[0]
                            _pingId, = struct.unpack("!h", _dd[1:3])
                            if _pingType == 2:
                                self.writeByte(
                                    bytes([0, 3, 1, 1]) + struct.pack("!h", _pingId)
                                )
                        elif _dt == 3:
                            _requestId, = struct.unpack("!H", _dd[0:2])
                            _isFin = (_requestId & 32768) != 0
                            _requestId &= 32767
                            _responsePayload = _dd[2:]
                            self.manager.OnSignOnResponse(_requestId, _isFin, _responsePayload)
                        elif _dt == 4:
                            _pushType = _dd[0]
                            _serviceType = _dd[1]
                            _pushId, = struct.unpack("!i", _dd[2:6])
                            if _pushType == 2:
                                _pushPayload = _dd[6:]

                                # SEND ACK FOR PUSHES
                                _PushAck = bytes([1] + [_serviceType]) + struct.pack("!i", _pushId) + b''
                                _DATA = struct.pack("!h", len(_PushAck)) + bytes([4]) + _PushAck
                                self.conn.send_data(stream_id=1, data=_DATA, end_stream=False)

                                # Callback
                                self.manager.OnPushResponse(_serviceType, _pushId, _pushPayload)
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

        # close the socket
        self.writer.close()