# -*- coding: utf-8 -*-

class AccessTokenRefreshService(object):
    
    def __init__(self):
        pass

    def refreshAccessToken(self, refreshToken):
        params = [
            [12, 1, [
                [11, 1, refreshToken]
            ]]
        ]
        sqrd = self.generateDummyProtocol('refresh', params, 3)
        return self.postPackDataAndGetUnpackRespData("/EXT/auth/tokenrefresh/v1" ,sqrd, 3)