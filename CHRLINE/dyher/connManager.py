
from CHRLINE import CHRLINE
import struct


class ConnManager(object):

    def __init__(self, line_client: CHRLINE):
        self.line_client = line_client
        self.conns = []
        self.hook_callback = None
        self.SignOnRequests = {}
        self.OnSignOnResponse = self._OnSignOnResponse
        self.OnPushResponse = self._OnPushResponse

        self._eventSynced = False
    
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
        _conn.writeByte(self.buildRequest(0, bytes([0, 0, 30])))
        _conn.writeByte(self.buildRequest(2, self.buildSignOnRequest(3)))
        _conn.read()
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
            _req = self.buildFetchMyEventRequest()
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
                [10, 1, 1656326442965],
                [8, 3, 100],
            ]]
        ]
        return bytes(self.line_client.generateDummyProtocol('fetchMyEvents', params, 4))
    
    def _OnSignOnResponse(self, reqId, isFin, data):
        if reqId in self.SignOnRequests:
            serviceType = self.SignOnRequests[reqId]
            cl = self.line_client
            if serviceType == 3:
                data = cl.TCompactProtocol(cl, data)
                resp = data.res
                subscription = cl.checkAndGetValue(resp, 'subscription', 1)
                syncToken = cl.checkAndGetValue(resp, 'syncToken', 3)
                subscriptionId = cl.checkAndGetValue(subscription, 'subscriptionId', 1)
                cl.subscriptionId = subscriptionId
                if not self._eventSynced:
                    cl.setEventSyncToken(syncToken)
                    print(f'Sync EventSyncToken --> {cl.eventSyncToken}')
            else:
                raise NotImplementedError('Not support type: {serviceType}')
    
    def _OnPushResponse(self, serviceType, pushId, pushPayload):
        cl = self.line_client
        cl.log(f'PUSH RECV: id={pushId}, service={serviceType}, payload={pushPayload.hex()}')
        if serviceType == 3:
            for event in self.line_client._Poll__fetchMyEvents():
                _type = cl.checkAndGetValue(event, 'type', 3)
                cl.log(f'[SQ FETER] Event Type --> {_type}')
                self.hook_callback(self.line_client, serviceType, event)
        else:
            raise NotImplementedError('Not support type: {serviceType}')
