# -*- coding: utf-8 -*-
import time
import json

class SquareService(object):

    def __init__(self):
        pass
        
    def inviteIntoSquareChat(self, inviteeMids, squareChatMid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/SQS1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 105, 110, 118, 105, 116, 101, 73, 110, 116, 111, 83, 113, 117, 97, 114, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(inviteeMids)]
        for mid in inviteeMids:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req_h2.post(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        print(data)
        return self.tryReadData(data)
        
    def inviteToSquare(self, squareMid, invitees, squareChatMid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/SQS1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes("inviteToSquare") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(squareMid)
        sqrd += [15, 0, 3, 11, 0, 0, 0, len(invitees)]
        for mid in invitees:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 4] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req_h2.post(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getJoinedSquares(self, continuationToken=None, limit=50):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/SQS1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 74, 111, 105, 110, 101, 100, 83, 113, 117, 97, 114, 101, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        #sqrd += [11, 0, 2] + self.getStringBytes(continuationToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req_h2.post("https://gf.line.naver.jp/SQS1", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def markAsRead(self, squareChatMid, messageId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/SQS1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 109, 97, 114, 107, 65, 115, 82, 101, 97, 100, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2, 0, 0, 0, len(squareChatMid)]
        for value in squareChatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def reactToMessage(self, squareChatMid, messageId, reactionType=2):
        """
        - reactionType
            ALL     = 0,
            UNDO    = 1,
            NICE    = 2,
            LOVE    = 3,
            FUN     = 4,
            AMAZING = 5,
            SAD     = 6,
            OMG     = 7,
        """
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/SQS1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes("reactToMessage") +  [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 3] + self.getStringBytes(messageId)
        sqrd += [8, 0, 4] + self.getIntBytes(reactionType)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req_h2.post(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['reactToMessage']