# -*- coding: utf-8 -*-

class ChatAppService(object):
    CAPP_REQ_TYPE = 4
    CAPP_RES_TYPE = 4
    
    def __init__(self):
        pass

    def getChatapp(self, chatappId: str, language: str = 'zh_TW'):
        params = [
            [12, 1, [
                [11, 1, chatappId],
                [11, 2, language]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChatapp', params, self.CAPP_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHAT_APP_ENDPOINT, sqrd, self.CAPP_RES_TYPE)

    def getMyChatapps(self, language: str = 'zh_TW', continuationToken: str = None):
        params = [
            [12, 1, [
                [11, 1, language],
                [11, 2, None]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getMyChatapps', params, self.CAPP_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHAT_APP_ENDPOINT, sqrd, self.CAPP_RES_TYPE)