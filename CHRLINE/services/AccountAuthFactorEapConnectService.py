# -*- coding: utf-8 -*-

class AccountAuthFactorEapConnectService(object):
    AAFEC_REQ_TYPE = 3
    AAFEC_RES_TYPE = 3

    def __init__(self):
        pass

    def connectEapAccount(self, authSessionId: str):
        params = [
            [12, 1, [
                [11, 1, authSessionId]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'connectEapAccount', params, self.AAFEC_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_EAP_ENDPOINT, sqrd, self.AAFEC_RES_TYPE)

    def disconnectEapAccount(self, eapType: int = 3):
        params = [
            [12, 1, [
                [8, 1, eapType]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'disconnectEapAccount', params, self.AAFEC_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_EAP_ENDPOINT, sqrd, self.AAFEC_RES_TYPE)

    def getHashedPpidForYahoojapan(self):
        params = [
            [12, 1, []]
        ]
        sqrd = self.generateDummyProtocol(
            'getHashedPpidForYahoojapan', params, self.AAFEC_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_EAP_ENDPOINT, sqrd, self.AAFEC_RES_TYPE)

    def openAAFECSession(self, udid: str, deviceModel: str = "Pixel 2"):
        params = [
            [12, 1, [
                [12, 1, [
                    [11, 1, udid],  # len 32
                    [11, 1, deviceModel]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'openSession', params, self.AAFEC_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_EAP_ENDPOINT, sqrd, self.AAFEC_RES_TYPE)

    def verifyEapLogin(self, authSessionId: str, type: int, accessToken: str):
        """
        - type:
            UNKNOWN(0),
            FACEBOOK(1),
            APPLE(2),
            YAHOOJAPAN(3);
        """
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [12, 2, [
                    [8, 1, type],
                    [11, 2, accessToken]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'verifyEapLogin', params, self.AAFEC_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_EAP_ENDPOINT, sqrd, self.AAFEC_RES_TYPE)
