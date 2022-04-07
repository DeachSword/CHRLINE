# -*- coding: utf-8 -*-
import time
import json


class SquareService(object):


    SQUARE_EXCEPTION = {
        'code': 1,
        'message': 3,
        'metadata': 2
    }

    def __init__(self):
        pass

    def inviteIntoSquareChat(self, inviteeMids, squareChatMid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 105, 110, 118, 105, 116, 101, 73, 110,
                116, 111, 83, 113, 117, 97, 114, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(inviteeMids)]
        for mid in inviteeMids:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def inviteToSquare(self, squareMid, invitees, squareChatMid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("inviteToSquare") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(squareMid)
        sqrd += [15, 0, 3, 11, 0, 0, 0, len(invitees)]
        for mid in invitees:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 4] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def getJoinedSquares(self, continuationToken=None, limit=50):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 74, 111, 105,
                110, 101, 100, 83, 113, 117, 97, 114, 101, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        #sqrd += [11, 0, 2] + self.getStringBytes(continuationToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [0, 0]
        #sqr_rd = sqrd
        #data = bytes(sqr_rd)
        #res = self.req_h2.post(self.LINE_HOST_DOMAIN + self.LINE_SQUARE_QUERY_PATH, data=data, headers=self.square_headers)
        #data = res.content
        # return self.tryReadData(data, mode=0)['getJoinedSquares']
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def markAsRead(self, squareChatMid, messageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 109, 97, 114,
                107, 65, 115, 82, 101, 97, 100, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2, 0, 0, 0, len(squareChatMid)]
        for value in squareChatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

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
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("reactToMessage") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 3] + self.getStringBytes(messageId)
        sqrd += [8, 0, 4] + self.getIntBytes(reactionType)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def findSquareByInvitationTicket(self, invitationTicket):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("findSquareByInvitationTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(invitationTicket)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def fetchMyEvents(self, subscriptionId=0, syncToken='', continuationToken=None, limit=50):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("fetchMyEvents") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [10, 0, 1] + self.getIntBytes(subscriptionId, 8)
        sqrd += [11, 0, 2] + self.getStringBytes(syncToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [11, 0, 4] + self.getStringBytes(continuationToken)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def fetchSquareChatEvents(self, squareChatMid, syncToken='', subscriptionId=0, limit=50):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("fetchSquareChatEvents") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [10, 0, 1] + self.getIntBytes(subscriptionId, 8)
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 3] + self.getStringBytes(syncToken)
        sqrd += [8, 0, 4] + self.getIntBytes(limit)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def sendSquareMessage(self, squareChatMid, text):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("sendMessage") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [12, 0, 3]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [11, 0, 10] + self.getStringBytes(text)
        sqrd += [8, 0, 15] + self.getIntBytes(0)  # contentType
        sqrd += [0]
        sqrd += [8, 0, 3] + self.getIntBytes(4)  # fromType
        # sqrd += [10, 0, 4] + self.getIntBytes(0, 8) # squareMessageRevision
        sqrd += [0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, baseException=SquareService.SQUARE_EXCEPTION)

    def getSquare(self, squareMid):
        params = [
            [12, 1, [
                [11, 2, squareMid]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getSquare', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, 4, encType=0, baseException=SquareService.SQUARE_EXCEPTION)

    def getJoinableSquareChats(self, squareMid, continuationToken=None):
        params = [
            [12, 1, [
                [11, 2, squareMid],
                [11, 10, continuationToken],
                [8, 11, 100]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getJoinableSquareChats', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, 4, encType=0, baseException=SquareService.SQUARE_EXCEPTION)

    def createSquare(self, name: str, displayName: str, profileImageObsHash: str = "0h6tJf0hQsaVt3H0eLAsAWDFheczgHd3wTCTx2eApNKSoefHNVGRdwfgxbdgUMLi8MSngnPFMeNmpbLi8MSngnPFMeNmpbLi8MSngnOA", desc: str = "test with CHRLINE API", searchable: bool = True, SquareJoinMethodType: int = 0):
        """
        - SquareJoinMethodType
            NONE(0),
            APPROVAL(1),
            CODE(2);
        """
        params = [
            [12, 1, [
                [8, 2, self.getCurrReqId()],
                [12, 2, [
                    [11, 2, name],
                    [11, 4, profileImageObsHash],
                    [11, 5, desc],
                    [2, 6, searchable],
                    [8, 7, 1],  # type
                    [8, 8, 1],  # categoryId
                    [10, 10, 0],  # revision
                    [2, 11, True],  # ableToUseInvitationTicket
                    [12, 14, [
                        [8, 1, SquareJoinMethodType]
                    ]],
                    [2, 15, False],  # adultOnly
                    [15, 16, [11, []]]  # svcTags
                ]],
                [12, 3, [
                    [11, 3, displayName],
                    # [11, 4, profileImageObsHash],
                    [2, 5, True],  # ableToReceiveMessage
                    [10, 9, 0],  # revision
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createSquare', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, 4, encType=0, baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatAnnouncements(self, squareMid: str):
        params = [
            [12, 1, [
                [11, 2, squareMid],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getSquareChatAnnouncements', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_SQUARE_ENDPOINT, sqrd, 4, encType=0, baseException=SquareService.SQUARE_EXCEPTION)

    def leaveSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareChatMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChatMember", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def searchSquares(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquares is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchSquares", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareFeatureSet(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareFeatureSet is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareFeatureSet", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def joinSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("joinSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "joinSquare", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquarePopularKeywords(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularKeywords is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularKeywords", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def reportSquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareMessage", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMemberRelation", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def leaveSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveSquare", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareMemberRelations(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelations is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMemberRelations", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def removeSquareSubscriptions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeSubscriptions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "removeSubscriptions", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareMessageReactions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getMessageReactions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getMessageReactions", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def destroySquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "destroyMessage", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def reportSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def unsendSquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("unsendMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "unsendMessage", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def deleteSquareChatAnnouncement(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChatAnnouncement is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquareChatAnnouncement", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def createSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def deleteSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareChatMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChatMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareFeatureSet(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareFeatureSet is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareFeatureSet", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareAuthority", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def rejectSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "rejectSquareMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def deleteSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquare", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def reportSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquare", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareInvitationTicketUrl(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getInvitationTicketUrl is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getInvitationTicketUrl", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareChatMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareChatMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareChatMember", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMember", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquare", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareAuthorities(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthorities is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareAuthorities", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def updateSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareChatStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChatStatus", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def approveSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("approveSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "approveSquareMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareStatus", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def searchSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchSquareMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def checkSquareJoinCode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("checkJoinCode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "checkJoinCode", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def createSquareChatAnnouncement(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createSquareChatAnnouncement is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createSquareChatAnnouncement", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareAuthority", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def refreshSquareSubscriptions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("refreshSubscriptions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "refreshSubscriptions", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getJoinedSquareChats(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getJoinedSquareChats is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getJoinedSquareChats", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def joinSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("joinSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "joinSquareChat", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def findSquareByEmid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSquareByEmid is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findSquareByEmid", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMemberRelation", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMember", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def destroySquareMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessages is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "destroyMessages", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareCategories(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCategories is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCategories", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def reportSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareMember", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def getSquareNoteStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNoteStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNoteStatus", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)

    def searchSquareChatMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquareChatMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchSquareChatMembers", params, SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SquareService_API_PATH, sqrd, SquareService_RES_TYPE)
