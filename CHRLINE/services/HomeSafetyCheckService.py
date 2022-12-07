# -*- coding: utf-8 -*-


class HomeSafetyCheckService(object):
    HomeSafetyCheckService_REQ_TYPE = 3
    HomeSafetyCheckService_RES_TYPE = 3
    HomeSafetyCheckService_API_PATH = "/EXT/home/safety-check/safety-check"

    def __init__(self):
        pass

    def deleteSafetyStatus(self, disasterId: str):
        METHOD_NAME = "deleteSafetyStatus"
        params = [[12, 1, [[11, 1, disasterId]]]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.HomeSafetyCheckService_API_PATH, sqrd,
            self.HomeSafetyCheckService_RES_TYPE)

    def getDisasterCases(self):
        METHOD_NAME = "getDisasterCases"
        params = [[12, 1, []]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.HomeSafetyCheckService_API_PATH,
            sqrd,
            self.HomeSafetyCheckService_RES_TYPE,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")

    def updateSafetyStatus(self,
                           disasterId: str,
                           message: str,
                           safetyStatus: int = 1):
        """
        - safetyStatus:
            SAFE(1),
            NOT_SAFE(2);
        """
        METHOD_NAME = "updateSafetyStatus"
        params = [[
            12, 1,
            [
                [11, 1, disasterId],
                [8, 2, safetyStatus],
                [11, 3, message],
            ]
        ]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.HomeSafetyCheckService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.HomeSafetyCheckService_API_PATH, sqrd,
            self.HomeSafetyCheckService_RES_TYPE)
