# -*- coding: utf-8 -*-
from typing import List
from typing import TYPE_CHECKING

from .BaseService import BaseService, BaseServiceStruct
from .SquareService import SquareService

if TYPE_CHECKING:
    from CHRLINE import CHRLINE


class SquareLiveTalkService(BaseService):
    SquareLiveTalkService_REQ_TYPE = 4  # BASE_VAL
    SquareLiveTalkService_RES_TYPE = 4  # BASE_VAL
    SquareLiveTalkService_API_PATH = None  # BASE_VAL

    def __init__(self):
        self.SquareLiveTalkService_API_PATH = "/SQLV1"

    def acceptSpeakers(self, squareChatMid: str, sessionId: str, targetMids: List[str]):
        """Accept speakers."""
        METHOD_NAME = "acceptSpeakers"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [14, 3, [11, targetMids]]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def acceptToChangeRole(
        self, squareChatMid: str, sessionId: str, inviteRequestId: str
    ):
        """Accept to change role."""
        METHOD_NAME = "acceptToChangeRole"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def acceptToListen(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Accept to listen."""
        METHOD_NAME = "acceptToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def acceptToSpeak(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Accept to speak."""
        METHOD_NAME = "acceptToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def cancelToSpeak(self, squareChatMid: str, sessionId: str):
        """Cancel to speak."""
        METHOD_NAME = "cancelToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def endLiveTalk(self, squareChatMid: str, sessionId: str):
        """End live talk."""
        METHOD_NAME = "endLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def fetchLiveTalkEvents(
        self, squareChatMid: str, sessionId: str, syncToken: str, limit: int = 50
    ):
        """Fetch live talk events."""
        METHOD_NAME = "fetchLiveTalkEvents"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, syncToken],
            [8, 4, limit],
        ]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def findLiveTalkByInvitationTicket(self, invitationTicket: str):
        """Find live talk by invitation ticket."""
        METHOD_NAME = "findLiveTalkByInvitationTicket"
        params = [[11, 1, invitationTicket]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def forceEndLiveTalk(self, squareChatMid: str, sessionId: str):
        """Force end live talk."""
        METHOD_NAME = "forceEndLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getLiveTalkInfoForNonMember(
        self, squareChatMid: str, sessionId: str, speakers: List[str]
    ):
        """Get live talk info for non-member."""
        METHOD_NAME = "getLiveTalkInfoForNonMember"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, speakers]]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getLiveTalkInvitationUrl(self, squareChatMid: str, sessionId: str):
        """Get live talk invitation url."""
        METHOD_NAME = "getLiveTalkInvitationUrl"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getLiveTalkSpeakersForNonMember(
        self, squareChatMid: str, sessionId: str, speakers: List[str]
    ):
        """Get live talk speakers for non-member."""
        METHOD_NAME = "getLiveTalkSpeakersForNonMember"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, speakers]]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareInfoByChatMid(self, squareChatMid: str):
        """Get square info by chat mid."""
        METHOD_NAME = "getSquareInfoByChatMid"
        params = [[11, 1, squareChatMid]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToChangeRole(
        self, squareChatMid: str, sessionId: str, targetMid: str, targetRole: int
    ):
        """
        Invite to change role.

        - targetRole:
            HOST(1),
            CO_HOST(2),
            GUEST(3);
        """
        METHOD_NAME = "inviteToChangeRole"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, targetMid],
            [8, 4, targetRole],
        ]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToListen(self, squareChatMid: str, sessionId: str, targetMid: str):
        """Invite to listen."""
        METHOD_NAME = "inviteToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, targetMid]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToLiveTalk(self, squareChatMid: str, sessionId: str, invitees: List[str]):
        """Invite to live talk."""
        METHOD_NAME = "inviteToLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, invitees]]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToSpeak(self, squareChatMid: str, sessionId: str, targetMid: str):
        """Invite to speak."""
        METHOD_NAME = "inviteToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, targetMid]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinLiveTalk(self, squareChatMid: str, sessionId: str, wantToSpeak: bool):
        """Join live talk."""
        METHOD_NAME = "joinLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [2, 3, wantToSpeak]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def kickOutLiveTalkParticipants(
        self, squareChatMid: str, sessionId: str, mid: str = None
    ):
        """Kick out live talk participants."""
        METHOD_NAME = "kickOutLiveTalkParticipants"
        target = []
        if mid is not None:
            liveTalkParticipant = [[11, 1, mid]]
            target.append([12, 1, liveTalkParticipant])
        else:
            target.append([12, 2, []])
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [12, 3, target]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def rejectSpeakers(self, squareChatMid: str, sessionId: str, targetMids: List[str]):
        """Reject speakers."""
        METHOD_NAME = "rejectSpeakers"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [14, 3, [11, targetMids]]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def rejectToSpeak(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Reject to speak."""
        METHOD_NAME = "rejectToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportLiveTalk(self, squareChatMid: str, sessionId: str, reportType: int):
        """
        Report live talk.

        - reportType:
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3),
            IRRELEVANT_CONTENT(4),
            OTHER(5);
        """
        METHOD_NAME = "reportLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [8, 3, reportType]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportLiveTalkSpeaker(
        self, squareChatMid: str, sessionId: str, speakerMemberMid: str, reportType: int
    ):
        """
        Report live talk speaks.

        - reportType:
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3),
            IRRELEVANT_CONTENT(4),
            OTHER(5);
        """
        METHOD_NAME = "reportLiveTalkSpeaker"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, speakerMemberMid],
            [8, 4, reportType],
        ]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def requestToListen(self, squareChatMid: str, sessionId: str):
        """Request to listen."""
        METHOD_NAME = "requestToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def requestToSpeak(self, squareChatMid: str, sessionId: str):
        """Request to speak."""
        METHOD_NAME = "requestToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def startLiveTalk(
        self, squareChatMid: str, title: str, _type: int = 1, speakerSetting: int = 2
    ):
        """
        Start live talk.

        - type:
            PUBLIC(1),
            PRIVATE(2);
        - speakerSetting:
            LIMITED_SPEAKERS(1),
            ALL_AS_SPEAKERS(2);
        """
        METHOD_NAME = "startLiveTalk"
        params = [
            [11, 1, squareChatMid],
            [11, 2, title],
            [8, 3, _type],
            [8, 4, speakerSetting],
        ]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateLiveTalkAttrs(
        self,
        squareChatMid: str,
        sessionId: str,
        updatedAttrs: List[int],
        title: str = None,
        speakerSetting: int = None,
        allowRequestToSpeak: bool = None,
    ):
        """
        Update live talk attrs.

        - updatedAttrs:
            TITLE(1),
            SPEAKER_SETTING(2),
            ALLOW_REQUEST_TO_SPEAK(3);
        """
        METHOD_NAME = "updateLiveTalkAttrs"
        liveTalk = [[11, 1, squareChatMid], [11, 2, sessionId]]
        if title is not None:
            liveTalk.append([11, 3, title])
        if speakerSetting is not None:
            liveTalk.append([8, 5, speakerSetting])
        if allowRequestToSpeak is not None:
            liveTalk.append([2, 6, allowRequestToSpeak])
        params = [[14, 1, [8, updatedAttrs]], [12, 2, liveTalk]]
        return SquareLiveTalkServiceStruct.SendRequestByName(self, METHOD_NAME, params)


class SquareLiveTalkServiceStruct(BaseServiceStruct):
    @staticmethod
    def SendRequestByName(client: "CHRLINE", name: str, request: str):
        payload = __class__.BaseRequest(request)
        sqrd = client.generateDummyProtocol(
            name, payload, client.SquareLiveTalkService_REQ_TYPE
        )
        return client.postPackDataAndGetUnpackRespData(
            client.SquareLiveTalkService_API_PATH,
            sqrd,
            client.SquareLiveTalkService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"SquareLiveTalkService.{name}",
        )
