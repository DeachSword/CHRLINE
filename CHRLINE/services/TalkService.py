# -*- coding: utf-8 -*-
import time

import httpx
import requests


class TalkService():
    url = "https://ga2.line.naver.jp/enc"
    TalkService_REQ_TYPE = 4
    TalkService_RES_TYPE = 5
    TalkService_API_PATH = "/S5"

    def __init__(self):
        self.testPollConn = requests.session()

    def sendMessage(self, to: str, text: str, contentType: int=0, contentMetadata: dict={}, relatedMessageId: str=None, location: dict=None, chunk: list=None):
        message = [
            [11, 2, to],
            [10, 5, 0],  # createdTime
            [10, 6, 0],  # deliveredTime
            [2, 14, False],  # hasContent
            [8, 15, contentType],
            [13, 18, [11, 11, contentMetadata]],
            [3, 19, 0],  # sessionId
        ]
        if text is not None:
            message.append(
                [11, 10, text]
            )
        if location is not None:
            locationObj = [
                [11, 1, location.get(1, 'CHRLINE API')],
                [11, 2, location.get(2, 'https://github.com/DeachSword/CHRLINE')],
                [4, 3, location.get(3, 0)],
                [4, 4, location.get(4, 0)],
                [11, 6, location.get(6, 'PC0')],
                [8, 7, location.get(7, 2)],
            ]
            message.append(
                [12, 11, locationObj]
            )
        if chunk is not None:
            message.append(
                [15, 20, [11, chunk]]
            )
        if relatedMessageId is not None:
            message.append(
                [11, 21, relatedMessageId]
            )
            message.append(
                [8, 22, 3] # messageRelationType; FORWARD(0), AUTO_REPLY(1), SUBORDINATE(2), REPLY(3);

            )
            message.append(
                [8, 24, 1] # relatedMessageServiceCode; 1 for Talk 2 for Square
            )
        params = [
            [8, 1, self.getCurrReqId()],
            [12, 2, message]
        ]
        sqrd = self.generateDummyProtocol('sendMessage', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def replyMessage(self, msgData: dict, text: str, contentType: int = 0, contentMetadata: dict = {}):
        to = msgData[2]
        toType = msgData[3]
        relatedMessageId = msgData[4]
        if toType == 0 and msgData.get('opType', 26) == 26:  # opType for hooks
            to = msgData[1]
        if msgData.get('isE2EE') == True:
            return self.sendMessageWithE2EE(to, text, contentType, contentMetadata, relatedMessageId)
        return self.sendMessage(to, text, contentType, contentMetadata, relatedMessageId)

    def sendContact(self, to, mid):
        return self.sendMessage(to, None, contentType=13, contentMetadata={"mid": mid})

    def sendLocation(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, None, contentType=15, location=data)

    def sendLocationMessage(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, "test", location=data)

    def sendMessageWithE2EE(self, to, text, contentType=0, contentMetadata={}, relatedMessageId=None):
        chunk = self.encryptE2EEMessage(to, text)
        contentMetadata = self.server.additionalHeaders(contentMetadata, {
            'e2eeVersion': '2',
            'contentType': '0',
            'e2eeMark': '2'
        })
        return self.sendMessageWithChunks(to, chunk, contentType, contentMetadata, relatedMessageId)

    def sendMessageWithChunks(self, to, chunk, contentType=0, contentMetadata={}, relatedMessageId=None):
        return self.sendMessage(to, None,contentType, contentMetadata, relatedMessageId, chunk=chunk)

    def sendCompactMessage(self, to: str, text: str, chunks: list = []):
        cType = -1  # 2 = TEXT, 4 = STICKER, 5 = E2EE_TEXT, 6 = E2EE_LOCATION
        ep = self.LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT
        if text is not None:
            cType = 2
        elif chunks:
            cType = 5
            ep = self.LINE_COMPACT_E2EE_MESSAGE_ENDPOINT
        sqrd = [cType]
        midType = to[0]
        if midType == 'u':
            sqrd.append(0)
        elif midType == 'r':
            sqrd.append(1)
        elif midType == 'c':
            sqrd.append(2)
        else:
            raise Exception(f"unknown midType: {midType}")
        _reqId = self.getCurrReqId()
        self.log(f"[sendCompactMessage] REQ_ID: {_reqId}", True)
        sqrd += self.getIntBytes(_reqId, isCompact=True)
        sqrd += self.getMagicStringBytes(to[1:])
        if cType == 2:
            sqrd += self.getStringBytes(text, isCompact=True)
            sqrd.append(2)
        elif cType == 5:
            sqrd += [2]
            for _ck in chunks[:3]:
                sqrd += self.getStringBytes(_ck, isCompact=True)
            for _ck in chunks[3:5]:
                sqrd += list(_ck)
        hr = self.server.additionalHeaders(self.server.Headers, {
            'x-lai': str(_reqId)
        })
        return self.postPackDataAndGetUnpackRespData(ep, sqrd, -7, headers=hr)

    def sendCompactE2EEMessage(self, to, text):
        chunks = self.encryptE2EEMessage(to, text, isCompact=True)
        return self.sendCompactMessage(to, None, chunks)

    def getEncryptedIdentity(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 69, 110, 99, 114, 121,
                112, 116, 101, 100, 73, 100, 101, 110, 116, 105, 116, 121, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getProfile(self):
        params = []
        sqrd = self.generateDummyProtocol('getProfile', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getSettings(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 83,
                101, 116, 116, 105, 110, 103, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def sendChatChecked(self, chatMid, lastMessageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 115, 101, 110, 100, 67,
                104, 97, 116, 67, 104, 101, 99, 107, 101, 100, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in chatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(lastMessageId)]
        for value in lastMessageId:
            sqrd.append(ord(value))
        # [3, 0, 4] # sessionId
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def unsendMessage(self, messageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 117, 110, 115, 101,
                110, 100, 77, 101, 115, 115, 97, 103, 101, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getContact(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 67, 111,
                110, 116, 97, 99, 116, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getContacts(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 67, 111, 110, 116,
                97, 99, 116, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getContactsV2(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 67,
                111, 110, 116, 97, 99, 116, 115, 86, 50, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def findAndAddContactsByMid(self, mid, reference='{"screen":"groupMemberList","spec":"native"}'):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 23, 102, 105, 110, 100, 65, 110, 100, 65, 100,
                100, 67, 111, 110, 116, 97, 99, 116, 115, 66, 121, 77, 105, 100, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        sqrd += [11, 0, 4] + self.getStringBytes(reference)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getGroup(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 71, 114,
                111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getGroups(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 9, 103, 101, 116, 71, 114, 111,
                117, 112, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getGroupsV2(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 71, 114, 111, 117,
                112, 115, 86, 50, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getChats(self, mids, withMembers=True, withInvitees=True):
        if type(mids) != list:
            raise Exception("[getChats] mids must be a list")
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101,
                116, 67, 104, 97, 116, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [2, 0, 2, int(withMembers)]
        sqrd += [2, 0, 3, int(withMembers)]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getAllChatMids(self, withMembers=True, withInvitees=True):
        params = [
            [12, 1, [
                [2, 1, withMembers],
                [2, 2, withInvitees]
            ]],
            [8, 2, 7]
        ]
        sqrd = self.generateDummyProtocol('getAllChatMids', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getCompactGroup(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 67, 111, 109, 112, 97,
                99, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def deleteOtherFromChat(self, to, mid):
        if type(mid) == list:
            _lastReq = None
            for _mid in mid:
                print(f'[deleteOtherFromChat] The parameter \'mid\' should be str')
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 100, 101, 108, 101, 116, 101, 79,
                116, 104, 101, 114, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]  # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def inviteIntoChat(self, to, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 105, 110, 118, 105, 116,
                101, 73, 110, 116, 111, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def cancelChatInvitation(self, to, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 99, 97, 110, 99, 101, 108, 67, 104,
                97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]  # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def deleteSelfFromChat(self, to):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 100, 101, 108, 101, 116, 101, 83,
                101, 108, 102, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        # sqrd += [10, 0, 3] # lastSeenMessageDeliveredTime
        # sqrd += [11, 0, 4] # lastSeenMessageId
        # sqrd += [10, 0, 5] # lastMessageDeliveredTime
        # sqrd += [11, 0, 6] # lastMessageId
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def acceptChatInvitation(self, to):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 97, 99, 99, 101, 112, 116, 67, 104,
                97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(self.getCurrReqId())
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        _d = self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT, sqrd)
        #self.sendMessage(to, 'Powered by CHRLINE API')
        return _d

    def reissueChatTicket(self, groupMid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("reissueChatTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(groupMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def findChatByTicket(self, ticketId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 102, 105, 110, 100, 67, 104,
                97, 116, 66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 1] + self.getStringBytes(ticketId)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def acceptChatInvitationByTicket(self, to, ticket):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 28, 97, 99, 99, 101, 112, 116, 67, 104, 97, 116, 73, 110,
                118, 105, 116, 97, 116, 105, 111, 110, 66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(ticket)]
        for value in ticket:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        _d = self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT, sqrd)
        self.sendMessage(to, 'Powered by CHRLINE API')
        return _d

    def updateChat(self, chatMid, chatSet, updatedAttribute=1):
        """
        updatedAttribute:
            NAME(1),
            PICTURE_STATUS(2),
            PREVENTED_JOIN_BY_TICKET(4),
            NOTIFICATION_SETTING(8),
            INVITATION_TICKET(16),
            FAVORITE_TIMESTAMP(32),
            CHAT_TYPE(64);
        TODO:
            using dict to update?
        """
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 117, 112, 100,
                97, 116, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        if chatSet.get(1) is not None:
            sqrd += [8, 0, 1] + self.getIntBytes(chatSet[1])
        else:
            sqrd += [8, 0, 1, 0, 0, 0, 1]  # type
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        if chatSet.get(4) is not None:
            sqrd += [2, 0, 4, int(chatSet[4])]
        if chatSet.get(6) is not None:
            sqrd += [11, 0, 6] + self.getStringBytes(chatSet[6])
        if chatSet.get(8) is not None:
            extra = chatSet[8]
            sqrd += [12, 0, 8]
            sqrd += [12, 0, 1]
            if extra.get(2) is not None:
                sqrd += [2, 0, 2, int(extra[2])]
            if extra.get(6) is not None:
                sqrd += [2, 0, 6, int(extra[6])]
            if extra.get(7) is not None:
                sqrd += [2, 0, 7, int(extra[7])]
            sqrd += [0, 0]
        sqrd += [0]
        sqrd += [8, 0, 3] + self.getIntBytes(updatedAttribute)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def updateChatName(self, chatMid, name):
        return self.updateChat(chatMid, {6: name}, 1)

    def updateChatPreventedUrl(self, chatMid, bool):
        return self.updateChat(chatMid, {8: {2: bool}}, 4)

    def getGroupIdsJoined(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 71, 114, 111, 117,
                112, 73, 100, 115, 74, 111, 105, 110, 101, 100, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getGroupIdsInvited(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 103, 101, 116, 71, 114, 111, 117,
                112, 73, 100, 115, 73, 110, 118, 105, 116, 101, 100, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getAllContactIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 65, 108, 108,
                67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getBlockedContactIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 66, 108, 111, 99, 107,
                101, 100, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getBlockedRecommendationIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 27, 103, 101, 116, 66, 108, 111, 99, 107, 101, 100, 82, 101,
                99, 111, 109, 109, 101, 110, 100, 97, 116, 105, 111, 110, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getAllReadMessageOps(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116,
                79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def sendPostback(self, messageId, url, chatMID, originMID):
        """
        :url: linepostback://postback?_data=
        """
        params = [
            [12, 2, [
                [11, 1, messageId],
                [11, 2, url],
                [11, 3, chatMID],
                [11, 4, originMID]
            ]],
        ]
        sqrd = self.generateDummyProtocol('sendPostback', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getPreviousMessagesV2WithRequest(self, messageBoxId, endMessageId=0, messagesCount=200, withReadCount=0, receivedOnly=False):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 32, 103, 101, 116, 80, 114, 101, 118, 105, 111, 117, 115, 77, 101, 115,
                115, 97, 103, 101, 115, 86, 50, 87, 105, 116, 104, 82, 101, 113, 117, 101, 115, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1, 0, 0, 0, len(messageBoxId)]
        for value in messageBoxId:
            sqrd.append(ord(value))
        sqrd += [12, 0, 2]
        sqrd += [10, 0, 1] + \
            self.getIntBytes(1611064540822, 8)  # 時間... fk u time
        sqrd += [10, 0, 2] + self.getIntBytes(int(endMessageId), 8) + [0]
        sqrd += [8, 0, 3] + self.getIntBytes(messagesCount)
        sqrd += [2, 0, 4, 1]
        sqrd += [2, 0, 5, 0]
        sqrd += [0]
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getMessageBoxes(self, minChatId=0, maxChatId=0, activeOnly=0, messageBoxCountLimit=0, withUnreadCount=False, lastMessagesPerMessageBoxCount=False, unreadOnly=False):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 77, 101,
                115, 115, 97, 103, 101, 66, 111, 120, 101, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1, 0, 0, 0, len(minChatId)]
        for value in minChatId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(maxChatId)]
        for value in maxChatId:
            sqrd.append(ord(value))
        sqrd += [2, 0, 3, 0]  # activeOnly
        sqrd += [8, 0, 4, 0, 0, 0, 200]  # messageBoxCountLimit
        sqrd += [2, 0, 5, 0]  # withUnreadCount
        sqrd += [8, 0, 6, 0, 0, 0, 200]  # lastMessagesPerMessageBoxCount
        sqrd += [2, 0, 7]  # unreadOnly
        sqrd += [0, 0]
        sqrd += [8, 0, 3, 0, 0, 0, 7]
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        params = [
            [15, 2, [11, chatRoomMids]],
            [8, 3, 0]
        ]
        sqrd = self.generateDummyProtocol(
            'getChatRoomAnnouncementsBulk', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getChatRoomAnnouncements(self, chatRoomMid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getChatRoomAnnouncements') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 26, 114, 101, 109, 111, 118, 101, 67, 104, 97, 116, 82,
                111, 111, 109, 65, 110, 110, 111, 117, 110, 99, 101, 109, 101, 110, 116, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, len(chatRoomMid)]
        for value in chatRoomMid:
            sqrd.append(ord(value))
        sqrd += [10, 0, 3] + self.getIntBytes(int(announcementSeq), 8)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def createChatRoomAnnouncement(self, chatRoomMid, text, link='', thumbnail='', type=0, displayFields=5, contentMetadata=None):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('createChatRoomAnnouncement') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [8, 0, 3] + self.getIntBytes(type)
        sqrd += [12, 0, 4]
        sqrd += [8, 0, 1] + self.getIntBytes(displayFields)
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [11, 0, 3] + self.getStringBytes(link)
        sqrd += [11, 0, 4] + self.getStringBytes(thumbnail)
        # sqrd += [12, 0, 5] #contentMetadata
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def leaveRoom(self, roomIds):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('leaveRoom') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(roomIds)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getRoomsV2(self, roomIds):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getRoomsV2') + [0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(roomIds)]
        for mid in roomIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def createRoomV2(self, contactIds):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('createRoomV2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(contactIds)]
        for mid in contactIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getCountries(self, countryGroup=1):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getCountries') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(countryGroup)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def acquireEncryptedAccessToken(self, featureType=2):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('acquireEncryptedAccessToken') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(featureType)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def blockContact(self, mid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('blockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def unblockContact(self, mid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('unblockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getLastOpRevision(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116,
                79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getServerTime(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 83, 101,
                114, 118, 101, 114, 84, 105, 109, 101, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getConfigurations(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 67, 111, 110, 102,
                105, 103, 117, 114, 97, 116, 105, 111, 110, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def fetchOps(self, revision, count=100):
        params = [
            [10, 2, revision],
            [8, 3, count],
            [10, 4, self.globalRev],
            [10, 5, self.individualRev]
        ]
        sqrd = self.generateDummyProtocol('fetchOps', params, 4)
        hr = self.server.additionalHeaders(self.server.Headers, {
            # "x-lst": "110000",
            "x-las": "F",  # or "B" if background
            "x-lam": "w",  # or "m"
            "x-lac": "46692"  # carrier
        })
        try:
            data = self.postPackDataAndGetUnpackRespData(
                "/P5", sqrd, 5, encType=0, headers=hr)
            if data is None:
                return []
            if 'error' not in data:
                for op in data:
                    if op[3] == 0:
                        if 10 in op:
                            a = op[10].split('\x1e')
                            self.individualRev = a[0]
                            self.log(f"individualRev: {self.individualRev}")
                        if 11 in op:
                            b = op[11].split('\x1e')
                            self.globalRev = b[0]
                            self.log(f"globalRev: {self.globalRev}")
                return data
            else:
                raise Exception(data['error'])
        except httpx.ReadTimeout:
            pass
        return []

    def fetchOpsOld(self, revision, count=100):
        _headers = {
            'X-Line-Access': self.authToken,
            'x-lpqs': "/P3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 102, 101,
                116, 99, 104, 79, 112, 115, 0, 0, 0, 0]
        sqrd += [10, 0, 2] + self.getIntBytes(revision, 8)
        sqrd += [8, 0, 3] + self.getIntBytes(count)
        sqrd += [10, 0, 4] + self.getIntBytes(self.globalRev, 8)
        sqrd += [10, 0, 5] + self.getIntBytes(self.individualRev, 8)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        hr = self.server.additionalHeaders(self.server.Headers, {
            "x-lst": "110000",
        })
        try:
            res = self.testPollConn.post(
                "https://gf.line.naver.jp/enc", data=data, headers=hr, timeout=180)
            if res.status_code == 200:
                data = self.decData(res.content)
                data = self.tryReadData(data)
                if 'fetchOps' in data:
                    for op in data['fetchOps']:
                        if op[3] == 0:
                            if 10 in op:
                                a = op[10].split('\x1e')
                                self.individualRev = a[0]
                                self.log(
                                    f"individualRev: {self.individualRev}")
                            if 11 in op:
                                b = op[11].split('\x1e')
                                self.globalRev = b[0]
                                self.log(f"globalRev: {self.globalRev}")
                    return data['fetchOps']
                else:
                    raise Exception(f"no data")
        except Exception as e:
            print(f"[fetchOps]{e}")
            return self.fetchOps(revision, count)
        return []

    def fetchOperations(self, localRev, count=100):
        params = [
            [10, 2, localRev],
            [8, 3, count],
        ]
        sqrd = self.generateDummyProtocol('fetchOperations', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S4", sqrd, 4)

    def sendEchoPush(self, text):
        # for long poll? check conn is alive
        # text: 1614384862517 = time
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('sendEchoPush') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def getRepairElements(self, profile: bool = True, settings: bool = False, syncReason: int = 5):
        params = [
            [12, 1, [
                [2, 1, profile],
                [2, 2, settings],
                [8, 11, syncReason],
            ]]

        ]
        sqrd = self.generateDummyProtocol('getRepairElements', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd, 4)

    def getSettingsAttributes2(self, attributesToRetrieve: list):
        """
            NOTIFICATION_ENABLE(0),
            NOTIFICATION_MUTE_EXPIRATION(1),
            NOTIFICATION_NEW_MESSAGE(2),
            NOTIFICATION_GROUP_INVITATION(3),
            NOTIFICATION_SHOW_MESSAGE(4),
            NOTIFICATION_INCOMING_CALL(5),
            NOTIFICATION_SOUND_MESSAGE(8),
            NOTIFICATION_SOUND_GROUP(9),
            NOTIFICATION_DISABLED_WITH_SUB(16),
            NOTIFICATION_PAYMENT(17),
            NOTIFICATION_MENTION(40),
            NOTIFICATION_THUMBNAIL(45),
            NOTIFICATION_BADGE_TALK_ONLY(65),
            NOTIFICATION_REACTION(67),
            PRIVACY_SYNC_CONTACTS(6),
            PRIVACY_SEARCH_BY_PHONE_NUMBER(7),
            PRIVACY_SEARCH_BY_USERID(13),
            PRIVACY_SEARCH_BY_EMAIL(14),
            PRIVACY_SHARE_PERSONAL_INFO_TO_FRIENDS(51),
            PRIVACY_ALLOW_SECONDARY_DEVICE_LOGIN(21),
            PRIVACY_PROFILE_IMAGE_POST_TO_MYHOME(23),
            PRIVACY_PROFILE_MUSIC_POST_TO_MYHOME(35),
            PRIVACY_PROFILE_HISTORY(57),
            PRIVACY_STATUS_MESSAGE_HISTORY(54),
            PRIVACY_ALLOW_FRIEND_REQUEST(30),
            PRIVACY_RECV_MESSAGES_FROM_NOT_FRIEND(25),
            PRIVACY_AGREE_USE_LINECOIN_TO_PAIDCALL(26),
            PRIVACY_AGREE_USE_PAIDCALL(27),
            PRIVACY_AGE_RESULT(60),
            PRIVACY_AGE_RESULT_RECEIVED(61),
            PRIVACY_ALLOW_FOLLOW(63),
            PRIVACY_SHOW_FOLLOW_LIST(64),
            CONTACT_MY_TICKET(10),
            IDENTITY_PROVIDER(11),
            IDENTITY_IDENTIFIER(12),
            SNS_ACCOUNT(19),
            PHONE_REGISTRATION(20),
            PWLESS_PRIMARY_CREDENTIAL_REGISTRATION(31),
            ALLOWED_TO_CONNECT_EAP_ACCOUNT(32),
            PREFERENCE_LOCALE(15),
            CUSTOM_MODE(22),
            EMAIL_CONFIRMATION_STATUS(24),
            ACCOUNT_MIGRATION_PINCODE(28),
            ENFORCED_INPUT_ACCOUNT_MIGRATION_PINCODE(29),
            SECURITY_CENTER_SETTINGS(18),
            E2EE_ENABLE(33),
            HITOKOTO_BACKUP_REQUESTED(34),
            CONTACT_ALLOW_FOLLOWING(36),
            PRIVACY_ALLOW_NEARBY(37),
            AGREEMENT_NEARBY(38),
            AGREEMENT_SQUARE(39),
            ALLOW_UNREGISTRATION_SECONDARY_DEVICE(41),
            AGREEMENT_BOT_USE(42),
            AGREEMENT_SHAKE_FUNCTION(43),
            AGREEMENT_MOBILE_CONTACT_NAME(44),
            AGREEMENT_SOUND_TO_TEXT(46),
            AGREEMENT_PRIVACY_POLICY_VERSION(47),
            AGREEMENT_AD_BY_WEB_ACCESS(48),
            AGREEMENT_PHONE_NUMBER_MATCHING(49),
            AGREEMENT_COMMUNICATION_INFO(50),
            AGREEMENT_THINGS_WIRELESS_COMMUNICATION(52),
            AGREEMENT_GDPR(53),
            AGREEMENT_PROVIDE_LOCATION(55),
            AGREEMENT_BEACON(56),
            AGREEMENT_CONTENTS_SUGGEST(58),
            AGREEMENT_CONTENTS_SUGGEST_DATA_COLLECTION(59),
            AGREEMENT_OCR_IMAGE_COLLECTION(62),
            AGREEMENT_ICNA(66),
            AGREEMENT_MID(68),
            HOME_NOTIFICATION_NEW_FRIEND(69),
            HOME_NOTIFICATION_FAVORITE_FRIEND_UPDATE(70),
            HOME_NOTIFICATION_GROUP_MEMBER_UPDATE(71),
            HOME_NOTIFICATION_BIRTHDAY(72),
            AGREEMENT_LINE_OUT_USE(73),
            AGREEMENT_LINE_OUT_PROVIDE_INFO(74);
            NOTIFICATION_ENABLE(0),
            NOTIFICATION_MUTE_EXPIRATION(1),
            NOTIFICATION_NEW_MESSAGE(2),
            NOTIFICATION_GROUP_INVITATION(3),
            NOTIFICATION_SHOW_MESSAGE(4),
            NOTIFICATION_INCOMING_CALL(5),
            NOTIFICATION_SOUND_MESSAGE(8),
            NOTIFICATION_SOUND_GROUP(9),
            NOTIFICATION_DISABLED_WITH_SUB(16),
            NOTIFICATION_PAYMENT(17),
            NOTIFICATION_MENTION(40),
            NOTIFICATION_THUMBNAIL(45),
            NOTIFICATION_BADGE_TALK_ONLY(65),
            NOTIFICATION_REACTION(67),
            PRIVACY_SYNC_CONTACTS(6),
            PRIVACY_SEARCH_BY_PHONE_NUMBER(7),
            PRIVACY_SEARCH_BY_USERID(13),
            PRIVACY_SEARCH_BY_EMAIL(14),
            PRIVACY_SHARE_PERSONAL_INFO_TO_FRIENDS(51),
            PRIVACY_ALLOW_SECONDARY_DEVICE_LOGIN(21),
            PRIVACY_PROFILE_IMAGE_POST_TO_MYHOME(23),
            PRIVACY_PROFILE_MUSIC_POST_TO_MYHOME(35),
            PRIVACY_PROFILE_HISTORY(57),
            PRIVACY_STATUS_MESSAGE_HISTORY(54),
            PRIVACY_ALLOW_FRIEND_REQUEST(30),
            PRIVACY_RECV_MESSAGES_FROM_NOT_FRIEND(25),
            PRIVACY_AGREE_USE_LINECOIN_TO_PAIDCALL(26),
            PRIVACY_AGREE_USE_PAIDCALL(27),
            PRIVACY_AGE_RESULT(60),
            PRIVACY_AGE_RESULT_RECEIVED(61),
            PRIVACY_ALLOW_FOLLOW(63),
            PRIVACY_SHOW_FOLLOW_LIST(64),
            CONTACT_MY_TICKET(10),
            IDENTITY_PROVIDER(11),
            IDENTITY_IDENTIFIER(12),
            SNS_ACCOUNT(19),
            PHONE_REGISTRATION(20),
            PWLESS_PRIMARY_CREDENTIAL_REGISTRATION(31),
            ALLOWED_TO_CONNECT_EAP_ACCOUNT(32),
            PREFERENCE_LOCALE(15),
            CUSTOM_MODE(22),
            EMAIL_CONFIRMATION_STATUS(24),
            ACCOUNT_MIGRATION_PINCODE(28),
            ENFORCED_INPUT_ACCOUNT_MIGRATION_PINCODE(29),
            SECURITY_CENTER_SETTINGS(18),
            E2EE_ENABLE(33),
            HITOKOTO_BACKUP_REQUESTED(34),
            CONTACT_ALLOW_FOLLOWING(36),
            PRIVACY_ALLOW_NEARBY(37),
            AGREEMENT_NEARBY(38),
            AGREEMENT_SQUARE(39),
            ALLOW_UNREGISTRATION_SECONDARY_DEVICE(41),
            AGREEMENT_BOT_USE(42),
            AGREEMENT_SHAKE_FUNCTION(43),
            AGREEMENT_MOBILE_CONTACT_NAME(44),
            AGREEMENT_SOUND_TO_TEXT(46),
            AGREEMENT_PRIVACY_POLICY_VERSION(47),
            AGREEMENT_AD_BY_WEB_ACCESS(48),
            AGREEMENT_PHONE_NUMBER_MATCHING(49),
            AGREEMENT_COMMUNICATION_INFO(50),
            AGREEMENT_THINGS_WIRELESS_COMMUNICATION(52),
            AGREEMENT_GDPR(53),
            AGREEMENT_PROVIDE_LOCATION(55),
            AGREEMENT_BEACON(56),
            AGREEMENT_CONTENTS_SUGGEST(58),
            AGREEMENT_CONTENTS_SUGGEST_DATA_COLLECTION(59),
            AGREEMENT_OCR_IMAGE_COLLECTION(62),
            AGREEMENT_ICNA(66),
            AGREEMENT_MID(68),
            HOME_NOTIFICATION_NEW_FRIEND(69),
            HOME_NOTIFICATION_FAVORITE_FRIEND_UPDATE(70),
            HOME_NOTIFICATION_GROUP_MEMBER_UPDATE(71),
            HOME_NOTIFICATION_BIRTHDAY(72),
            AGREEMENT_LINE_OUT_USE(73),
            AGREEMENT_LINE_OUT_PROVIDE_INFO(74);
        """
        if type(attributesToRetrieve) != list:
            attributesToRetrieve = [attributesToRetrieve]
            print('[attributesToRetrieve] plz using LIST')
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getSettingsAttributes2') + [0, 0, 0, 0]
        sqrd += [14, 0, 2, 8, 0, 0, 0, len(attributesToRetrieve)]
        for value in attributesToRetrieve:
            sqrd += self.getIntBytes(value)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def updateSettingsAttributes2(self, settings: dict, attributesToUpdate: list):
        if type(attributesToUpdate) != list:
            attributesToRetrieve = [attributesToUpdate]
            print('[attributesToRetrieve] plz using LIST')
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('updateSettingsAttributes2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [12, 0, 3]
        for sk, sv in settings.items():
            svt = type(sv)
            if svt == bool:
                sqrd += [2, 0, sk, int(sv)]
            elif svt == int:
                sqrd += [10, 0, sk] + self.getIntBytes(sv, 8)
            else:
                print(
                    f"[updateSettingsAttributes2] not support type {svt} (id: {sk})")
        sqrd += [0]
        sqrd += [14, 0, 4, 8, 0, 0, 0, len(attributesToUpdate)]
        for value in attributesToUpdate:
            sqrd += self.getIntBytes(value)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def rejectChatInvitation(self, chatMid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('rejectChatInvitation') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def updateProfileAttribute(self, attr: int, value: str):
        """
        attr:
            ALL(0),
            EMAIL(1),
            DISPLAY_NAME(2),
            PHONETIC_NAME(4),
            PICTURE(8),
            STATUS_MESSAGE(16),
            ALLOW_SEARCH_BY_USERID(32),
            ALLOW_SEARCH_BY_EMAIL(64),
            BUDDY_STATUS(128),
            MUSIC_PROFILE(256),
            AVATAR_PROFILE(512);
        """
        params = [
            [8, 1, 0],
            [8, 2, attr],
            [11, 3, value]
        ]
        sqrd = self.generateDummyProtocol('updateProfileAttribute', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getE2EEPublicKey(self, mid, keyVersion, keyId):
        params = [
            [11, 2, mid],
            [8, 3, keyVersion],
            [8, 4, keyId]
        ]
        sqrd = self.generateDummyProtocol('getE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getE2EEPublicKeys(self):
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getE2EEPublicKeysEx(self, ignoreE2EEStatus: int):
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeysEx', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def removeE2EEPublicKey(self, spec, keyId, keyData):
        params = [
            [12, 2, [
                [8, 1, spec],
                [8, 2, keyId],
                [11, 4, keyData]
            ]]
        ]
        sqrd = self.generateDummyProtocol('removeE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def registerE2EEPublicKey(self, version: int, keyId: int, keyData: str, time: int):
        params = [
            [12, 2, [
                [8, 1, version],
                [8, 2, keyId],
                [11, 4, keyData],
                [10, 5, time],
            ]]
        ]
        sqrd = self.generateDummyProtocol('registerE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def registerE2EEGroupKey(self, keyVersion: int, chatMid: str, members: list, keyIds: list, encryptedSharedKeys: list):
        if type(members) != list:
            raise Exception("[registerE2EEGroupKey] members must be a list")
        if type(keyIds) != list:
            raise Exception("[registerE2EEGroupKey] keyIds must be a list")
        if type(encryptedSharedKeys) != list:
            raise Exception(
                "[registerE2EEGroupKey] encryptedSharedKeys must be a list")
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [15, 4, [11, members]],
            [15, 5, [8, keyIds]],
            [15, 6, [11, encryptedSharedKeys]],
        ]
        sqrd = self.generateDummyProtocol('registerE2EEGroupKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getE2EEGroupSharedKey(self, keyVersion: int, chatMid: str, groupKeyId: int):
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [8, 4, groupKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEGroupSharedKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getLastE2EEGroupSharedKey(self, keyVersion: int, chatMid: str):
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
        ]
        sqrd = self.generateDummyProtocol(
            'getLastE2EEGroupSharedKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getLastE2EEPublicKeys(self, chatMid: str):
        params = [
            [11, 2, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getLastE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def requestE2EEKeyExchange(self, temporalPublicKey: str, keyVersion: int, keyId: int, verifier: str):
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, temporalPublicKey],
            [12, 3, [
                [8, 1, keyVersion],
                [8, 2, keyId]
            ]],
            [11, 4, verifier]
        ]
        sqrd = self.generateDummyProtocol('requestE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def respondE2EEKeyExchange(self, encryptedKeyChain: str, hashKeyChain: str):
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, encryptedKeyChain],
            [11, 3, hashKeyChain]
        ]
        sqrd = self.generateDummyProtocol('respondE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def negotiateE2EEPublicKey(self, mid: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('negotiateE2EEPublicKey') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT, sqrd)

    def react(self, messageId, reactionType=5):
        params = [
            [12, 1, [
                [8, 1, 0],
                [10, 2, messageId],
                [12, 3, [
                    [8, 1, reactionType]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('react', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def createChat(self, name, targetUserMids, type=0, picturePath=None):
        params = [
            [12, 1, [
                [8, 1, 0],
                [8, 2, type],
                [11, 3, name],
                [14, 4, [11, targetUserMids]],
                [11, 5, picturePath]
            ]]

        ]
        sqrd = self.generateDummyProtocol('createChat', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def updateRegion(self, region='TW'):
        raise Exception("updateRegion is not implemented")
        params = [
            [11, 4, region]

        ]
        sqrd = self.generateDummyProtocol('updateRegion', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getChatExistence(self, ids):
        params = [
            [12, 2, [
                [14, 1, [11, ids]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChatExistence', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getChatMembership(self, chatIds):
        params = [
            [12, 2, [
                [14, 1, [11, chatIds]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChatMembership', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def setChatHiddenStatus(self, chatId, bF=False):
        raise Exception("setChatHiddenStatus is not implemented")
        params = [
            [12, 1, [
                [11, 2, chatId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('setChatHiddenStatus', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getReadMessageOps(self, chatId):
        params = [
            [11, 2, chatId]
        ]
        sqrd = self.generateDummyProtocol('getReadMessageOps', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getReadMessageOpsInBulk(self, chatIds):
        params = [
            [15, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getReadMessageOpsInBulk', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getE2EEMessageInfo(self, mid, msgid, receiverKeyId):
        params = [
            [11, 2, mid],
            [11, 3, msgid],
            [8, 4, receiverKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEMessageInfo', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getMessageBoxCompactWrapUpList(self):
        raise Exception("getMessageBoxCompactWrapUpList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            'getMessageBoxCompactWrapUpList', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getRecentMessages(self, to):
        """ old func? still return 0 """
        params = [
            [11, 2, to],
            [8, 3, 101]
        ]
        sqrd = self.generateDummyProtocol('getRecentMessages', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getRecentMessagesV2(self, to):
        params = [
            [11, 2, to],
            [8, 3, 500]
        ]
        sqrd = self.generateDummyProtocol('getRecentMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getPreviousMessageIds(self, to, count=100):
        params = [
            [12, 2, [
                [11, 1, to],
                [8, 4, count],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getPreviousMessageIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getMessagesByIds(self, msgIds=[]):
        # messagesByIdsRequests
        # - messagesByIdsRequest
        # {1: 1626172142246, 2: 14386851950042}
        raise Exception("getMessagesByIds is not implemented")
        params = [
            [15, 2, [12, [
            ]]]
        ]
        sqrd = self.generateDummyProtocol('getMessagesByIds', params, 3)
        return self.postPackDataAndGetUnpackRespData("/S3", sqrd, 3)

    def getMessageBoxesByIds(self, mids=[]):
        params = [
            [12, 2, [
                [15, 1, [11, mids]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getMessageBoxesByIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getMessageBoxCompactWrapUpListV2(self, start=0, end=1):
        params = [
            [8, 2, start],
            [8, 3, end]
        ]
        sqrd = self.generateDummyProtocol(
            'getMessageBoxCompactWrapUpListV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getPreviousMessagesV2(self, mid, time, id):
        params = [
            [11, 2, mid],
            [12, 3, [
                [10, 1, time],
                [10, 2, id]
            ]],
            [8, 4, 101]
        ]
        sqrd = self.generateDummyProtocol('getPreviousMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getPreviousMessagesV2WithReadCount(self, mid, time, id, count=101):
        params = [
            [11, 2, mid],
            [12, 3, [
                [10, 1, time],
                [10, 2, id]
            ]],
            [8, 4, count]
        ]
        sqrd = self.generateDummyProtocol(
            'getPreviousMessagesV2WithReadCount', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getNextMessagesV2(self, mid, time, id):
        params = [
            [11, 2, mid],
            [12, 3, [
                [10, 1, time],
                [10, 2, id]
            ]],
            [8, 4, 101]  # count, 101 is max? maybe, hehe...
        ]
        sqrd = self.generateDummyProtocol('getNextMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getAllRoomIds(self):
        params = []
        sqrd = self.generateDummyProtocol('getAllRoomIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getCompactRooms(self, roomIds):
        params = [
            [15, 2, [11, roomIds]]
        ]
        sqrd = self.generateDummyProtocol('getCompactRooms', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def acquireCallTicket(self, to):
        params = [
            [11, 1, to]
        ]
        sqrd = self.generateDummyProtocol('acquireCallTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def isAbusive(self):
        """ idk """
        # 2021/09/16 it removed...
        params = [
            [8, 1, 0],
            [8, 2, 1],  # reportSource
        ]
        sqrd = self.generateDummyProtocol('isAbusive', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def removeBuddySubscriptionAndNotifyBuddyUnregistered(self, contactMids):
        """ OA only """
        params = [
            [15, 1, [11, contactMids]]
        ]
        sqrd = self.generateDummyProtocol(
            'removeBuddySubscriptionAndNotifyBuddyUnregistered', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def makeUserAddMyselfAsContact(self, contactMids):
        """ OA only """
        params = [
            [15, 1, [11, contactMids]]
        ]
        sqrd = self.generateDummyProtocol(
            'makeUserAddMyselfAsContact', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getFollowers(self, mid=None, eMid=None, cursor=None):
        data = [11, 1, mid]
        if eMid is not None:
            data = [11, 2, eMid]
        params = [
            [12, 2, [
                [12, 1, [
                    data
                ]],
                [11, 2, cursor]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getFollowers', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getFollowings(self, mid=None, eMid=None, cursor=None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid]
                ]],
                [11, 2, cursor]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getFollowings', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def removeFollower(self, mid=None, eMid=None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('removeFollower', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def follow(self, mid=None, eMid=None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('follow', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def unfollow(self, mid=None, eMid=None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('unfollow', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def bulkFollow(self, contactMids):
        """ disallow """
        params = [
            [12, 2, [
                [15, 2, [11, contactMids]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('bulkFollow', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def decryptFollowEMid(self, eMid):
        params = [
            [11, 2, eMid]
        ]
        sqrd = self.generateDummyProtocol('decryptFollowEMid', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getMessageReadRange(self, chatIds):
        params = [
            [15, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getMessageReadRange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def getChatRoomBGMs(self, chatIds: list):
        params = [
            [14, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getChatRoomBGMs', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5", sqrd, 5)

    def updateChatRoomBGM(self, chatId: str, chatRoomBGMInfo: str):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, chatId],
            [11, 3, chatRoomBGMInfo]
        ]
        sqrd = self.generateDummyProtocol('updateChatRoomBGM', params, 4)

    def addSnsId(self, snsAccessToken):
        params = [
            [8, 2, 1],  # FB?
            [11, 3, snsAccessToken],
        ]
        sqrd = self.generateDummyProtocol('addSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def removeSnsId(self):
        params = [
            [8, 2, 1],  # FB?
        ]
        sqrd = self.generateDummyProtocol('removeSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getContactRegistration(self, mid, type=0):
        """ MID(0),
            PHONE(1),
            EMAIL(2),
            USERID(3),
            PROXIMITY(4),
            GROUP(5),
            USER(6),
            QRCODE(7),
            PROMOTION_BOT(8),
            CONTACT_MESSAGE(9),
            FRIEND_REQUEST(10),
            REPAIR(128),
            FACEBOOK(2305),
            SINA(2306),
            RENREN(2307),
            FEIXIN(2308),
            BBM(2309),
            BEACON(11);
        """
        params = [
            [11, 1, mid],
            [8, 2, type],
        ]
        sqrd = self.generateDummyProtocol('getContactRegistration', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getHiddenContactMids(self):
        params = []
        sqrd = self.generateDummyProtocol('getHiddenContactMids', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def blockRecommendation(self, mid):
        params = [
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol('blockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def unblockRecommendation(self, mid):
        params = [
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol('unblockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getRecommendationIds(self):
        params = []
        sqrd = self.generateDummyProtocol('getRecommendationIds', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getBlockedRecommendationIds(self):
        params = []
        sqrd = self.generateDummyProtocol(
            'getBlockedRecommendationIds', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def sync(self, revision: int, count: int = 50):
        """ fetchOps for IOS """
        # 2021/7/26 it blocked, but 2021/7/20 it working
        # LINE are u here?
        params = [
            [12, 1, [
                [10, 1, revision],
                [8, 2, count],
                [10, 4, self.individualRev],
                # [10, 5, self.globalRev]
            ]]
        ]
        sqrd = self.generateDummyProtocol('sync', params, 4)
        res = self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)
        if 1 in res:
            res = res[1]
            ops = res[1]
            isSync = res[2]
            if not isSync:
                self.individualRev = res[4][2]
            return ops
        elif 2 in res:
            # revision - 1 for sync revision on next req
            return self.sync(res[2][2] - 1, count)
        return None

    def updateChatRoomAnnouncement(self, gid: str, announcementId: int, messageLink: str, text: str, imgLink: str):
        params = [
            [11, 2, gid],
            [10, 3, announcementId],
            [12, 4, [
                [8, 1, 5],
                [11, 2, text],
                [11, 3, messageLink],
                [11, 4, imgLink]
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'updateChatRoomAnnouncement', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def reissueTrackingTicket(self):
        params = []
        sqrd = self.generateDummyProtocol('reissueTrackingTicket', params, 4)

    def getExtendedProfile(self, syncReason=7):
        params = [
            [8, 1, syncReason]
        ]
        sqrd = self.generateDummyProtocol('getExtendedProfile', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def updateExtendedProfileAttribute(self, year: str, yearPrivacyLevelType: int, yearEnabled: bool, day: str, dayPrivacyLevelType: int, dayEnabled: bool):
        """
        - PrivacyLevelType
            PUBLIC(0),
            PRIVATE(1);
        """
        params = [
            [8, 1, self.getCurrReqId()],
            [8, 2, 0],  # attr
            [12, 3, [
                [12, 1, [
                    [11, 1, year],
                    [8, 2, yearPrivacyLevelType],
                    [2, 3, yearEnabled],
                    [11, 5, day],
                    [8, 6, dayPrivacyLevelType],
                    [2, 7, dayEnabled],
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'updateExtendedProfileAttribute', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def setNotificationsEnabled(self, type: int, target: str, enablement: bool = True):
        """
        - type
            USER(0),
            ROOM(1),
            GROUP(2),
            SQUARE(3),
            SQUARE_CHAT(4),
            SQUARE_MEMBER(5),
            BOT(6);
        """
        params = [
            [8, 1, self.getCurrReqId()],
            [8, 2, type],  # attr
            [11, 3, target],
            [2, 4, enablement]
        ]
        sqrd = self.generateDummyProtocol('setNotificationsEnabled', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findAndAddContactsByPhone(self, phones: list, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        if type(phones) != list:
            raise Exception(
                "[findAndAddContactsByPhone] phones must be a list")
        params = [
            [8, 1, self.getCurrReqId()],
            [14, 2, [11, phones]],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol(
            'findAndAddContactsByPhone', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findAndAddContactsByUserid(self, searchId: str, reference: str = '{"screen":"friendAdd:idSearch","spec":"native"}'):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol(
            'findAndAddContactsByUserid', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def syncContacts(self, phones: list = [], emails: list = [], userids: list = []):
        """
        - type
            ADD(0),
            REMOVE(1),
            MODIFY(2);
        """
        if type(phones) != list:
            raise Exception("[syncContacts] phones must be a list")
        if type(emails) != list:
            raise Exception("[syncContacts] emails must be a list")
        if type(userids) != list:
            raise Exception("[syncContacts] userids must be a list")
        localContacts = []
        luid = 0
        for phone in phones:
            luid += 1
            localContacts.append([
                [8, 1, 0],
                [11, 2, luid],
                [15, 11, [11, [phone]]],
            ])
        for email in emails:
            luid += 1
            localContacts.append([
                [8, 1, 0],
                [11, 2, luid],
                [15, 12, [11, [email]]],
            ])
        for userid in userids:
            luid += 1
            localContacts.append([
                [8, 1, 0],
                [11, 2, luid],
                [15, 13, [11, [userid]]],
            ])
        base_localContacts = [
            [8, 1, 0],
            [11, 2, luid],
            [15, 11, [11, phones]],
            [15, 12, [11, emails]],
            [15, 13, [11, userids]],
            # [11, 14, mobileContactName],
            # [11, 15, phoneticName],
        ]
        params = [
            [8, 1, self.getCurrReqId()],
            [15, 2, [12, localContacts]],
        ]
        sqrd = self.generateDummyProtocol('syncContacts', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getContactWithFriendRequestStatus(self, mid: str):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol(
            'getContactWithFriendRequestStatus', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findContactsByPhone(self, phones: list):
        if type(phones) != list:
            raise Exception("[findContactsByPhone] phones must be a list")
        params = [
            [14, 2, [11, phones]]
        ]
        sqrd = self.generateDummyProtocol('findContactsByPhone', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findContactByUserid(self, searchId: str):
        params = [
            [11, 2, searchId]
        ]
        sqrd = self.generateDummyProtocol('findContactByUserid', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findContactByMetaTag(self, searchId: str, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        params = [
            [11, 2, searchId],
            [11, 3, reference]
        ]
        sqrd = self.generateDummyProtocol('findContactByMetaTag', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findAndAddContactByMetaTag(self, searchId: str, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference]
        ]
        sqrd = self.generateDummyProtocol(
            'findAndAddContactByMetaTag', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def updateContactSetting(self, mid: str, flag: int, value: str):
        """
        - flag
            CONTACT_SETTING_NOTIFICATION_DISABLE(1),
            CONTACT_SETTING_DISPLAY_NAME_OVERRIDE(2),
            CONTACT_SETTING_CONTACT_HIDE(4),
            CONTACT_SETTING_FAVORITE(8),
            CONTACT_SETTING_DELETE(16);
        """
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, mid],
            [8, 3, flag],
            [11, 4, value]
        ]
        sqrd = self.generateDummyProtocol('updateContactSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def getFavoriteMids(self):
        params = []
        sqrd = self.generateDummyProtocol('getFavoriteMids', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def sendMessageAwaitCommit(self):
        params = []
        sqrd = self.generateDummyProtocol('sendMessageAwaitCommit', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def findContactByUserTicket(self, ticketIdWithTag: str):
        params = [
            [11, 2, ticketIdWithTag]
        ]
        sqrd = self.generateDummyProtocol('findContactByUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def invalidateUserTicket(self):
        params = []
        sqrd = self.generateDummyProtocol('invalidateUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def unregisterUserAndDevice(self):
        params = []
        sqrd = self.generateDummyProtocol('unregisterUserAndDevice', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def verifyQrcode(self, verifier, pinCode):
        params = [
            [11, 2, verifier],
            [11, 3, pinCode],
        ]
        sqrd = self.generateDummyProtocol('verifyQrcode', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S4", sqrd, 4)

    def reportAbuseEx(self, message: list = None, lineMeeting: list = None):
        """
        - reportSource
            UNKNOWN(0),
            DIRECT_INVITATION(1),
            DIRECT_CHAT(2),
            GROUP_INVITATION(3),
            GROUP_CHAT(4),
            ROOM_INVITATION(5),
            ROOM_CHAT(6),
            FRIEND_PROFILE(7),
            DIRECT_CHAT_SELECTED(8),
            GROUP_CHAT_SELECTED(9),
            ROOM_CHAT_SELECTED(10),
            DEPRECATED(11);
        - spammerReasons
            OTHER(0),
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3);
        """
        if message is None and lineMeeting is None:
            raise Exception(
                "Should use reportAbuseExWithMessage() or reportAbuseExWithLineMeeting()")
        params = [
            [12, 2, [
                [12, 1, [
                    [12, 1, message],
                    [12, 2, lineMeeting],
                ]],
            ]],
        ]
        sqrd = self.generateDummyProtocol('reportAbuseEx', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S4", sqrd, 4)

    def reportAbuseExWithMessage(self, reportSource: int, spammerReasons: int, messageIds: list, messages: list, senderMids: list, contentTypes: list, createdTimes: list, metadatas: list, metadata: dict, applicationType: int = 384):
        abuseMessages = []
        def _get(a, b, c): return a[b] if len(a) > b else c
        for i in range(len(messageIds)):
            abuseMessages.append([
                [10, 1, _get(messageIds, i, 0)],
                [11, 2, _get(messages, i, "")],
                [11, 3, _get(senderMids, i, "")],
                [8, 4, _get(contentTypes, i, 0)],
                [10, 5, _get(createdTimes, i, 0)],
                [13, 6, [11, 11, _get(metadatas, i, {})]],
            ])
        # metadata["groupMid"] = groupMid
        # metadata["groupName"] = groupName
        # metadata["inviterMid"] = inviterMid
        # metadata["picturePath"] = picturePath
        withMessage = [
            [8, 1, reportSource],
            [8, 2, applicationType],
            [15, 3, [8, [spammerReasons]]],
            [15, 4, [12, abuseMessages]],
            [13, 5, [11, 11, metadata]],
        ]
        return self.reportAbuseEx(message=withMessage)

    def reportAbuseExWithLineMeeting(self, reporteeMid: str, spammerReasons: int, spaceIds: list, objectIds: list, chatMid: str):
        evidenceIds = []
        def _get(a, b, c): return a[b] if len(a) > b else c
        for i in range(len(spaceIds)):
            evidenceIds.append([
                [11, 1, _get(spaceIds, i, "")],
                [11, 2, _get(objectIds, i, "")],
            ])
        withLineMeeting = [
            [11, 1, reporteeMid],
            [15, 2, [8, [spammerReasons]]],
            [15, 3, [12, evidenceIds]],
            [11, 4, chatMid],
        ]
        return self.reportAbuseEx(lineMeeting=withLineMeeting)

    def getCountryWithRequestIp(self):
        params = []
        sqrd = self.generateDummyProtocol('getCountryWithRequestIp', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5', sqrd, 5)

    def notifyBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyBuddyOnAir is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "notifyBuddyOnAir", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getSuggestRevisions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestRevisions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSuggestRevisions", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateProfileAttributes(self, profileAttribute: int, value: str, meta: dict = {}):
        # NO TEST
        # if u can check it, plz report on DC group
        params = [
            [8, 1, self.getCurrReqId()],
            [12, 2, [
                [13, 1, [8, 12, [
                    [8, 12, {
                        profileAttribute: [
                            [11, 1, value],
                            [13, 2, [11, 11, meta]],
                        ]
                    }]
                ]]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "updateProfileAttributes", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateNotificationToken(self, token: str, type: int = 21):
        params = [
            [11, 2, token],  # generated by google api
            [8, 3, type]
        ]
        sqrd = self.generateDummyProtocol(
            "updateNotificationToken", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def disableNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("disableNearby is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "disableNearby", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def createRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createRoom", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def tryFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("tryFriendRequest is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "tryFriendRequest", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def generateUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("generateUserTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "generateUserTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getRecentFriendRequests(self):
        params = []
        sqrd = self.generateDummyProtocol(
            "getRecentFriendRequests", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateSettingsAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttribute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSettingsAttribute", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def resendPinCode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "resendPinCode", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def notifyRegistrationComplete(self, udidHash: str, applicationTypeWithExtensions: str = "ANDROID\t11.19.1\tAndroid OS\t7.0"):
        params = [
            [11, 2, udidHash],  # len 32 hash
            [11, 3, applicationTypeWithExtensions],
        ]
        sqrd = self.generateDummyProtocol(
            "notifyRegistrationComplete", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def createGroupV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroupV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createGroupV2", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportSpam(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpam is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSpam", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def requestResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestResendMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "requestResendMessage", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def inviteFriendsBySms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteFriendsBySms is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "inviteFriendsBySms", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def findGroupByTicketV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicketV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findGroupByTicketV2", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getInstantNews(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getInstantNews is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getInstantNews", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def createQrcodeBase64Image(self, url: str):
        params = [
            [11, 2, url]
        ]
        sqrd = self.generateDummyProtocol(
            "createQrcodeBase64Image", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def findSnsIdUserStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSnsIdUserStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findSnsIdUserStatus", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getPendingAgreements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPendingAgreements is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPendingAgreements", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyIdentityCredentialWithResult(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "verifyIdentityCredentialWithResult is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyIdentityCredentialWithResult", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerWithSnsId(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithSnsId is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithSnsId", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyAccountMigration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigration is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyAccountMigration", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getEncryptedIdentityV3(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getEncryptedIdentityV3 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getEncryptedIdentityV3", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reissueGroupTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueGroupTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reissueGroupTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUserTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getUserTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def changeVerificationMethod(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("changeVerificationMethod is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "changeVerificationMethod", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getRooms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRooms is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRooms", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getAcceptedProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAcceptedProximityMatches is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getAcceptedProximityMatches", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getChatEffectMetaList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChatEffectMetaList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChatEffectMetaList", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def notifyInstalled(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyInstalled is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "notifyInstalled", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reissueUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueUserTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reissueUserTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def sendDummyPush(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("sendDummyPush is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "sendDummyPush", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyAccountMigrationPincode", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def acquireCallRoute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acquireCallRoute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "acquireCallRoute", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerDeviceWithoutPhoneNumberWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerDeviceWithoutPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDeviceWithoutPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDeviceWithoutPhoneNumber", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def inviteIntoGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "inviteIntoGroup", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def removeAllMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeAllMessages is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "removeAllMessages", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerWithPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithPhoneNumber", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRingbackTone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRingbackTone", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportSpammer(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpammer is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSpammer", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def loginWithVerifierForCerificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCerificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithVerifierForCerificate", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def logoutSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logoutSession is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "logoutSession", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def clearIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "clearIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateGroupPreferenceAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroupPreferenceAttribute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateGroupPreferenceAttribute", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def closeProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("closeProximityMatch is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "closeProximityMatch", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def loginWithVerifierForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCertificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithVerifierForCertificate", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def respondResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("respondResendMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "respondResendMessage", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getProximityMatchCandidateList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidateList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProximityMatchCandidateList", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportDeviceState(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportDeviceState is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportDeviceState", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def sendChatRemoved(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("sendChatRemoved is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "sendChatRemoved", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getAuthQrcode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAuthQrcode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getAuthQrcode", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateAccountMigrationPincode", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerWithSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithSnsIdAndIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithSnsIdAndIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def startUpdateVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startUpdateVerification is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "startUpdateVerification", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def notifySleep(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifySleep is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "notifySleep", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportContacts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportContacts is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportContacts", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def acceptGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "acceptGroupInvitation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def loginWithVerifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifier is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithVerifier", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttributes is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSettingsAttributes", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyPhoneNumberForLogin(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumberForLogin is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyPhoneNumberForLogin", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getUpdatedMessageBoxIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUpdatedMessageBoxIds is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getUpdatedMessageBoxIds", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def inviteIntoRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "inviteIntoRoom", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def removeFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeFriendRequest is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "removeFriendRequest", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def acceptGroupInvitationByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitationByTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "acceptGroupInvitationByTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportProfile is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportProfile", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateProfile is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateProfile", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def createGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createGroup", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def resendEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendEmailConfirmation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "resendEmailConfirmation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerWithPhoneNumberAndPassword(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithPhoneNumberAndPassword is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithPhoneNumberAndPassword", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def openProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("openProximityMatch is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "openProximityMatch", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyPhone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyPhone", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getSessions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSessions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSessions", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def clearRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearRingbackTone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "clearRingbackTone", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def leaveGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveGroup", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getProximityMatchCandidates(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidates is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProximityMatchCandidates", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def createAccountMigrationPincodeSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "createAccountMigrationPincodeSession is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createAccountMigrationPincodeSession", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRoom", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def startVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startVerification is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "startVerification", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def logout(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logout is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "logout", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateNotificationTokenWithBytes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateNotificationTokenWithBytes is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateNotificationTokenWithBytes", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def confirmEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("confirmEmail is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "confirmEmail", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getIdentityIdentifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getIdentityIdentifier is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getIdentityIdentifier", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateDeviceInfo(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateDeviceInfo is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateDeviceInfo", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerDeviceWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerDeviceWithIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDeviceWithIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def wakeUpLongPolling(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("wakeUpLongPolling is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "wakeUpLongPolling", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateAndGetNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAndGetNearby is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateAndGetNearby", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSettingsAttributes is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSettingsAttributes", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def rejectGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "rejectGroupInvitation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def loginWithIdentityCredentialForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "loginWithIdentityCredentialForCertificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithIdentityCredentialForCertificate", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportSettings", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerWithExistingSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithExistingSnsIdAndIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithExistingSnsIdAndIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def requestAccountPasswordReset(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestAccountPasswordReset is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "requestAccountPasswordReset", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def requestEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestEmailConfirmation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "requestEmailConfirmation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def resendPinCodeBySMS(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCodeBySMS is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "resendPinCodeBySMS", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getSuggestIncrements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestIncrements is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSuggestIncrements", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def noop(self):
        params = []
        sqrd = self.generateDummyProtocol(
            "noop", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getSuggestSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSuggestSettings", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def acceptProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptProximityMatches is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "acceptProximityMatches", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def kickoutFromGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("kickoutFromGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "kickoutFromGroup", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def loginWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def setIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "setIdentityCredential", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyLocation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def verifyPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyPhoneNumber", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerDevice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDevice is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDevice", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getRingtone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRingtone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRingtone", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def findGroupByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findGroupByTicket", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportClientStatistics(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportClientStatistics is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportClientStatistics", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def updateGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateGroup", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getEncryptedIdentityV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getEncryptedIdentityV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getEncryptedIdentityV2", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportAbuse(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportAbuse is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reportAbuse", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getAnalyticsInfo(self):
        params = []
        sqrd = self.generateDummyProtocol(
            "getAnalyticsInfo", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getCompactGroups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactGroups is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCompactGroups", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def setBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "setBuddyLocation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def isUseridAvailable(self, searchId: str):
        params = [
            [11, 2, searchId]
        ]
        sqrd = self.generateDummyProtocol(
            "isUseridAvailable", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def removeBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "removeBuddyLocation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def report(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("report is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "report", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def registerUserid(self, searchId: str):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId]
        ]
        sqrd = self.generateDummyProtocol(
            "registerUserid", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def finishUpdateVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("finishUpdateVerification is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "finishUpdateVerification", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def notifySleepV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifySleepV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "notifySleepV2", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getCompactRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCompactRoom", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def cancelGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("cancelGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "cancelGroupInvitation", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def clearRingtone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearRingtone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "clearRingtone", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def notifyUpdated(self, lastRev: int, udidHash: str, oldUdidHash: str, deviceName: str = "DeachSword", systemName: str = "Android OS", systemVersion: str = "9.1", model: str = "DeachSword", webViewVersion: str = "96.0.4664.45", carrierCode: int = 0, carrierName: str = "", applicationType: int = 32):
        params = [
            [10, 2, lastRev],
            [12, 3, [
                [11, 1, deviceName],  # DeachSword
                [11, 2, systemName],  # Android OS
                [11, 3, systemVersion],  # 9.1
                [11, 4, model],  # DeachSword
                [11, 5, webViewVersion],  # 96.0.4664.45
                [8, 10, carrierCode],  # 0
                [11, 10, carrierName],
                [8, 20, applicationType],  # 32
            ]],
            [11, 4, udidHash],  # 57f44905fd117a5661828440bb7d1bd5
            [11, 4, oldUdidHash],  # 5284047f4ffb4e04824a2fd1d1f0cd62
        ]
        sqrd = self.generateDummyProtocol(
            "notifyUpdated", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getGroupWithoutMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getGroupWithoutMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getGroupWithoutMembers", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getShakeEventV1(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getShakeEventV1 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getShakeEventV1", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def reportPushRecvReports(self, pushTrackingId: str, recvTimestamp: int, battery: int = 22, batteryMode: int = 1, clientNetworkType: int = 1, carrierCode: str = "", displayTimestamp: int = 0):
        pushRecvReports = []
        pushRecvReports.append([
            [11, 1, pushTrackingId],  # E5DNYLDgRI6uEHUNdDWFqg==
            [10, 2, recvTimestamp],  # 1637752269347
            [8, 3, battery],
            [8, 4, batteryMode],
            [8, 5, clientNetworkType],
            [11, 6, carrierCode],
            [10, 7, displayTimestamp],
        ])
        params = [
            [8, 1, 0],
            [15, 2, [12, pushRecvReports]]
        ]
        sqrd = self.generateDummyProtocol(
            "reportPushRecvReports", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getFriendRequests(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        params = []
        sqrd = self.generateDummyProtocol(
            "getFriendRequests", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def requestIdentityUnbind(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestIdentityUnbind is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "requestIdentityUnbind", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def addToFollowBlacklist(self, mid: str = None, eMid: str = None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid],
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "addToFollowBlacklist", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def removeFromFollowBlacklist(self, mid: str = None, eMid: str = None):
        params = [
            [12, 2, [
                [12, 1, [
                    [11, 1, mid],
                    [11, 2, eMid],
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "removeFromFollowBlacklist", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)

    def getFollowBlacklist(self, cursor: str = None):
        params = [
            [12, 2, [
                [11, 1, cursor]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "getFollowBlacklist", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE)


    def determineMediaMessageFlow(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("determineMediaMessageFlow is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("determineMediaMessageFlow", params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH ,sqrd,  self.TalkService_RES_TYPE)