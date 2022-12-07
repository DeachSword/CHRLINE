# -*- coding: utf-8 -*-
import time
import json


class SquareService(object):
    SquareService_REQ_TYPE = 4
    SquareService_RES_TYPE = 4
    SquareService_API_PATH = "/SQS1"

    SQUARE_EXCEPTION = {'code': 1, 'message': 3, 'metadata': 2}

    def __init__(self):
        self.SquareService_API_PATH = self.LINE_SQUARE_ENDPOINT

    def inviteIntoSquareChat(self, inviteeMids, squareChatMid):
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 20, 105, 110, 118, 105, 116, 101, 73, 110,
            116, 111, 83, 113, 117, 97, 114, 101, 67, 104, 97, 116, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(inviteeMids)]
        for mid in inviteeMids:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 2] + self.getStringBytes(squareChatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getJoinedSquares(self, continuationToken=None, limit=50):
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 74, 111, 105, 110, 101,
            100, 83, 113, 117, 97, 114, 101, 115, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        #sqrd += [11, 0, 2] + self.getStringBytes(continuationToken)
        sqrd += [8, 0, 3] + self.getIntBytes(limit)
        sqrd += [0, 0]
        #sqr_rd = sqrd
        #data = bytes(sqr_rd)
        #res = self.req_h2.post(self.LINE_HOST_DOMAIN + self.LINE_SQUARE_QUERY_PATH, data=data, headers=self.square_headers)
        #data = res.content
        # return self.tryReadData(data, mode=0)['getJoinedSquares']
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

    def markAsRead(self, squareChatMid, messageId):
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 10, 109, 97, 114, 107, 65, 115, 82, 101, 97,
            100, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2, 0, 0, 0, len(squareChatMid)]
        for value in squareChatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

    def findSquareByInvitationTicket(self, invitationTicket):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("findSquareByInvitationTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 2] + self.getStringBytes(invitationTicket)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            baseException=SquareService.SQUARE_EXCEPTION)

    def fetchMyEvents(self,
                      subscriptionId: int = 0,
                      syncToken: str = None,
                      continuationToken: str = None,
                      limit: int = 100):
        params = [[
            12, 1,
            [[10, 1, subscriptionId], [11, 2, syncToken], [8, 3, limit],
             [11, 4, continuationToken]]
        ]]
        sqrd = self.generateDummyProtocol('fetchMyEvents', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            baseException=SquareService.SQUARE_EXCEPTION)

    def fetchSquareChatEvents(self,
                              squareChatMid,
                              syncToken='',
                              subscriptionId=0,
                              limit=100):
        params = [[
            12,
            1,
            [
                [10, 1, subscriptionId],
                [11, 2, squareChatMid],
                # [11, 3, syncToken],
                [8, 4, limit],
                [8, 5, 1],  # direction
                [8, 6, 1],  # inclusive
                # [11, 7, continuationToken]
            ]
        ]]
        sqrd = self.generateDummyProtocol('fetchSquareChatEvents', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            baseException=SquareService.SQUARE_EXCEPTION)

    def sendSquareMessage(self,
                          squareChatMid: str,
                          text: str,
                          contentType: int = 0,
                          contentMetadata: dict = {},
                          relatedMessageId: str = None):
        message = [
            # [11, 1, _from],
            [11, 2, squareChatMid],
            [11, 10, text],
            [8, 15, contentType],  # contentType
            [13, 18, [11, 11, contentMetadata]],
        ]
        if relatedMessageId is not None:
            message.append([11, 21, relatedMessageId])
            message.append([
                8, 22, 3
            ]  # messageRelationType; FORWARD(0), AUTO_REPLY(1), SUBORDINATE(2), REPLY(3);
                           )
            message.append(
                [8, 24,
                 2]  # relatedMessageServiceCode; 1 for Talk 2 for Square
            )
        params = [[
            12,
            1,
            [
                [8, 1, self.getCurrReqId()],  # reqSeq
                [11, 2, squareChatMid],
                [
                    12,
                    3,
                    [
                        [12, 1, message],
                        [8, 3, 4],  # fromType
                        # [10, 4, 0],  # squareMessageRevision
                        # [8, 5, 1]
                    ]
                ],
            ]
        ]]
        sqrd = self.generateDummyProtocol('sendMessage', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def sendSquareTextMessage(self,
                              squareChatMid: str,
                              text: str,
                              contentMetadata: dict = {},
                              relatedMessageId: str = None):
        return self.sendSquareMessage(squareChatMid, text, 0, contentMetadata,
                                      relatedMessageId)

    def getSquare(self, squareMid):
        params = [[12, 1, [[11, 2, squareMid]]]]
        sqrd = self.generateDummyProtocol('getSquare', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getJoinableSquareChats(self, squareMid, continuationToken=None):
        params = [[
            12, 1,
            [[11, 2, squareMid], [11, 10, continuationToken], [8, 11, 100]]
        ]]
        sqrd = self.generateDummyProtocol('getJoinableSquareChats', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def createSquare(
            self,
            name: str,
            displayName: str,
            profileImageObsHash:
        str = "0h6tJf0hQsaVt3H0eLAsAWDFheczgHd3wTCTx2eApNKSoefHNVGRdwfgxbdgUMLi8MSngnPFMeNmpbLi8MSngnPFMeNmpbLi8MSngnOA",
            desc: str = "test with CHRLINE API",
            searchable: bool = True,
            SquareJoinMethodType: int = 0):
        """
        - SquareJoinMethodType
            NONE(0),
            APPROVAL(1),
            CODE(2);
        """
        params = [[
            12,
            1,
            [
                [8, 2, self.getCurrReqId()],
                [
                    12,
                    2,
                    [
                        [11, 2, name],
                        [11, 4, profileImageObsHash],
                        [11, 5, desc],
                        [2, 6, searchable],
                        [8, 7, 1],  # type
                        [8, 8, 1],  # categoryId
                        [10, 10, 0],  # revision
                        [2, 11, True],  # ableToUseInvitationTicket
                        [12, 14, [[8, 1, SquareJoinMethodType]]],
                        [2, 15, False],  # adultOnly
                        [15, 16, [11, []]]  # svcTags
                    ]
                ],
                [
                    12,
                    3,
                    [
                        [11, 3, displayName],
                        # [11, 4, profileImageObsHash],
                        [2, 5, True],  # ableToReceiveMessage
                        [10, 9, 0],  # revision
                    ]
                ]
            ]
        ]]
        sqrd = self.generateDummyProtocol('createSquare', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatAnnouncements(self, squareMid: str):
        params = [[12, 1, [
            [11, 2, squareMid],
        ]]]
        sqrd = self.generateDummyProtocol('getSquareChatAnnouncements', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def leaveSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("leaveSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareChatMember", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def searchSquares(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquares is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("searchSquares", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareFeatureSet(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareFeatureSet is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareFeatureSet", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def joinSquare(self,
                   squareMid,
                   displayName,
                   ableToReceiveMessage: bool = False,
                   passCode: str = None):
        params = [[
            12, 1,
            [[11, 2, squareMid],
             [
                 12, 3,
                 [
                     [11, 2, squareMid],
                     [11, 3, displayName],
                     [2, 5, ableToReceiveMessage],
                     [10, 9, 0],
                 ]
             ], [12, 5, [[12, 2, [[11, 1, passCode]]]]]]
        ]]
        sqrd = self.generateDummyProtocol('joinSquare', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquarePopularKeywords(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularKeywords is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getPopularKeywords", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def reportSquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSquareMessage", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareMemberRelation", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def leaveSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("leaveSquare", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareMemberRelations(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelations is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareMemberRelations", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def removeSquareSubscriptions(self, subscriptionIds: list = []):
        params = [[12, 1, [
            [15, 2, [10, subscriptionIds]],
        ]]]
        sqrd = self.generateDummyProtocol('removeSubscriptions', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareMessageReactions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getMessageReactions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getMessageReactions", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def destroySquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("destroyMessage", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def reportSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def unsendSquareMessage(self, squareChatMid: str, messageId: str):
        """
        Unsend message for square.

        2022/09/19: Added.
        """
        METHOD_NAME = "unsendMessage"
        params = SquareServiceStruct.UnsendMessageRequest(
            squareChatMid, messageId)
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")

    def deleteSquareChatAnnouncement(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChatAnnouncement is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("deleteSquareChatAnnouncement",
                                          params, self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def createSquareChat(self,
                         squareChatMid: str,
                         name: str,
                         chatImageObsHash: str,
                         squareChatType: int = 1,
                         maxMemberCount: int = 5000,
                         ableToSearchMessage: int = 1,
                         squareMemberMids: list = []):
        """
        - SquareChatType:
            OPEN(1),
            SECRET(2),
            ONE_ON_ONE(3),
            SQUARE_DEFAULT(4);
        - ableToSearchMessage:
            NONE(0),
            OFF(1),
            ON(2);
        """
        params = [[
            12, 1,
            [[8, 1, self.getCurrReqId()],
             [
                 12, 2,
                 [[11, 1, squareChatMid], [8, 3, squareChatType],
                  [11, 4, name], [11, 5, chatImageObsHash],
                  [8, 7, maxMemberCount], [8, 11, ableToSearchMessage]]
             ], [15, 3, [11, squareMemberMids]]]
        ]]
        sqrd = self.generateDummyProtocol("createSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def deleteSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("deleteSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatMembers(self,
                             squareChatMid: str,
                             continuationToken: str = None,
                             limit: int = 200):
        GetSquareChatMembersRequest = [[11, 1, squareChatMid], [8, 3, limit]]
        if continuationToken is not None:
            GetSquareChatMembersRequest.append([11, 2, continuationToken])
        params = [[12, 1, GetSquareChatMembersRequest]]
        sqrd = self.generateDummyProtocol("getSquareChatMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareFeatureSet(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareFeatureSet is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareFeatureSet", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareAuthority", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def rejectSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("rejectSquareMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def deleteSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("deleteSquare", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def reportSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSquare", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareInvitationTicketUrl(self, mid: str):
        params = [[12, 1, [
            [11, 2, mid],
        ]]]
        sqrd = self.generateDummyProtocol('getInvitationTicketUrl', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareChatMember(self,
                               squareMemberMid: str,
                               squareChatMid: str,
                               notificationForMessage: bool = True,
                               notificationForNewMember: bool = True,
                               updatedAttrs: list = [6]):
        """
        - SquareChatMemberAttribute:
            MEMBERSHIP_STATE(4),
            NOTIFICATION_MESSAGE(6),
            NOTIFICATION_NEW_MEMBER(7);
        """
        params = [[
            12, 1,
            [
                [14, 2, [8, updatedAttrs]],
                [
                    12, 3,
                    [
                        [11, 1, squareMemberMid],
                        [11, 2, squareChatMid],
                        [2, 5, notificationForMessage],
                        [2, 6, notificationForNewMember],
                    ]
                ],
            ]
        ]]
        sqrd = self.generateDummyProtocol('updateSquareChatMember', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareMember", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquare", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareAuthorities(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthorities is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareAuthorities", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def updateSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSquareMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareChatStatus", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def approveSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("approveSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("approveSquareMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareStatus", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def searchSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("searchSquareMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def checkSquareJoinCode(self, squareMid: str, code: str):
        params = [[12, 1, [
            [11, 2, squareMid],
            [11, 3, code],
        ]]]
        sqrd = self.generateDummyProtocol('checkJoinCode', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def createSquareChatAnnouncement(self,
                                     squareChatMid: str,
                                     messageId: str,
                                     text: str,
                                     senderSquareMemberMid: str,
                                     createdAt: int,
                                     announcementType: int = 0):
        """
        - SquareChatAnnouncementType:
            TEXT_MESSAGE(0);
        """
        params = [[
            12, 1,
            [[8, 1, self.getCurrReqId()], [11, 2, squareChatMid],
             [
                 12, 3,
                 [[8, 2, announcementType],
                  [
                      12, 3,
                      [[
                          12, 1,
                          [[11, 1, messageId], [11, 2, text],
                           [11, 3, senderSquareMemberMid], [10, 4, createdAt]]
                      ]]
                  ]]
             ]]
        ]]
        sqrd = self.generateDummyProtocol("createSquareChatAnnouncement",
                                          params, self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareAuthority", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def refreshSquareSubscriptions(self, subscriptions: list):
        params = [[12, 1, [
            [15, 2, [10, subscriptions]],
        ]]]
        sqrd = self.generateDummyProtocol('refreshSubscriptions', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getJoinedSquareChats(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getJoinedSquareChats is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getJoinedSquareChats", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def joinSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("joinSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("joinSquareChat", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def findSquareByEmid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSquareByEmid is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("findSquareByEmid", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareMemberRelation", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareMember(self, squareMemberMid: str):
        params = [[12, 1, [
            [11, 1, squareMemberMid],
        ]]]
        sqrd = self.generateDummyProtocol('getSquareMember', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION)

    def destroySquareMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessages is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("destroyMessages", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareCategories(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCategories is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getCategories", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def reportSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSquareMember", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareNoteStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNoteStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getNoteStatus", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def searchSquareChatMembers(self,
                                squareChatMid: str,
                                displayName: str = '',
                                continuationToken: str = None,
                                limit: int = 20):
        SearchSquareChatMembersRequest = [
            [11, 1, squareChatMid],
            [
                12,
                2,
                [
                    [11, 1, displayName],
                    # [2, 2, True]  # includingMe
                ]
            ],
            [8, 4, limit],
        ]
        if continuationToken is not None:
            SearchSquareChatMembersRequest.append([11, 3, continuationToken])
        params = [[12, 1, SearchSquareChatMembersRequest]]
        sqrd = self.generateDummyProtocol("searchSquareChatMembers", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION)

    def getSquareChatFeatureSet(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatFeatureSet is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSquareChatFeatureSet", params,
                                          self.SquareService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH, sqrd, self.SquareService_RES_TYPE)


class SquareServiceStruct(object):

    @staticmethod
    def BaseRequest(request: list):
        return [[12, 1, request]]

    @staticmethod
    def UnsendMessageRequest(squareChatMid: str, messageId: str):
        return __class__.BaseRequest([[11, 2, squareChatMid],
                                      [11, 3, messageId]])
