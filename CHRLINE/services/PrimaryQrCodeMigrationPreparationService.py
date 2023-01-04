# -*- coding: utf-8 -*-

class PrimaryQrCodeMigrationPreparationService(object):
    PQCMPS_REQ_TYPE = 4
    PQCMPS_RES_TYPE = 4
    PQCMPS_API_PATH = "/EXT/auth/feature-user/api/primary/mig/qr/prepare"

    def __init__(self):
        pass
        
    def createQRMigrationSession(self):
        params = [
            [12, 1, []]
        ]
        sqrd = self.generateDummyProtocol(
            'createSession', params, self.PQCMPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.PQCMPS_API_PATH ,sqrd, self.PQCMPS_RES_TYPE)
        
    def sendEncryptedE2EEKey(self, sessionId: str, recoveryKey: bytes, backupBlobPayload: bytes):
        params = [
            [12, 1, [
                [11, 1, sessionId],
                [12, 2, [
                    [11, 1, recoveryKey],
                    [11, 2, backupBlobPayload] 
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'sendEncryptedE2EEKey', params, self.PQCMPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.PQCMPS_API_PATH ,sqrd, self.PQCMPS_RES_TYPE)