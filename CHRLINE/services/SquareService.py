# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, List
from .BaseService import BaseService, BaseServiceStruct

if TYPE_CHECKING:
    from CHRLINE import CHRLINE


class SquareService(BaseService):
    SquareService_REQ_TYPE = 4
    SquareService_RES_TYPE = 4
    SquareService_API_PATH = "/SQS1"

    SQUARE_EXCEPTION = {"code": 1, "message": 3, "metadata": 2}

    def __init__(self):
        self.SquareService_API_PATH = self.LINE_SQUARE_ENDPOINT

    def inviteIntoSquareChat(self, inviteeMids: list, squareChatMid: str):
        """Invite into square chat."""
        METHOD_NAME = "inviteIntoSquareChat"
        params = [[15, 1, [11, inviteeMids]], [11, 2, squareChatMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToSquare(self, squareMid: str, invitees: list, squareChatMid: str):
        """Invite to square."""
        METHOD_NAME = "inviteToSquare"
        params = [[11, 2, squareMid], [15, 3, [11, invitees]], [11, 4, squareChatMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinedSquares(self, continuationToken: str = None, limit: int = 50):
        """Get joined squares."""
        METHOD_NAME = "getJoinedSquares"
        params = [[11, 2, continuationToken], [8, 3, limit]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def markAsRead(self, squareChatMid: str, messageId: str):
        """Mark as read for square chat."""
        METHOD_NAME = "markAsRead"
        params = [[11, 2, squareChatMid], [11, 4, messageId]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reactToMessage(self, squareChatMid: str, messageId: str, reactionType: int = 2):
        """
        React to message for square chat message.

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
        METHOD_NAME = "reactToMessage"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, squareChatMid],
            [11, 3, messageId],
            [8, 4, reactionType],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def findSquareByInvitationTicket(self, invitationTicket: str):
        """Find square by invitation ticket."""
        METHOD_NAME = "findSquareByInvitationTicket"
        params = [[11, 2, invitationTicket]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def fetchMyEvents(
        self,
        subscriptionId: int = 0,
        syncToken: str = None,
        continuationToken: str = None,
        limit: int = 100,
    ):
        """Fetch square events."""
        METHOD_NAME = "fetchMyEvents"
        params = [
            [10, 1, subscriptionId],
            [11, 2, syncToken],
            [8, 3, limit],
            [11, 4, continuationToken],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def fetchSquareChatEvents(
        self,
        squareChatMid: str,
        syncToken: str = None,
        continuationToken: str = None,
        subscriptionId: int = 0,
        limit: int = 100,
    ):
        """Fetch square chat events."""
        METHOD_NAME = "fetchSquareChatEvents"
        fetchType = 1  # DEFAULT(1),PREFETCH_BY_SERVER(2),
        # PREFETCH_BY_CLIENT(3);
        params = [
            [10, 1, subscriptionId],
            [11, 2, squareChatMid],
            [11, 3, syncToken],
            [8, 4, limit],
            [8, 5, 1],  # direction
            [8, 6, 1],  # inclusive
            [11, 7, continuationToken],
            [8, 8, fetchType],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def sendSquareMessage(
        self,
        squareChatMid: str,
        text: str,
        contentType: int = 0,
        contentMetadata: dict = {},
        relatedMessageId: str = None,
    ):
        """Send message for square chat (OLD)."""
        METHOD_NAME = "sendMessage"
        message = [
            # [11, 1, _from],
            [11, 2, squareChatMid],
            [11, 10, text],
            [8, 15, contentType],  # contentType
            [13, 18, [11, 11, contentMetadata]],
        ]
        if relatedMessageId is not None:
            message.append([11, 21, relatedMessageId])
            message.append(
                [
                    8,
                    22,
                    3,
                ]
            )
            message.append([8, 24, 2])
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, squareChatMid],
            [
                12,
                3,
                [
                    [12, 1, message],
                    [8, 3, 4],
                ],
            ],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def sendSquareTextMessage(
        self,
        squareChatMid: str,
        text: str,
        contentMetadata: dict = {},
        relatedMessageId: str = None,
    ):
        return self.sendSquareMessage(
            squareChatMid, text, 0, contentMetadata, relatedMessageId
        )

    def getSquare(self, squareMid: str):
        """Get square."""
        METHOD_NAME = "getSquare"
        params = [[11, 2, squareMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinableSquareChats(
        self, squareMid: str, continuationToken: str = None, limit: int = 100
    ):
        """Get joinable square chats."""
        METHOD_NAME = "getJoinableSquareChats"
        params = [[11, 1, squareMid], [11, 10, continuationToken], [8, 11, limit]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def createSquare(
        self,
        name: str,
        displayName: str,
        profileImageObsHash: str = "0h6tJf0hQsaVt3H0eLAsAWDFheczgHd3wTCTx2eApNKSoefHNVGRdwfgxbdgUMLi8MSngnPFMeNmpbLi8MSngnPFMeNmpbLi8MSngnOA",
        desc: str = "test with CHRLINE API",
        searchable: bool = True,
        SquareJoinMethodType: int = 0,
    ):
        """
        Create square.

        - SquareJoinMethodType
            NONE(0),
            APPROVAL(1),
            CODE(2);
        """
        METHOD_NAME = "createSquare"
        params = [
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
                    [15, 16, [11, []]],  # svcTags
                ],
            ],
            [
                12,
                3,
                [
                    [11, 3, displayName],
                    # [11, 4, profileImageObsHash],
                    [2, 5, True],  # ableToReceiveMessage
                    [10, 9, 0],  # revision
                ],
            ],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatAnnouncements(self, squareMid: str):
        """Get square chat announcements."""
        METHOD_NAME = "getSquareChatAnnouncements"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def leaveSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChatMember", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def searchSquares(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquares is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchSquares", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareFeatureSet(self, updateAttributes: List[int], squareMid: str, revision: int, creatingSecretSquareChat: int = 0):
        """
        Update square feature set.

        - updateAttributes:
            CREATING_SECRET_SQUARE_CHAT(1),
            INVITING_INTO_OPEN_SQUARE_CHAT(2),
            CREATING_SQUARE_CHAT(3),
            READONLY_DEFAULT_CHAT(4),
            SHOWING_ADVERTISEMENT(5),
            DELEGATE_JOIN_TO_PLUG(6),
            DELEGATE_KICK_OUT_TO_PLUG(7),
            DISABLE_UPDATE_JOIN_METHOD(8),
            DISABLE_TRANSFER_ADMIN(9),
            CREATING_LIVE_TALK(10);
        """
        METHOD_NAME = "updateSquareFeatureSet"
        SquareFeatureSet = [
            [11, 1, squareMid],
            [10, 2, revision],
        ]
        if creatingSecretSquareChat != 0:
            SquareFeatureSet.append([12, 11, [
                [8, 1, 1],
                [8, 2, creatingSecretSquareChat]
            ]])
        params = [
            [14, 2, [8, updateAttributes]],
            [12, 3, SquareFeatureSet]
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinSquare(
        self,
        squareMid,
        displayName,
        ableToReceiveMessage: bool = False,
        passCode: str = None,
    ):
        params = [
            [
                12,
                1,
                [
                    [11, 2, squareMid],
                    [
                        12,
                        3,
                        [
                            [11, 2, squareMid],
                            [11, 3, displayName],
                            [2, 5, ableToReceiveMessage],
                            [10, 9, 0],
                        ],
                    ],
                    [12, 5, [[12, 2, [[11, 1, passCode]]]]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("joinSquare", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquarePopularKeywords(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularKeywords is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularKeywords", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def reportSquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareMessage", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMemberRelation", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def leaveSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveSquare", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMemberRelations(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelations is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMemberRelations", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def removeSquareSubscriptions(self, subscriptionIds: list = []):
        params = [
            [
                12,
                1,
                [
                    [15, 2, [10, subscriptionIds]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("removeSubscriptions", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMessageReactions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getMessageReactions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getMessageReactions", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def destroySquareMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "destroyMessage", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def reportSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def unsendSquareMessage(self, squareChatMid: str, messageId: str):
        """
        Unsend message for square.

        2022/09/19: Added.
        """
        METHOD_NAME = "unsendMessage"
        params = SquareServiceStruct.UnsendMessageRequest(squareChatMid, messageId)
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"{__class__.__name__}.{METHOD_NAME}",
        )

    def deleteSquareChatAnnouncement(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChatAnnouncement is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquareChatAnnouncement", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def createSquareChat(
        self,
        squareChatMid: str,
        name: str,
        chatImageObsHash: str,
        squareChatType: int = 1,
        maxMemberCount: int = 5000,
        ableToSearchMessage: int = 1,
        squareMemberMids: list = [],
    ):
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
        params = [
            [
                12,
                1,
                [
                    [8, 1, self.getCurrReqId()],
                    [
                        12,
                        2,
                        [
                            [11, 1, squareChatMid],
                            [8, 3, squareChatType],
                            [11, 4, name],
                            [11, 5, chatImageObsHash],
                            [8, 7, maxMemberCount],
                            [8, 11, ableToSearchMessage],
                        ],
                    ],
                    [15, 3, [11, squareMemberMids]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol(
            "createSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def deleteSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatMembers(
        self, squareChatMid: str, continuationToken: str = None, limit: int = 200
    ):
        GetSquareChatMembersRequest = [[11, 1, squareChatMid], [8, 3, limit]]
        if continuationToken is not None:
            GetSquareChatMembersRequest.append([11, 2, continuationToken])
        params = [[12, 1, GetSquareChatMembersRequest]]
        sqrd = self.generateDummyProtocol(
            "getSquareChatMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareFeatureSet(self, squareMid: str):
        """Get square feature set."""
        METHOD_NAME = "getSquareFeatureSet"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareAuthority", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def rejectSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "rejectSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def deleteSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteSquare", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def reportSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquare", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareInvitationTicketUrl(self, mid: str):
        params = [
            [
                12,
                1,
                [
                    [11, 2, mid],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("getInvitationTicketUrl", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareChatMember(
        self,
        squareMemberMid: str,
        squareChatMid: str,
        notificationForMessage: bool = True,
        notificationForNewMember: bool = True,
        updatedAttrs: list = [6],
    ):
        """
        - SquareChatMemberAttribute:
            MEMBERSHIP_STATE(4),
            NOTIFICATION_MESSAGE(6),
            NOTIFICATION_NEW_MEMBER(7);
        """
        params = [
            [
                12,
                1,
                [
                    [14, 2, [8, updatedAttrs]],
                    [
                        12,
                        3,
                        [
                            [11, 1, squareMemberMid],
                            [11, 2, squareChatMid],
                            [2, 5, notificationForMessage],
                            [2, 6, notificationForNewMember],
                        ],
                    ],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("updateSquareChatMember", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareMember(
        self,
        updatedAttrs: list,
        updatedPreferenceAttrs: list,
        squareMemberMid: str,
        squareMid: str,
        revision: int,
        displayName: str = None,
        membershipState: int = None,
        role: int = None,
    ):
        """
        Update square member.

        SquareMemberAttribute:
            DISPLAY_NAME(1),
            PROFILE_IMAGE(2),
            ABLE_TO_RECEIVE_MESSAGE(3),
            MEMBERSHIP_STATE(5),
            ROLE(6),
            PREFERENCE(7);
        SquareMembershipState:
            JOIN_REQUESTED(1),
            JOINED(2),
            REJECTED(3),
            LEFT(4),
            KICK_OUT(5),
            BANNED(6),
            DELETED(7);
        """
        METHOD_NAME = "updateSquareMember"
        squareMember = [[11, 1, squareMemberMid], [11, 2, squareMid]]
        if 1 in updatedAttrs:
            if displayName is None:
                raise ValueError("displayName is None")
            squareMember.append([11, 3, displayName])
        if 5 in updatedAttrs:
            if membershipState is None:
                raise ValueError("membershipState is None")
            squareMember.append([8, 7, membershipState])
        if 6 in updatedAttrs:
            if role is None:
                raise ValueError("role is None")
            squareMember.append([8, 8, role])
        squareMember.append([10, 9, revision])
        params = [
            [14, 2, [8, updatedAttrs]],
            [14, 3, [8, updatedPreferenceAttrs]],
            [12, 4, squareMember],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    # https://discord.com/channels/466066749440393216/1076212330620256296
    def deleteOtherFromSquare(self, sid: str, pid: str):
        """Kick out member for square."""
        UPDATE_PREF_ATTRS = []
        UPDATE_ATTRS = [5]
        MEMBERSHIP_STATE = 5
        getSquareMemberResp = self.getSquareMember(pid)
        squareMember = self.checkAndGetValue(getSquareMemberResp, "squareMember", 1)
        squareMemberRevision = self.checkAndGetValue(squareMember, "revision", 9)
        revision = squareMemberRevision
        self.updateSquareMember(
            UPDATE_ATTRS,
            UPDATE_PREF_ATTRS,
            pid,
            sid,
            revision,
            membershipState=MEMBERSHIP_STATE,
        )

    def updateSquare(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquare is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquare", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareAuthorities(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthorities is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareAuthorities", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def updateSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChatStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChatStatus", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def approveSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("approveSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "approveSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareStatus", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def searchSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def checkSquareJoinCode(self, squareMid: str, code: str):
        params = [
            [
                12,
                1,
                [
                    [11, 2, squareMid],
                    [11, 3, code],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("checkJoinCode", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def createSquareChatAnnouncement(
        self,
        squareChatMid: str,
        messageId: str,
        text: str,
        senderSquareMemberMid: str,
        createdAt: int,
        announcementType: int = 0,
    ):
        """
        - SquareChatAnnouncementType:
            TEXT_MESSAGE(0);
        """
        params = [
            [
                12,
                1,
                [
                    [8, 1, self.getCurrReqId()],
                    [11, 2, squareChatMid],
                    [
                        12,
                        3,
                        [
                            [8, 2, announcementType],
                            [
                                12,
                                3,
                                [
                                    [
                                        12,
                                        1,
                                        [
                                            [11, 1, messageId],
                                            [11, 2, text],
                                            [11, 3, senderSquareMemberMid],
                                            [10, 4, createdAt],
                                        ],
                                    ]
                                ],
                            ],
                        ],
                    ],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol(
            "createSquareChatAnnouncement", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareAuthority(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareAuthority is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareAuthority", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def refreshSquareSubscriptions(self, subscriptions: list):
        params = [
            [
                12,
                1,
                [
                    [15, 2, [10, subscriptions]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("refreshSubscriptions", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getJoinedSquareChats(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getJoinedSquareChats is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getJoinedSquareChats", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def joinSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("joinSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "joinSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def findSquareByEmid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSquareByEmid is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findSquareByEmid", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMemberRelation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSquareMemberRelation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSquareMemberRelation", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMember(self, squareMemberMid: str):
        params = [
            [
                12,
                1,
                [
                    [11, 2, squareMemberMid],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("getSquareMember", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def destroySquareMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("destroyMessages is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "destroyMessages", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareCategories(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCategories is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCategories", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def reportSquareMember(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSquareMember is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSquareMember", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareNoteStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNoteStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNoteStatus", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def searchSquareChatMembers(
        self,
        squareChatMid: str,
        displayName: str = "",
        continuationToken: str = None,
        limit: int = 20,
    ):
        SearchSquareChatMembersRequest = [
            [11, 1, squareChatMid],
            [
                12,
                2,
                [
                    [11, 1, displayName],
                    # [2, 2, True]  # includingMe
                ],
            ],
            [8, 4, limit],
        ]
        if continuationToken is not None:
            SearchSquareChatMembersRequest.append([11, 3, continuationToken])
        params = [[12, 1, SearchSquareChatMembersRequest]]
        sqrd = self.generateDummyProtocol(
            "searchSquareChatMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatFeatureSet(self, squareChatMid: str):
        """Get square chat feature set."""
        METHOD_NAME = "getSquareChatFeatureSet"
        params = [
            [11, 2, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareEmid(self, squareMid: str):
        """
        Get square eMid.

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "getSquareEmid"
        params = [[11, 1, squareMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMembersBySquare(self, squareMid: str, squareMemberMids: list):
        """
        Get square members by square.

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "getSquareMembersBySquare"
        params = [
            [11, 2, squareMid],
            [14, 3, [11, squareMemberMids]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def manualRepair(self, syncToken: str, limit: int, continuationToken: str):
        """
        Manual repair.

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "manualRepair"
        params = [
            [11, 1, syncToken],
            [8, 2, limit],
            [11, 3, continuationToken],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)


class SquareServiceStruct(BaseServiceStruct):
    @staticmethod
    def UnsendMessageRequest(squareChatMid: str, messageId: str):
        return __class__.BaseRequest([[11, 2, squareChatMid], [11, 3, messageId]])

    @staticmethod
    def SendRequestByName(client: "CHRLINE", name: str, request: str):
        payload = __class__.BaseRequest(request)
        sqrd = client.generateDummyProtocol(
            name, payload, client.SquareService_REQ_TYPE
        )
        return client.postPackDataAndGetUnpackRespData(
            client.SquareService_API_PATH,
            sqrd,
            client.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"SquareService.{name}",
        )
