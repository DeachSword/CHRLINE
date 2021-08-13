# -*- coding: utf-8 -*-

class SecondaryPwlessLoginPermitNoticeService(object):
    
    def __init__(self):
        pass

    def checkPwlessPinCodeVerified(self, session):
        params = [
            [12, 1, [
                [11, 1, session],
            ]]
        ]
        sqrd = self.generateDummyProtocol('checkPinCodeVerified', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_PERMIT_ENDPOINT ,sqrd, 4, access_token=session)

    def checkPaakAuthenticated(self, session):
        params = [
            [12, 1, [
                [11, 1, session],
                [11, 2, 'CHANNELGW'],
                [2, 3, True]
            ]]
        ]
        sqrd = self.generateDummyProtocol('checkPaakAuthenticated', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_PERMIT_ENDPOINT ,sqrd, 4, access_token=session)