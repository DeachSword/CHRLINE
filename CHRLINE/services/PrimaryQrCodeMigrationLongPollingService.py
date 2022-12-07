# -*- coding: utf-8 -*-

class PrimaryQrCodeMigrationLongPollingService(object):
    PQCMLPS_REQ_TYPE = 4
    PQCMLPS_RES_TYPE = 4
    PQCMLPS_API_PATH = "/EXT/auth/feature-user/lp/api/primary/mig/qr"

    def __init__(self):
        pass
        
    def checkIfEncryptedE2EEKeyReceived(self, sessionId: str, newDevicePublicKey: bytes, encryptedQrIdentifier: str):
        params = [
            [11, 1, sessionId],
            [12, 2, [
                [11, 1, newDevicePublicKey],
                [11, 2, encryptedQrIdentifier]
            ]]
        ]
        params = [
            [12, 1, params]
        ]
        sqrd = self.generateDummyProtocol(
            'checkIfEncryptedE2EEKeyReceived', params, self.PQCMLPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.PQCMLPS_API_PATH ,sqrd, self.PQCMLPS_RES_TYPE, access_token=sessionId)