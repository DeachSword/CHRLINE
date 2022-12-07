import time
import threading
import struct
from ..client import CHRLINE


class ConnManager(object):
    def __init__(self, line_client: CHRLINE):
        self.line_client = line_client
        self.conns = []
        self.hook_callback = None
        self.curr_ping_id = 0
        self.subscriptionIds = {}
        self.SignOnRequests = {}
        self.OnPingCallback = self._OnPingCallback
        self.OnSignReqResp = {}
        self.OnSignOnResponse = self._OnSignOnResponse
        self.OnPushResponse = self._OnPushResponse

        self._eventSynced = False
        self._revisionSynced = False
        self._pingInterval = 30

    def initializeConn(self):
        """Create new conn and return it."""
        from .conn import Conn

        _conn = Conn(self)
        self.conns.append(_conn)
        tosend_headers = {
            "x-line-application": self.line_client.server.Headers["x-line-application"],
            "x-line-access": self.line_client.authToken,
        }
        _conn.new("gw.line.naver.jp", 443, "/PUSH/1/subs?m=20", tosend_headers)
        return _conn

    def InitAndRead(self, initServices: list = [3, 5]):
        """Init conn state and read data."""
        if not self.conns:
            raise ValueError("No valid connections found.")
        _conn = self.conns[0]
        FLAG = 0
        _conn.wirteRequest(0, bytes([0, FLAG, self._pingInterval]))
        self.line_client.log(
            f"[PUSH] send status frame. flag:{FLAG}, pi:{self._pingInterval}"
        )
        for service in initServices:
            self.line_client.log(f"[PUSH] Init service: {service}")
            ex_val = {}
            if service == 3:
                subscriptionId = int(time.time() * 1000)
                syncToken = ""
                ex_val = {
                    "subscriptionId": subscriptionId,
                    "syncToken": syncToken,
                }
                self.line_client.log(
                    f"[SQ_FETCHER][SQ] request fetchMyEvent({subscriptionId}), syncToken:{syncToken}"
                )
            payload, _ = self.buildSignOnRequest(service, **ex_val)
            _conn.wirteRequest(2, payload)
        self.line_client.log(f"[PUSH] CONN start read push.")
        _conn.read()
        self.line_client.log(f"[PUSH] CONN died on PingId={self.curr_ping_id}")
        self.conns.remove(_conn)

    def SendAndReadSignOnRequest(
        self, serviceType, waitAndReadResp: bool = False, **kwargs
    ):
        """Test send request and read response."""
        if not self.conns:
            raise ValueError("No valid connections found.")
        # _conn = self.conns[0]
        conns = []
        for c in self.conns[1:]:
            if c.IsAble2Request():
                conns.append(c)
        if len(conns) < 1:
            pusher = ConnManager(self.line_client)
            pusher.initializeConn()
            # use thread for send pings
            _td = threading.Thread(target=pusher.InitAndRead, args=([],))
            _td.daemon = True
            _td.start()
            _conn = pusher.conns[0]
            self.conns.append(_conn)
        else:
            for c in conns:
                if not c._closed:
                    _conn = c
                    break
        payload, reqId = self.buildSignOnRequest(serviceType, **kwargs)
        _conn.wirteRequest(2, payload)
        if waitAndReadResp:
            raise NotImplementedError()

            def Callback(self, reqId, data):
                self.OnSignReqResp[reqId] = data

            self.SignOnRequests[reqId][2] = Callback
            return self.OnSignReqResp[reqId]

    def buildRequest(self, service, data):
        """Build request struct."""
        return struct.pack("!H", len(data)) + bytes([service]) + data

    def buildSignOnRequest(self, serviceType, **kwargs):
        """
        Build request for fetchMyEvents.

        ServiceType:
            - 3: fetchMyEvents
            - 5: fecthOps
        """
        _id = len(self.SignOnRequests) + 1
        _payload = struct.pack("!H", _id)
        _req = None
        methodName = None
        if serviceType == 1:
            raise NotImplementedError
        elif serviceType == 3:
            methodName = "fetchMyEvents"
            _req = self.buildFetchMyEventsRequest(**kwargs)
        elif serviceType == 5:
            methodName = "fetchOps"
            _req = self.buildFetchOpsRequest(**kwargs)
        elif serviceType == 6:
            raise NotImplementedError
        elif serviceType == "sendMessage":
            raise NotImplementedError
            methodName = "sendMessage"
            serviceType = 5
            _req = self.buildSendMessageRequest(**kwargs)
        else:
            raise ValueError(f"unknow serviceType: {serviceType}")
        _payload += bytes([serviceType, 0])
        _payload += struct.pack("!H", len(_req))
        _payload += _req
        self.SignOnRequests[_id] = [serviceType, methodName, None]
        return _payload, _id

    def buildFetchMyEventsRequest(self, subscriptionId, syncToken):
        """Build request for fetchMyEvents."""
        cl = self.line_client
        params = [
            [
                12,
                1,
                [
                    [10, 1, subscriptionId],
                    [11, 2, syncToken],
                    [8, 3, 100],
                ],
            ]
        ]
        return bytes(cl.generateDummyProtocol("fetchMyEvents", params, 4))

    def buildFetchOpsRequest(self, revision: int = -1):
        """Build request for fetchOps."""
        cl = self.line_client
        if revision == -1:
            revision = cl.revision
        params = [
            [10, 2, revision],
            [8, 3, 100],
            [10, 4, cl.globalRev],
            [10, 5, cl.individualRev],
        ]
        return bytes(cl.generateDummyProtocol("fetchOps", params, 4))

    def _OnSignOnResponse(self, reqId, isFin, data):
        if reqId in self.SignOnRequests:
            serviceType = self.SignOnRequests[reqId][0]
            methodName = self.SignOnRequests[reqId][1]
            callback = self.SignOnRequests[reqId][2]
            cl = self.line_client
            self.line_client.log(
                f"[PUSH] receives sign-on-response frame. requestId:{reqId}, service:{serviceType}, isFin:{isFin}, payload:{data[:20].hex()}",
                True,
            )
            if serviceType == 3:
                data = cl.TCompactProtocol(cl, data)
                resp = data.res
                if "error" in resp:
                    self.line_client.log(
                        f"[SQ_FETCHER][SQ] can't use PUSH for OpenChat:{resp['error']}"
                    )
                    return False
                subscription = cl.checkAndGetValue(resp, "subscription", 1)
                events = cl.checkAndGetValue(resp, "events", 2)
                syncToken = cl.checkAndGetValue(resp, "syncToken", 3)
                subscriptionId = cl.checkAndGetValue(subscription, "subscriptionId", 1)
                self.line_client.log(
                    f"[SQ_FETCHER][SQ] response fetchMyEvent({subscriptionId}) events:{len(events)}, syncToken:{syncToken}"
                )
                cl.subscriptionId = subscriptionId
                if subscriptionId is not None:
                    self.subscriptionIds[subscriptionId] = self.curr_ping_id
                if not self._eventSynced:
                    cl.setEventSyncToken(syncToken)
                    self.line_client.log(
                        f"[SQ_FETCHER][SQ] myEvents start({subscriptionId}) : syncToken:{cl.eventSyncToken}"
                    )
            elif serviceType == 5:
                try:
                    data = cl.TMoreCompactProtocol(cl, data)
                    resp = data.res
                    if cl.use_thrift:
                        resp = cl.serializeDummyProtocolToThrift(
                            data.dummyProtocol, readWith=f"TalkService.{methodName}")
                    if methodName == "fetchOps":
                        ops = resp
                        cl.log(
                            f"[POLLING][PUSH] response fetchOps. operations:{len(ops)}",
                            True,
                        )
                        for op in ops:
                            opType = cl.checkAndGetValue(op, "type", 3)
                            param1 = cl.checkAndGetValue(op, "param1", 10)
                            param2 = cl.checkAndGetValue(op, "param2", 11)
                            if opType == 0:
                                if param1 is not None:
                                    cl.individualRev = param1.split("\x1e")[0]
                                    cl.log(f"individualRev: {cl.individualRev}", True)
                                if param2 is not None:
                                    cl.globalRev = param2.split("\x1e")[0]
                                    cl.log(f"globalRev: {cl.globalRev}", True)
                            cl.setRevision(cl.checkAndGetValue(op, "revision", 1))
                            self.hook_callback(self.line_client, serviceType, op)
                        # LOOP
                        _conn = self.conns[0]
                        fetch_req_data = {"revision": cl.revision}
                        payload, _ = self.buildSignOnRequest(5, **fetch_req_data)
                        _conn.wirteRequest(2, payload)
                    else:
                        # TODO:
                        # Callback resp to ReqId
                        if callback is not None:
                            callback(self, reqId, resp)
                except Exception as e:
                    raise Exception(
                        f"[PUSH] response {methodName} error: {e}"
                    )
            else:
                raise ValueError(
                    "[PUSH] receives invalid sign-on-response frame. requestId:{reqId}, service:{serviceType}"
                )

    def _OnPushResponse(self, serviceType, pushId, pushPayload):
        cl = self.line_client
        tcp = cl.TCompactProtocol(cl, passProtocol=True)
        tcp.data = pushPayload
        subscriptionId = tcp.x(False)[1]
        cl.log(
            f"[PUSH] id:{pushId}, service:{serviceType}, subscriptionId:{subscriptionId}",
            True,
        )
        if serviceType == 3:
            for event in self.line_client._Poll__fetchMyEvents():
                _type = cl.checkAndGetValue(event, "type", 3)
                cl.log(
                    f"[SQ_FETCHER][PUSH] subscriptionId:{subscriptionId}, eventType:{_type}",
                    True,
                )
                self.hook_callback(self.line_client, serviceType, event)
        else:
            raise NotImplementedError("Not support type: {serviceType}")

    def _OnPingCallback(self, pingId):
        cl = self.line_client
        self.curr_ping_id = pingId
        refreshIds = []
        for subscriptionId in self.subscriptionIds.keys():
            pingId2 = self.subscriptionIds[subscriptionId]
            if (pingId - pingId2) * self._pingInterval >= 3600 - self._pingInterval:
                self.subscriptionIds[subscriptionId] = pingId
                refreshIds.append(subscriptionId)
        if refreshIds:
            cl.log(f"[SQ_FETCHER][PUSH] refresh subscriptionId: {refreshIds}")
            self.line_client.refreshSquareSubscriptions(refreshIds)
