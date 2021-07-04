# -*- coding: utf-8 -*-
import time
import json

class SquareService(object):

    def __init__(self):
        pass
        
    def inviteIntoSquareChat(self, inviteeMids, squareChatMid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 105, 110, 118, 105, 116, 101, 73, 110, 116, 111, 83, 113, 117, 97, 114, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(inviteeMids)]
        for mid in inviteeMids:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['inviteIntoSquareChat']
        
    def inviteToSquare(self, squareMid, invitees, squareChatMid):
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['inviteToSquare']

    def getJoinedSquares(self, continuationToken=None, limit=50):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 74, 111, 105, 110, 101, 100, 83, 113, 117, 97, 114, 101, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        #sqrd += [11, 0, 2] + self.getStringBytes(continuationToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [0, 0]
        #sqr_rd = sqrd
        #data = bytes(sqr_rd)
        #res = self.req_h2.post(self.LINE_HOST_DOMAIN + self.LINE_SQUARE_QUERY_PATH, data=data, headers=self.square_headers)
        #data = res.content
        #return self.tryReadData(data, mode=0)['getJoinedSquares']
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['getJoinedSquares']

    def markAsRead(self, squareChatMid, messageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 109, 97, 114, 107, 65, 115, 82, 101, 97, 100, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2, 0, 0, 0, len(squareChatMid)]
        for value in squareChatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['markAsRead']

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
        sqrd = [128, 1, 0, 1] + self.getStringBytes("reactToMessage") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 3] + self.getStringBytes(messageId)
        sqrd += [8, 0, 4] + self.getIntBytes(reactionType)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['reactToMessage']

    def findSquareByInvitationTicket(self, invitationTicket):
        sqrd = [128, 1, 0, 1] + self.getStringBytes("findSquareByInvitationTicket") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(invitationTicket)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['findSquareByInvitationTicket']

    def fetchMyEvents(self, subscriptionId=0, syncToken='', continuationToken=None, limit=50):
        sqrd = [128, 1, 0, 1] + self.getStringBytes("fetchMyEvents") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [10, 0, 1] + self.getIntBytes(subscriptionId, 8)
        sqrd += [11, 0, 2] + self.getStringBytes(syncToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [11, 0, 4] + self.getStringBytes(continuationToken)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['fetchMyEvents']

    def fetchSquareChatEvents(self, squareChatMid, syncToken='', subscriptionId=0, limit=50):
        sqrd = [128, 1, 0, 1] + self.getStringBytes("fetchSquareChatEvents") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [10, 0, 1] + self.getIntBytes(subscriptionId, 8)
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 3] + self.getStringBytes(syncToken)
        sqrd += [8, 0, 4] + self.getIntBytes(limit)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['fetchSquareChatEvents']

    def sendSquareMessage(self, squareChatMid, text):
        sqrd = [128, 1, 0, 1] + self.getStringBytes("sendMessage") +  [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [12, 0, 3]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 10] + self.getStringBytes(text)
        sqrd += [8, 0, 15] + self.getIntBytes(0) # contentType
        sqrd += [0]
        sqrd += [8, 0, 3] + self.getIntBytes(4) # fromType
        #sqrd += [10, 0, 4] + self.getIntBytes(0, 8) # squareMessageRevision
        sqrd += [0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT ,sqrd)['sendMessage']