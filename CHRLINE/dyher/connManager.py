
from CHRLINE import CHRLINE
import struct


class ConnManager(object):

    def __init__(self, line_client: CHRLINE):
        self.line_client = line_client
        self.conns = []
        self.hook_callback = None
        self.curr_ping_id = 0
        self.subscriptionIds = {}
        self.SignOnRequests = {}
        self.OnPingCallback = self._OnPingCallback
        self.OnSignOnResponse = self._OnSignOnResponse
        self.OnPushResponse = self._OnPushResponse

        self._eventSynced = False
        self._revisionSynced = False
        self._pingInterval = 30
    
    def initializeConn(self):
        from .conn import Conn
        _conn = Conn(self)
        self.conns.append(_conn)
        tosend_headers = {
            "x-line-application": self.line_client.server.Headers['x-line-application'],
            "x-line-access": self.line_client.authToken,
        }
        _conn.new("gw.line.naver.jp", 443, "/PUSH/1/subs?m=20", tosend_headers)
    
    def InitAndRead(self, initServices: list = [3, 5]):
        if not self.conns:
            raise ValueError("No valid connections found.")
        _conn = self.conns[0]
        _conn.writeByte(self.buildRequest(0, bytes([0, 0, self._pingInterval])))
        for service in initServices:
            _conn.writeByte(self.buildRequest(2, self.buildSignOnRequest(service)))
        _conn.read()
        print('CONN died')
        self.conns.remove(_conn)
    
    def buildRequest(self, service, data):
        return struct.pack("!h", len(data)) + bytes([service]) + data
    
    def buildSignOnRequest(self, serviceType, **kwargs):
        """
        ServiceType:
            - 3: fetchMyEvents
            - 5: fecthOps
        """
        _id = len(self.SignOnRequests) + 1
        _payload = struct.pack("!H", _id)
        _req = None
        if serviceType == 3:
            # fetchMyEvents
            _req = self.buildFetchMyEventRequest(**kwargs)
        elif serviceType == 5:
            # fetchOps
            _req = self.buildFetchOpsRequest(**kwargs)
        else:
            raise ValueError(f"unknow serviceType: {serviceType}")
        _payload += bytes([serviceType, 0])
        _payload += struct.pack("!H", len(_req))
        _payload += _req
        self.SignOnRequests[_id] = serviceType
        return _payload
    
    def buildFetchMyEventRequest(self,):
        params = [
            [12, 1, [
                [10, 1, 101],
                [8, 3, 100],
            ]]
        ]
        return bytes(self.line_client.generateDummyProtocol('fetchMyEvents', params, 4))
    
    def buildFetchOpsRequest(self, revision: int = -1):
        cl = self.line_client
        params = [
            [10, 2, revision],
            [8, 3, 100],
            [10, 4, cl.globalRev],
            [10, 5, cl.individualRev]
        ]
        return bytes(self.line_client.generateDummyProtocol('fetchOps', params, 4))
    
    def _OnSignOnResponse(self, reqId, isFin, data):
        if reqId in self.SignOnRequests:
            serviceType = self.SignOnRequests[reqId]
            cl = self.line_client
            if serviceType == 3:
                data = cl.TCompactProtocol(cl, data)
                resp = data.res
                subscription = cl.checkAndGetValue(resp, 'subscription', 1)
                syncToken = cl.checkAndGetValue(resp, 'syncToken', 3)
                print(subscription)
                subscriptionId = cl.checkAndGetValue(subscription, 'subscriptionId', 1)
                cl.subscriptionId = subscriptionId
                if subscriptionId is not None: 
                    self.subscriptionIds[subscriptionId] = self.curr_ping_id
                if not self._eventSynced:
                    cl.setEventSyncToken(syncToken)
                    print(f'Sync EventSyncToken --> {cl.eventSyncToken}, subscriptionId={subscriptionId}')
            elif serviceType == 5:
                data = cl.TMoreCompactProtocol(cl, data)
                ops = data.res
                for op in ops:
                    opType = cl.checkAndGetValue(
                        op, 'type', 3)
                    param1 = cl.checkAndGetValue(
                        op, 'param1', 10)
                    param2 = cl.checkAndGetValue(
                        op, 'param2', 11)
                    if opType == 0:
                        if param1 is not None:
                            cl.individualRev = param1.split('\x1e')[0]
                            cl.log(
                                f"individualRev: {cl.individualRev}", True)
                        if param2 is not None:
                            cl.globalRev = param2.split('\x1e')[0]
                            cl.log(f"globalRev: {cl.globalRev}", True)
                    cl.setRevision(cl.checkAndGetValue(op, 'revision', 1))
                    self.hook_callback(self.line_client, serviceType, op)
                _conn = self.conns[0]
                _conn.writeByte(
                    self.buildRequest(2, self.buildSignOnRequest(5, **{
                        "revision": cl.revision
                    })))
            else:
                raise NotImplementedError('Not support type: {serviceType}')
    
    def _OnPushResponse(self, serviceType, pushId, pushPayload):
        cl = self.line_client
        tcp = cl.TCompactProtocol(cl, passProtocol=True)
        tcp.data = pushPayload
        subscriptionId = tcp.x(False)[1]
        cl.log(f'PUSH RECV: id={pushId}, service={serviceType}, subscriptionId={subscriptionId}')
        if serviceType == 3:
            for event in self.line_client._Poll__fetchMyEvents():
                _type = cl.checkAndGetValue(event, 'type', 3)
                cl.log(f'[SQ FETER] Event Type --> {_type}')
                self.hook_callback(self.line_client, serviceType, event)
        else:
            raise NotImplementedError('Not support type: {serviceType}')
    
    def _OnPingCallback(self, pingId):
        cl = self.line_client
        self.curr_ping_id = pingId
        refreshIds = []
        for subscriptionId in self.subscriptionIds.keys():
            pingId2 = self.subscriptionIds[subscriptionId]
            if (pingId - pingId2) * self._pingInterval >= 3600:
                self.subscriptionIds[subscriptionId] = pingId
                refreshIds.append(subscriptionId)
                cl.log(
                    f'refresh subscriptionId: {subscriptionId}')
        if refreshIds:
            self.line_client.refreshSquareSubscriptions(refreshIds)

