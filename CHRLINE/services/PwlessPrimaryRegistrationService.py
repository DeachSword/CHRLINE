# -*- coding: utf-8 -*-

class PwlessPrimaryRegistrationService(object):
    
    def __init__(self):
        pass

    def createSession(self):
        params = []
        sqrd = self.generateDummyProtocol('createSession', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT ,sqrd, 4)

    def getChallengeForPrimaryReg(self, session):
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChallengeForPrimaryReg', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT ,sqrd, 4)

    def registerPrimaryCredential(self, session: str, cId: str, cType: str):
        raise NotImplementedError('RegisterPrimaryCredential id not implemented.')
        params = [
            [12, 1, [
                [11, 1, session],
                [12, 2, [
                    [11, 1, cId],
                    [11, 2, cType],
                    # [12, 3, response],
                    # [12, 4, extensionResults]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('registerPrimaryCredential', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT ,sqrd, 4, access_token=session)