# -*- coding: utf-8 -*-


class AccessTokenRefreshService(object):

    def __init__(self):
        pass

    def refreshAccessToken(self, refreshToken):
        METHOD_NAME = "refresh"
        params = [[12, 1, [[11, 1, refreshToken]]]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 3)
        return self.postPackDataAndGetUnpackRespData(
            "/EXT/auth/tokenrefresh/v1",
            sqrd,
            3,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")

    def reportRefreshedAccessToken(self, refreshToken):
        METHOD_NAME = "reportRefreshedAccessToken"
        params = [[12, 1, [[11, 1, refreshToken]]]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 3)
        return self.postPackDataAndGetUnpackRespData(
            "/EXT/auth/tokenrefresh/v1",
            sqrd,
            3,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")
