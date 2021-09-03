# -*- coding: utf-8 -*-

class BotExternalService(object):
    BOTE_REQ_TYPE = 3
    BOTE_RES_TYPE = 3
    
    def __init__(self):
        pass

    def notifyOATalkroomEvents(self, eventId: list, type: list, context: list, content: list):
        OATalkroomEvent = []
        for eId in eventId:
            OATalkroomEvent.append([
                [11, 1, eId],
                [8, 2, type],
                # [12, 3, context],
                # [12, 4, content],
            ])
        params = [
            [12, 1, [
                [15, 1, [12, OATalkroomEvent]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('notifyOATalkroomEvents', params, self.BOTE_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_BOT_EXTERNAL_ENDPOINT, sqrd, self.BOTE_RES_TYPE)

    def notifyChatAdEntry(self, chatMid: str, scenarioId: str, sdata: str):
        params = [
            [12, 1, [
                [11, 1, chatMid],
                [11, 2, scenarioId],
                [11, 3, sdata]
            ]]
        ]
        sqrd = self.generateDummyProtocol('notifyChatAdEntry', params, self.BOTE_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_BOT_EXTERNAL_ENDPOINT, sqrd, self.BOTE_RES_TYPE)