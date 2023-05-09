import time
import threading
import struct

from ..client import CHRLINE
from ..services import *


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
        self._access_token = None
    
    @property
    def accessToken(self):
        return self._access_token
    
    @accessToken.setter
    def accessToken(self, newToken):
        self._access_token = newToken

    def initializeConn(self, state: int = 1):
        """Create new conn and return it."""
        from .conn import Conn

        _conn = Conn(self)
        if state == 1:
            self.conns.append(_conn)
            self.accessToken = self.line_client.authToken
        tosend_headers = {
            "x-line-application": self.line_client.server.Headers["x-line-application"],
            "x-line-access": self.accessToken,
        }
        _conn.new("gw.line.naver.jp", 443, "/PUSH/1/subs?m=20", tosend_headers)
        return _conn

    def InitAndRead(self, initServices: list = [3, 5]):
        """Init conn state and read data."""
        if not self.conns:
            raise ValueError("No valid connections found.")
        cl = self.line_client
        _conn = self.conns[0]
        FLAG = 0
        _conn.wirteRequest(0, bytes([0, FLAG, self._pingInterval]))
        cl.log(f"[PUSH] send status frame. flag:{FLAG}, pi:{self._pingInterval}")
        for service in initServices:
            cl.log(f"[PUSH] Init service: {service}")
            ex_val = {}
            if service == 3:
                subscriptionId = int(time.time() * 1000)
                syncToken = ""
                if self.line_client.eventSyncToken is not None:
                    syncToken = str(self.line_client.eventSyncToken)
                ex_val = {
                    "subscriptionId": subscriptionId,
                    "syncToken": syncToken,
                }
                cl.log(
                    f"[SQ_FETCHER][SQ] request fetchMyEvent({subscriptionId}), syncToken:{syncToken}"
                )
                self.subscriptionIds = {}  # clear
            elif service == 5:
                ex_val = {
                    "revision": self.line_client.revision,
                    "count": 100,
                    "globalRev": cl.globalRev,
                    "individualRev": cl.individualRev,
                    "fullSyncRequestReason": None,
                    "lastPartialFullSyncs": None,
                }
                cl.log(f"[FETCHER] request talk fetcher: {ex_val}")
            self.buildAndSendSignOnRequest(_conn, service, **ex_val)
        cl.log(f"[PUSH] CONN start read push.")
        _conn.read()
        cl.log(f"[PUSH] CONN died on PingId={self.curr_ping_id}")
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
        _, reqId = self.buildAndSendSignOnRequest(_conn, serviceType, **kwargs)
        if waitAndReadResp:
            raise NotImplementedError()

            def Callback(self, reqId, data):
                self.OnSignReqResp[reqId] = data

            self.SignOnRequests[reqId][2] = Callback
            return self.OnSignReqResp[reqId]

    def buildRequest(self, service, data):
        """Build request struct."""
        return struct.pack("!H", len(data)) + bytes([service]) + data

    def buildAndSendSignOnRequest(self, conn: any, serviceType: int, **kwargs):
        """
        Build and send sign-on-request.

        ServiceType:
            - 3: fetchMyEvents
            - 5: fecthOps / sync
        """
        cl = self.line_client
        _id = len(self.SignOnRequests) + 1
        _payload = struct.pack("!H", _id)
        _req = None
        serviceName = None
        methodName = None
        if serviceType == 1:
            raise NotImplementedError
        elif serviceType == 3:
            serviceName = "Square"
            methodName = "fetchMyEvents"
            _req = self.buildFetchMyEventsRequest(**kwargs)
        elif serviceType == 5:
            serviceName = "Talk"
            methodName = "fetchOps"
            if cl.DEVICE_TYPE in cl.SYNC_SUPPORT:
                methodName = "sync"
                _req = self.buildServiceRequest(serviceName, methodName, **kwargs)
            else:
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
        self.line_client.log(
            f"[H2][PUSH] send sign-on-request. requestId:{_id}, service:{serviceType}",
            True,
        )
        conn.wirteRequest(2, _payload)
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

    def buildFetchOpsRequest(self, revision: int = -1, **kargs):
        """Build request for fetchOps."""
        cl = self.line_client
        if revision == -1:
            revision = cl.revision
        params = [
            [10, 2, revision],
            [8, 3, 200],  # use 200.
            [10, 4, cl.globalRev],
            [10, 5, cl.individualRev],
        ]
        return bytes(cl.generateDummyProtocol("fetchOps", params, 4))

    def buildServiceRequest(self, serviceName: str, methodName: str, **kargs):
        """Build request for service."""
        cl = self.line_client
        service = f"{serviceName}Service"
        serviceStruct = f"{service}.{service}Struct"
        methodRequest = methodName.title() + "Request"
        unitCalled = f"{serviceStruct}.{methodRequest}"
        ins = eval(f"{unitCalled}")
        payload = ins(**kargs)
        data = cl.generateDummyProtocol(methodName, payload, 4)
        return bytes(data)

    def _OnSignOnResponse(self, reqId, isFin, data):
        if reqId in self.SignOnRequests:
            serviceType = self.SignOnRequests[reqId][0]
            methodName = self.SignOnRequests[reqId][1]
            callback = self.SignOnRequests[reqId][2]
            serviceName = "TalkService"
            cl = self.line_client
            cl.log(
                f"[PUSH] receives sign-on-response frame. requestId:{reqId}, service:{serviceType}, isFin:{isFin}, payload:{data[:20].hex()}",
                True,
            )
            if serviceType == 3:
                data = cl.TCompactProtocol(cl, data)
                resp = data.res
                if "error" in resp:
                    cl.log(
                        f"[SQ_FETCHER][SQ] can't use PUSH for OpenChat:{resp['error']}"
                    )
                    return False
                subscription = cl.checkAndGetValue(resp, "subscription", 1)
                events = cl.checkAndGetValue(resp, "events", 2)
                syncToken = cl.checkAndGetValue(resp, "syncToken", 3)
                subscriptionId = cl.checkAndGetValue(subscription, "subscriptionId", 1)
                cl.log(
                    f"[SQ_FETCHER][SQ] response fetchMyEvent({subscriptionId}) events:{len(events)}, syncToken:{syncToken}"
                )
                cl.subscriptionId = subscriptionId
                if subscriptionId is not None:
                    self.subscriptionIds[subscriptionId] = time.time()
                if not self._eventSynced:
                    cl.setEventSyncToken(syncToken)
                    cl.log(
                        f"[SQ_FETCHER][SQ] myEvents start({subscriptionId}) : syncToken:{cl.eventSyncToken}"
                    )
            elif serviceType == 5:
                _conn = self.conns[0]
                try:
                    data = cl.TMoreCompactProtocol(cl, data)
                    resp = data.res
                    if methodName == "sync":
                        serviceName = "SyncService"
                    if cl.use_thrift:
                        resp = cl.serializeDummyProtocolToThrift(
                            data.dummyProtocol, readWith=f"{serviceName}.{methodName}"
                        )
                    if methodName == "sync":
                        ops = resp
                        sht, shd = cl.talk_handler.SyncHandler(resp)
                        ex_val = {
                            "revision": cl.globalRev,
                            "count": 100,
                            "globalRev": cl.globalRev,
                            "individualRev": cl.individualRev,
                            "fullSyncRequestReason": None,
                            "lastPartialFullSyncs": None,
                        }
                        if sht == 1:
                            ops = shd
                            cl.log(
                                f"[POLLING][PUSH] response sync. operations:{len(ops)}",
                                True,
                            )
                            for op in ops:
                                self.hook_callback(cl, serviceType, op)
                                revision = cl.checkAndGetValue(op, "revision", 1)
                                cl.setRevision(
                                    revision
                                )
                        elif sht == 2:
                            cl.setRevision(shd)
                        else:
                            raise RuntimeError
                        ex_val["revision"] = cl.revision
                        self.buildAndSendSignOnRequest(_conn, serviceType, **ex_val)
                        return
                    elif methodName == "fetchOps":
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
                            self.hook_callback(cl, serviceType, op)
                        # LOOP
                        fetch_req_data = {"revision": cl.revision}
                        self.buildAndSendSignOnRequest(_conn, serviceType, **fetch_req_data)
                    else:
                        # TODO:
                        # Callback resp to ReqId
                        if callback is not None:
                            callback(self, reqId, resp)
                except Exception as e:
                    raise Exception(f"[PUSH] response {methodName} error: {e}")
            else:
                raise ValueError(
                    f"[PUSH] receives invalid sign-on-response frame. requestId:{reqId}, service:{serviceType}"
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
            if cl.subscriptionId != subscriptionId:
                cl.log(
                    f"[SQ_FETCHER][PUSH] subscriptionId not sync: {cl.subscriptionId} -> {subscriptionId},",
                )
                cl.subscriptionId = subscriptionId
            for event in self.line_client._Poll__fetchMyEvents():
                _type = cl.checkAndGetValue(event, "type", 3)
                cl.log(
                    f"[SQ_FETCHER][PUSH] subscriptionId:{subscriptionId}, eventType:{_type}",
                    True,
                )
                self.hook_callback(self.line_client, serviceType, event)
        else:
            raise NotImplementedError(f"Not support type: {serviceType}")

    def _OnPingCallback(self, pingId):
        cl = self.line_client
        self.curr_ping_id = pingId

        # check subscriptionIds need refresh.
        # LOG:
        #   - 221227: change use ts.
        refreshIds = []
        t1 = time.time()
        for subscriptionId in self.subscriptionIds.keys():
            t2 = self.subscriptionIds[subscriptionId]
            if (t1 - t2) >= 3000:
                self.subscriptionIds[subscriptionId] = time.time()
                refreshIds.append(subscriptionId)
        if refreshIds:
            cl.log(f"[SQ_FETCHER][PUSH] refresh subscriptionId: {refreshIds}")
            cl.refreshSquareSubscriptions(refreshIds)

        # when using the PUSH endpoint, you may not be able to update the AuthToken properly.
        # because you can't get the `x-line-next-access` header on the socket connection.
        # here use http protocol to check.
        if pingId % 3 == 0:
            cl.noop()
            oldToken = self.accessToken
            newToken = self.line_client.authToken
            if oldToken != newToken:
                cl.log(f"[PUSH] renew push conn for new authToken...")
                self.accessToken = newToken
                self.conns[0].close()

