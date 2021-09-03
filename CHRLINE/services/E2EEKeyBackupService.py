# -*- coding: utf-8 -*-

class E2EEKeyBackupService(object):
    EKBS_REQ_TYPE = 4
    EKBS_RES_TYPE = 4
    
    def __init__(self):
        pass

    def createE2EEKeyBackup(self, blobHeader: str, blobPayload: str, reason: int):
        """
        - reason
            UNKNOWN(0),
            BACKGROUND_NEW_KEY_CREATED(1),
            BACKGROUND_PERIODICAL_VERIFICATION(2),
            FOREGROUND_NEW_PIN_REGISTERED(3),
            FOREGROUND_VERIFICATION(4);
        """
        params = [
            [12, 2, [
                [11, 1, blobHeader],
                [11, 2, blobPayload],
                [8, 3, reason]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createE2EEKeyBackup', params, self.EKBS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_E2EE_KEY_BACKUP_ENDPOINT, sqrd, self.EKBS_RES_TYPE)

    def getE2EEKeyBackupCertificates(self):
        params = [
            [12, 2, []]
        ]
        sqrd = self.generateDummyProtocol('getE2EEKeyBackupCertificates', params, self.EKBS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_E2EE_KEY_BACKUP_ENDPOINT, sqrd, self.EKBS_RES_TYPE)

    def getE2EEKeyBackupInfo(self):
        params = [
            [12, 2, []]
        ]
        sqrd = self.generateDummyProtocol('getE2EEKeyBackupInfo', params, self.EKBS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_E2EE_KEY_BACKUP_ENDPOINT, sqrd, self.EKBS_RES_TYPE)