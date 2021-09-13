# -*- coding: utf-8 -*-

class SquareBotService(object):

    def __init__(self):
        pass
        
    def getSquareBot(self, botMid):
        params = [
            [12, 1, [
                [11, 1, botMid]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getSquareBot', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_BOT_ENDPOINT ,sqrd, 4)