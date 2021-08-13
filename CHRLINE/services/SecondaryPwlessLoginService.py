# -*- coding: utf-8 -*-

class SecondaryPwlessLoginService(object):
    
    def __init__(self):
        pass

    def createPwlessSession(self, phone, region='TW'):
        params = [
            [12, 1, [
                [11, 1, phone],
                [11, 2, region]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createSession', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 4)

    def verifyLoginCertificate(self, session, cert=None):
        params = [
            [12, 1, [
                [11, 1, session],
                [11, 2, cert]
            ]]
        ]
        sqrd = self.generateDummyProtocol('verifyLoginCertificate', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 4)

    def requestPinCodeVerif(self, session):
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        sqrd = self.generateDummyProtocol('requestPinCodeVerif', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 4)

    def putExchangeKey(self, session, temporalPublicKey, e2eeVersion=1):
        params = [
            [12, 1, [
                [11, 1, session],
                [13, 2, [11, 11, {
                    'e2eeVersion': str(e2eeVersion),
                    'temporalPublicKey': temporalPublicKey
                }]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('putExchangeKey', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 4)

    def requestPaakAuth(self, session):
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        sqrd = self.generateDummyProtocol('requestPaakAuth', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 4)

    def getE2eeKey(self, session):
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getE2eeKey', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 3)

    def pwlessLogin(self, session):
        params = [
            [12, 1, [
                [11, 1, session],
                [11, 2, "DeachSword-CHRLINE"],
                [11, 3, "CHANNELGW"]
            ]]
        ]
        sqrd = self.generateDummyProtocol('login', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 3)

    def pwlessLoginV2(self, session):
        params = [
            [12, 1, [
                [11, 1, session],
                [2, 2, True],
                [11, 3, "DeachSword-CHRLINE"],
                [11, 4, "CHANNELGW"]
            ]]
        ]
        sqrd = self.generateDummyProtocol('loginV2', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT ,sqrd, 3)