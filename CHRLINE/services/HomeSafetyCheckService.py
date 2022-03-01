# -*- coding: utf-8 -*-

class HomeSafetyCheckService(object):
    HomeSafetyCheckService_REQ_TYPE = 4
    HomeSafetyCheckService_RES_TYPE = 4
    HomeSafetyCheckService_API_PATH = "/EXT/home/safety-check/safety-check"

    def __init__(self):
        pass

    def deleteSafetyStatus(self, disasterId: str):
        params = [
            [12, 1, [
                [11, 1, disasterId]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'deleteSafetyStatus', params, self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.HomeSafetyCheckService_API_PATH, sqrd, self.HomeSafetyCheckService_RES_TYPE)

    def getDisasterCases(self):
        params = [
            [12, 1, [
                []
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getDisasterCases', params, self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.HomeSafetyCheckService_API_PATH, sqrd, self.HomeSafetyCheckService_RES_TYPE)

    def updateSafetyStatus(self, disasterId: str, message: str, safetyStatus: int = 1):
        """
        - safetyStatus:
            SAFE(1),
            NOT_SAFE(2);
        """
        params = [
            [12, 1, [
                [11, 1, disasterId],
                [8, 2, safetyStatus],
                [11, 3, message],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'updateSafetyStatus', params, self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.HomeSafetyCheckService_API_PATH, sqrd, self.HomeSafetyCheckService_RES_TYPE)
