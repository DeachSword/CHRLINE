# -*- coding: utf-8 -*-
import httpx
import requests
from random import randint
try:
    from ..exceptions import LineServiceException
except:
    pass


class TalkService():
    url = "https://ga2.line.naver.jp/enc"
    TalkService_REQ_TYPE = 4
    TalkService_RES_TYPE = 5
    TalkService_API_PATH = "/S5"

    def __init__(self):
        self.testPollConn = requests.session()

    def sendMessage(self,
                    to: str,
                    text: str,
                    contentType: int = 0,
                    contentMetadata: dict = None,
                    relatedMessageId: str = None,
                    location: dict = None,
                    chunk: list = None):
        if contentMetadata is None:
            contentMetadata = {}

        METHOD_NAME = "sendMessage"
        SERVICE_NAME = "TalkService"
        RES_TYPE = 5
        ENDPOINT = "/S5"
        relatedMessageServiceCode = 1

        if self.getToType(to) == 4:
            SERVICE_NAME = "SquareService"
            RES_TYPE = 4
            ENDPOINT = "/SQ1"
            relatedMessageServiceCode = 2

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
            message.append([11, 10, text])
        if location is not None:
            locationObj = [
                [11, 1, location.get(1, 'CHRLINE API')],
                [
                    11, 2,
                    location.get(2, 'https://github.com/DeachSword/CHRLINE')
                ],
                [4, 3, location.get(3, 0)],
                [4, 4, location.get(4, 0)],
                [11, 6, location.get(6, 'PC0')],
                [8, 7, location.get(7, 2)],
            ]
            message.append([12, 11, locationObj])
        if chunk is not None:
            message.append([15, 20, [11, chunk]])
        if relatedMessageId is not None:
            message.append([11, 21, relatedMessageId])
            message.append(
                # messageRelationType; FORWARD(0), AUTO_REPLY(1), SUBORDINATE(2), REPLY(3);
                [8, 22, 3])
            message.append([8, 24, relatedMessageServiceCode])
        params = [[8, 1, self.getCurrReqId()], [12, 2, message]]
        if self.getToType(to) == 4:
            params = [[
                12, 1,
                [
                    [8, 1, self.getCurrReqId()],
                    [11, 2, to],
                    [12, 3, [[12, 1, message]]],
                ]
            ]]
        else:
            params = [[8, 1, self.getCurrReqId()], [12, 2, message]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 4)
        try:
            return self.postPackDataAndGetUnpackRespData(
                ENDPOINT,
                sqrd,
                RES_TYPE,
                readWith=f"{SERVICE_NAME}.{METHOD_NAME}")
        except LineServiceException as e:
            if e.code in [82, 99]:
                return self.sendMessageWithE2EE(to, text, contentType,
                                                contentMetadata,
                                                relatedMessageId)
            raise e
        except Exception as e:
            raise e

    def replyMessage(self,
                     msgData: any,
                     text: str,
                     contentType: int = 0,
                     contentMetadata: dict = None,
                     location: dict = None,
                     relatedMessageId: str = None):
        to = self.checkAndGetValue(msgData, 'to', 2)
        toType = self.checkAndGetValue(msgData, 'toType', 3)
        if contentMetadata is None:
            contentMetadata = {}
        if relatedMessageId is None:
            relatedMessageId = self.checkAndGetValue(msgData, 'id', 4)
        opType = self.checkAndGetValue(msgData, 'opType')
        if toType == 0 and opType in [26, None]:  # opType for hooks
            to = self.checkAndGetValue(msgData, '_from', 1)
        if self.checkAndGetValue(msgData, 'isE2EE') is True:
            if contentType == 15:
                text = location  # difference
            return self.sendMessageWithE2EE(to, text, contentType,
                                            contentMetadata, relatedMessageId)
        return self.sendMessage(to, text, contentType, contentMetadata,
                                relatedMessageId)

    def sendContact(self, to, mid, displayName=None):
        if displayName is None:
            contentMetadata = {"mid": mid}
        else:
            contentMetadata = {"mid": mid, "displayName": displayName}
        return self.sendMessage(to,
                                None,
                                contentType=13,
                                contentMetadata=contentMetadata)

    def sendLocation(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, None, contentType=15, location=data)

    def sendLocationMessage(self,
                            to,
                            title,
                            la=0.0,
                            lb=0.0,
                            subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, "test", location=data)

    def sendGift(self, to, productId, productType):
        if productType not in ['theme', 'sticker']:
            raise Exception('Invalid productType value')
        contentMetadata = {
            'MSGTPL': str(randint(0, 12)),
            'PRDTYPE': productType.upper(),
            'STKPKGID' if productType == 'sticker' else 'PRDID': productId
        }
        return self.sendMessage(to=to,
                                text='',
                                contentMetadata=contentMetadata,
                                contentType=9)

    def sendMessageWithE2EE(self,
                            to,
                            text,
                            contentType=0,
                            contentMetadata=None,
                            relatedMessageId=None):
        if contentMetadata is None:
            contentMetadata = {}
        chunk = self.encryptE2EEMessage(to, text, contentType=contentType)
        contentMetadata = self.server.additionalHeaders(
            contentMetadata, {
                'e2eeVersion': '2',
                'contentType': str(contentType),
                'e2eeMark': '2'
            })
        return self.sendMessageWithChunks(to, chunk, contentType,
                                          contentMetadata, relatedMessageId)

    def sendMessageWithChunks(self,
                              to,
                              chunk,
                              contentType=0,
                              contentMetadata=None,
                              relatedMessageId=None):
        if contentMetadata is None:
            contentMetadata = {}
        return self.sendMessage(to,
                                None,
                                contentType,
                                contentMetadata,
                                relatedMessageId,
                                chunk=chunk)

    def sendCompactMessage(self, to: str, text: str, chunks: list = None):
        cType = -1  # 2 = TEXT, 4 = STICKER, 5 = E2EE_TEXT, 6 = E2EE_LOCATION
        ep = self.LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT
        if chunks is None:
            chunks = []
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
        hr = self.server.additionalHeaders(self.server.Headers,
                                           {'x-lai': str(_reqId)})
        try:
            return self.postPackDataAndGetUnpackRespData(ep,
                                                         sqrd,
                                                         -7,
                                                         headers=hr)
        except LineServiceException as e:
            if e.code in [82, 99]:
                return self.sendCompactE2EEMessage(to, text)
            raise e
        except Exception as e:
            raise e

    def sendCompactE2EEMessage(self, to, text):
        chunks = self.encryptE2EEMessage(to, text, isCompact=True)
        return self.sendCompactMessage(to, None, chunks)

    def sendSuperEzTagAll(self, to: str, text: str, **kwargs):
        """ 2022/08/25 """
        a = [['contentType', 0], ['contentMetadata', {}],
             ['relatedMessageId', None]]
        k = kwargs
        L = 0
        m = {}
        r = text
        S = 0
        T = 0
        for ck, cv in a:
            if ck not in k:
                k[ck] = cv
        if '@' not in r:
            r = f'@CHRLINE-v2.5.0-RC-Will-NOT-Be-Released {r}'
        S = r.index('@')
        T = r[S:].index(' ')
        L = S + (T if T != -1 else 1)
        m = self.genMentionData([{'S': S, 'L': L, 'A': True}])
        k['contentMetadata'].update(m)
        k['to'] = to
        k['text'] = r
        return self.sendMessage(**k)

    def getEncryptedIdentity(self):
        METHOD_NAME = "getEncryptedIdentity"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 69, 110, 99, 114, 121,
            112, 116, 101, 100, 73, 100, 101, 110, 116, 105, 116, 121, 0, 0, 0,
            0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getProfile(self):
        METHOD_NAME = "getProfile"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getSettings(self):
        METHOD_NAME = "getSettings"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 83, 101, 116, 116, 105,
            110, 103, 115, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def sendChatChecked(self, chatMid, lastMessageId):
        METHOD_NAME = "sendChatChecked"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 15, 115, 101, 110, 100, 67, 104, 97, 116,
            67, 104, 101, 99, 107, 101, 100, 0, 0, 0, 0
        ]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in chatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(lastMessageId)]
        for value in lastMessageId:
            sqrd.append(ord(value))
        # [3, 0, 4] # sessionId
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def unsendMessage(self, messageId):
        METHOD_NAME = "unsendMessage"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 13, 117, 110, 115, 101, 110, 100, 77, 101,
            115, 115, 97, 103, 101, 0, 0, 0, 0
        ]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getContact(self, mid: str):
        METHOD_NAME = "getContact"
        params = [[11, 2, mid]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 3)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getContacts(self, mids):
        METHOD_NAME = "getContacts"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 67, 111, 110, 116, 97,
            99, 116, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0,
            len(mids)
        ]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getContactsV2(self, mids):
        METHOD_NAME = "getContactsV2"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 67, 111, 110, 116, 97,
            99, 116, 115, 86, 50, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def findAndAddContactsByMid(
            self,
            mid,
            reference='{"screen":"groupMemberList","spec":"native"}'):
        METHOD_NAME = "findAndAddContactsByMid"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 23, 102, 105, 110, 100, 65, 110, 100, 65,
            100, 100, 67, 111, 110, 116, 97, 99, 116, 115, 66, 121, 77, 105,
            100, 0, 0, 0, 0
        ]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        sqrd += [11, 0, 4] + self.getStringBytes(reference)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getGroup(self, mid):
        raise NotImplementedError("getGroup is too old, please use getChats")
        METHOD_NAME = "getGroup"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 71, 114, 111, 117, 112, 0,
            0, 0, 0, 11, 0, 2, 0, 0, 0, 33
        ]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getGroups(self, mids):
        raise NotImplementedError("getGroups is too old, please use getChats")
        METHOD_NAME = "getGroups"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 9, 103, 101, 116, 71, 114, 111, 117, 112,
            115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0,
            len(mids)
        ]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getGroupsV2(self, mids):
        raise NotImplementedError(
            "getGroupsV2 is too old, please use getChats")
        METHOD_NAME = "getGroupsV2"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 71, 114, 111, 117, 112,
            115, 86, 50, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0,
            len(mids)
        ]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getChats(self, mids, withMembers=True, withInvitees=True):
        METHOD_NAME = "getChats"
        if type(mids) != list:
            raise Exception("[getChats] mids must be a list")
        params = [[
            12, 1,
            [[15, 1, [11, mids]], [2, 2, withMembers], [2, 3, withInvitees]]
        ]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 3)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAllChatMids(self, withMembers=True, withInvitees=True):
        METHOD_NAME = 'getAllChatMids'
        params = [[12, 1, [[2, 1, withMembers], [2, 2, withInvitees]]],
                  [8, 2, 7]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getCompactGroup(self, mid):
        METHOD_NAME = "getCompactGroup"
        raise NotImplementedError(
            "getCompactGroup is too old, please use getChats")
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 67, 111, 109, 112, 97,
            99, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33
        ]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def deleteOtherFromChat(self, to, mid):
        METHOD_NAME = "deleteOtherFromChat"
        if type(mid) == list:
            _lastReq = None
            for _mid in mid:
                print(
                    f'[deleteOtherFromChat] The parameter \'mid\' should be str'
                )
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 19, 100, 101, 108, 101, 116, 101, 79, 116,
            104, 101, 114, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]  # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def inviteIntoChat(self, to, mids):
        METHOD_NAME = "inviteIntoChat"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 14, 105, 110, 118, 105, 116, 101, 73, 110,
            116, 111, 67, 104, 97, 116, 0, 0, 0, 0
        ]
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def cancelChatInvitation(self, to, mid):
        METHOD_NAME = "cancelChatInvitation"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 20, 99, 97, 110, 99, 101, 108, 67, 104, 97,
            116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]  # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def deleteSelfFromChat(self, to):
        METHOD_NAME = "deleteSelfFromChat"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 18, 100, 101, 108, 101, 116, 101, 83, 101,
            108, 102, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0
        ]
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def acceptChatInvitation(self, to):
        METHOD_NAME = "acceptChatInvitation"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 20, 97, 99, 99, 101, 112, 116, 67, 104, 97,
            116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(self.getCurrReqId())
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        _d = self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")
        return _d

    def reissueChatTicket(self, groupMid):
        METHOD_NAME = "reissueChatTicket"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes("reissueChatTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(groupMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def findChatByTicket(self, ticketId):
        METHOD_NAME = "findChatByTicket"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 16, 102, 105, 110, 100, 67, 104, 97, 116,
            66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0
        ]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 1] + self.getStringBytes(ticketId)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def acceptChatInvitationByTicket(self, to, ticket):
        METHOD_NAME = "acceptChatInvitationByTicket"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 28, 97, 99, 99, 101, 112, 116, 67, 104, 97,
            116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 66, 121, 84,
            105, 99, 107, 101, 116, 0, 0, 0, 0
        ]
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
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")
        return _d

    def updateChat(self, chatMid, chatSet, updatedAttribute=1):
        METHOD_NAME = "updateChat"
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
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 10, 117, 112, 100, 97, 116, 101, 67, 104,
            97, 116, 0, 0, 0, 0
        ]
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateChatName(self, chatMid, name):
        return self.updateChat(chatMid, {6: name}, 1)

    def updateChatPreventedUrl(self, chatMid, bool):
        return self.updateChat(chatMid, {8: {2: bool}}, 4)

    def getGroupIdsJoined(self):
        raise NotImplementedError(
            "getGroupIdsJoined is too old, please use getAllChatMids")
        METHOD_NAME = "getGroupIdsJoined"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 71, 114, 111, 117, 112,
            73, 100, 115, 74, 111, 105, 110, 101, 100, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getGroupIdsInvited(self):
        raise NotImplementedError(
            "getGroupIdsInvited is too old, please use getAllChatMids")
        METHOD_NAME = "getGroupIdsInvited"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 18, 103, 101, 116, 71, 114, 111, 117, 112,
            73, 100, 115, 73, 110, 118, 105, 116, 101, 100, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAllContactIds(self):
        METHOD_NAME = "getAllContactIds"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 65, 108, 108, 67, 111,
            110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getBlockedContactIds(self):
        METHOD_NAME = "getBlockedContactIds"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 66, 108, 111, 99, 107,
            101, 100, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0,
            0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getBlockedRecommendationIds(self):
        METHOD_NAME = "getBlockedRecommendationIds"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 27, 103, 101, 116, 66, 108, 111, 99, 107,
            101, 100, 82, 101, 99, 111, 109, 109, 101, 110, 100, 97, 116, 105,
            111, 110, 73, 100, 115, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAllReadMessageOps(self):
        METHOD_NAME = "getAllReadMessageOps"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79,
            112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def sendPostback(self, messageId, url, chatMID, originMID):
        METHOD_NAME = "sendPostback"
        """
        :url: linepostback://postback?_data=
        """
        params = [
            [
                12, 2,
                [[11, 1, messageId], [11, 2, url], [11, 3, chatMID],
                 [11, 4, originMID]]
            ],
        ]
        sqrd = self.generateDummyProtocol('sendPostback', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getPreviousMessagesV2WithRequest(self,
                                         messageBoxId: str,
                                         deliveredTime: int,
                                         messageId: int,
                                         messagesCount=200,
                                         withReadCount=False,
                                         receivedOnly=False):
        METHOD_NAME = "getPreviousMessagesV2WithRequest"
        params = [[
            12, 2,
            [[11, 1, messageBoxId],
             [12, 2, [
                 [10, 1, deliveredTime],
                 [10, 1, messageId],
             ]], [8, 3, messagesCount], [2, 4, withReadCount],
             [2, 5, receivedOnly]]
        ], [8, 3, 3]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 3)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getMessageBoxes(self,
                        minChatId=0,
                        maxChatId=0,
                        activeOnly=0,
                        messageBoxCountLimit=0,
                        withUnreadCount=False,
                        lastMessagesPerMessageBoxCount=False,
                        unreadOnly=False):
        METHOD_NAME = "getMessageBoxes"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 77, 101, 115, 115, 97,
            103, 101, 66, 111, 120, 101, 115, 0, 0, 0, 0
        ]
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        METHOD_NAME = "getChatRoomAnnouncementsBulk"
        params = [[15, 2, [11, chatRoomMids]], [8, 3, 0]]
        sqrd = self.generateDummyProtocol('getChatRoomAnnouncementsBulk',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getChatRoomAnnouncements(self, chatRoomMid):
        METHOD_NAME = "getChatRoomAnnouncements"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getChatRoomAnnouncements') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        METHOD_NAME = "removeChatRoomAnnouncement"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 26, 114, 101, 109, 111, 118, 101, 67, 104,
            97, 116, 82, 111, 111, 109, 65, 110, 110, 111, 117, 110, 99, 101,
            109, 101, 110, 116, 0, 0, 0, 0
        ]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, len(chatRoomMid)]
        for value in chatRoomMid:
            sqrd.append(ord(value))
        sqrd += [10, 0, 3] + self.getIntBytes(int(announcementSeq), 8)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def createChatRoomAnnouncement(self,
                                   chatRoomMid,
                                   text,
                                   link='',
                                   thumbnail='',
                                   type=0,
                                   displayFields=5,
                                   contentMetadata=None):
        METHOD_NAME = "createChatRoomAnnouncement"
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def leaveRoom(self, roomIds):
        METHOD_NAME = "leaveRoom"
        sqrd = [128, 1, 0, 1] + self.getStringBytes('leaveRoom') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(roomIds)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRoomsV2(self, roomIds):
        METHOD_NAME = "getRoomsV2"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getRoomsV2') + [0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(roomIds)]
        for mid in roomIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def createRoomV2(self, contactIds):
        METHOD_NAME = "createRoomV2"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('createRoomV2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(contactIds)]
        for mid in contactIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getCountries(self, countryGroup=1):
        METHOD_NAME = "getCountries"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getCountries') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(countryGroup)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def acquireEncryptedAccessToken(self, featureType=2):
        METHOD_NAME = "acquireEncryptedAccessToken"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('acquireEncryptedAccessToken') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(featureType)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def blockContact(self, mid):
        METHOD_NAME = "blockContact"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('blockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def unblockContact(self, mid):
        METHOD_NAME = "unblockContact"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('unblockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getLastOpRevision(self):
        METHOD_NAME = "getLastOpRevision"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79,
            112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getServerTime(self):
        METHOD_NAME = "getServerTime"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 83, 101, 114, 118, 101,
            114, 84, 105, 109, 101, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getConfigurations(self):
        METHOD_NAME = "getConfigurations"
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 67, 111, 110, 102, 105,
            103, 117, 114, 97, 116, 105, 111, 110, 115, 0, 0, 0, 0, 0
        ]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def fetchOps(self, revision, count=100):
        METHOD_NAME = "fetchOps"
        params = [[10, 2, revision], [8, 3, count], [10, 4, self.globalRev],
                  [10, 5, self.individualRev]]
        sqrd = self.generateDummyProtocol('fetchOps', params, 4)
        hr = self.server.additionalHeaders(
            self.server.Headers,
            {
                # "x-lst": "110000",
                "x-las": "F",  # or "B" if background
                "x-lam": "w",  # or "m"
                "x-lac": "46692"  # carrier
            })
        try:
            data = self.postPackDataAndGetUnpackRespData(
                "/P5",
                sqrd,
                5,
                encType=0,
                headers=hr,
                readWith=f"TalkService.{METHOD_NAME}",
                timeout=110)
            if data is None:
                return []
            if 'error' not in data:
                for op in data:
                    if self.checkAndGetValue(op, 'type', 'val_3', 3) == 0:
                        param1 = self.checkAndGetValue(op, 'param1', 'val_10',
                                                       10)
                        param2 = self.checkAndGetValue(op, 'param2', 'val_11',
                                                       11)
                        if param1 is not None:
                            a = param1.split('\x1e')
                            self.individualRev = a[0]
                            self.log(f"individualRev: {self.individualRev}",
                                     True)
                        if param2 is not None:
                            b = param2.split('\x1e')
                            self.globalRev = b[0]
                            self.log(f"globalRev: {self.globalRev}", True)
                return data
            else:
                raise Exception(data['error'])
        except httpx.ReadTimeout:
            pass
        return []

    def fetchOpsOld(self, revision, count=100):
        METHOD_NAME = "fetchOps"
        _headers = {'X-Line-Access': self.authToken, 'x-lpqs': "/P3"}
        a = self.encHeaders(_headers)
        sqrd = [
            128, 1, 0, 1, 0, 0, 0, 8, 102, 101, 116, 99, 104, 79, 112, 115, 0,
            0, 0, 0
        ]
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
            res = self.testPollConn.post("https://gf.line.naver.jp/enc",
                                         data=data,
                                         headers=hr,
                                         timeout=180)
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
        METHOD_NAME = "fetchOperations"
        params = [
            [10, 2, localRev],
            [8, 3, count],
        ]
        sqrd = self.generateDummyProtocol('fetchOperations', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S4", sqrd, 4, readWith=f"TalkService.{METHOD_NAME}")

    def sendEchoPush(self, text):
        METHOD_NAME = "sendEchoPush"
        # for long poll? check conn is alive
        # text: 1614384862517 = time
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('sendEchoPush') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRepairElements(self,
                          profile: bool = True,
                          settings: bool = False,
                          syncReason: int = 5):
        METHOD_NAME = "getRepairElements"
        params = [[
            12, 1, [
                [2, 1, profile],
                [2, 2, settings],
                [8, 11, syncReason],
            ]
        ]]
        sqrd = self.generateDummyProtocol('getRepairElements', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT,
                                                     sqrd, 4)

    def getSettingsAttributes2(self, attributesToRetrieve: list):
        METHOD_NAME = "getSettingsAttributes2"
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
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateSettingsAttributes2(self, settings: dict,
                                  attributesToUpdate: list):
        METHOD_NAME = "updateSettingsAttributes2"
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
                    f"[updateSettingsAttributes2] not support type {svt} (id: {sk})"
                )
        sqrd += [0]
        sqrd += [14, 0, 4, 8, 0, 0, 0, len(attributesToUpdate)]
        for value in attributesToUpdate:
            sqrd += self.getIntBytes(value)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def rejectChatInvitation(self, chatMid):
        METHOD_NAME = "rejectChatInvitation"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('rejectChatInvitation') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0)  # reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NORMAL_ENDPOINT,
            sqrd,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateProfileAttribute(self, attr: int, value: str):
        METHOD_NAME = "updateProfileAttribute"
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
        params = [[8, 1, 0], [8, 2, attr], [11, 3, value]]
        sqrd = self.generateDummyProtocol('updateProfileAttribute', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getE2EEPublicKey(self, mid, keyVersion, keyId):
        METHOD_NAME = "getE2EEPublicKey"
        params = [[11, 2, mid], [8, 3, keyVersion], [8, 4, keyId]]
        sqrd = self.generateDummyProtocol('getE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getE2EEPublicKeys(self):
        METHOD_NAME = "getE2EEPublicKeys"
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getE2EEPublicKeysEx(self, ignoreE2EEStatus: int):
        METHOD_NAME = "getE2EEPublicKeysEx"
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeysEx', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def removeE2EEPublicKey(self, spec, keyId, keyData):
        METHOD_NAME = "removeE2EEPublicKey"
        params = [[12, 2, [[8, 1, spec], [8, 2, keyId], [11, 4, keyData]]]]
        sqrd = self.generateDummyProtocol('removeE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def registerE2EEPublicKey(self, version: int, keyId: int, keyData: str,
                              time: int):
        METHOD_NAME = "registerE2EEPublicKey"
        params = [[
            12, 2,
            [
                [8, 1, version],
                [8, 2, keyId],
                [11, 4, keyData],
                [10, 5, time],
            ]
        ]]
        sqrd = self.generateDummyProtocol('registerE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def registerE2EEGroupKey(self, keyVersion: int, chatMid: str,
                             members: list, keyIds: list,
                             encryptedSharedKeys: list):
        METHOD_NAME = "registerE2EEGroupKey"
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
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getE2EEGroupSharedKey(self, keyVersion: int, chatMid: str,
                              groupKeyId: int):
        METHOD_NAME = "getE2EEGroupSharedKey"
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [8, 4, groupKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEGroupSharedKey', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getLastE2EEGroupSharedKey(self, keyVersion: int, chatMid: str):
        METHOD_NAME = "getLastE2EEGroupSharedKey"
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getLastE2EEGroupSharedKey', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getLastE2EEPublicKeys(self, chatMid: str):
        METHOD_NAME = "getLastE2EEPublicKeys"
        params = [
            [11, 2, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getLastE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def requestE2EEKeyExchange(self, temporalPublicKey: str, keyVersion: int,
                               keyId: int, verifier: str):
        METHOD_NAME = "requestE2EEKeyExchange"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, temporalPublicKey],
            [12, 3, [[8, 1, keyVersion], [8, 2, keyId]]],
            [11, 4, verifier]
        ]
        sqrd = self.generateDummyProtocol('requestE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def respondE2EEKeyExchange(self, encryptedKeyChain: str,
                               hashKeyChain: str):
        METHOD_NAME = "respondE2EEKeyExchange"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, encryptedKeyChain],
            [11, 3, hashKeyChain]
        ]
        sqrd = self.generateDummyProtocol('respondE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def negotiateE2EEPublicKey(self, mid: str):
        METHOD_NAME = "negotiateE2EEPublicKey"
        params = [
            [11, 2, mid],
        ]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def react(self, messageId, reactionType=5):
        METHOD_NAME = "react"
        params = [[
            12, 1,
            [[8, 1, 0], [10, 2, messageId], [12, 3, [[8, 1, reactionType]]]]
        ]]
        sqrd = self.generateDummyProtocol('react', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def createChat(self, name, targetUserMids, type=0, picturePath=None):
        METHOD_NAME = "createChat"
        params = [[
            12, 1,
            [[8, 1, 0], [8, 2, type], [11, 3, name],
             [14, 4, [11, targetUserMids]], [11, 5, picturePath]]
        ]]
        sqrd = self.generateDummyProtocol('createChat', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def updateRegion(self, region='TW'):
        raise Exception("updateRegion is not implemented")
        params = [[11, 4, region]]
        sqrd = self.generateDummyProtocol('updateRegion', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getChatExistence(self, ids):
        METHOD_NAME = "getChatExistence"
        params = [[12, 2, [
            [14, 1, [11, ids]],
        ]]]
        sqrd = self.generateDummyProtocol('getChatExistence', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getChatMembership(self, chatIds):
        METHOD_NAME = "getChatMembership"
        params = [[12, 2, [[14, 1, [11, chatIds]]]]]
        sqrd = self.generateDummyProtocol('getChatMembership', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def setChatHiddenStatus(self, chatId, bF=False):
        raise Exception("setChatHiddenStatus is not implemented")
        params = [[12, 1, [[11, 2, chatId]]]]
        sqrd = self.generateDummyProtocol('setChatHiddenStatus', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getReadMessageOps(self, chatId):
        METHOD_NAME = "getReadMessageOps"
        params = [[11, 2, chatId]]
        sqrd = self.generateDummyProtocol('getReadMessageOps', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getReadMessageOpsInBulk(self, chatIds):
        METHOD_NAME = "getReadMessageOpsInBulk"
        params = [[15, 2, [11, chatIds]]]
        sqrd = self.generateDummyProtocol('getReadMessageOpsInBulk', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getE2EEMessageInfo(self, mid, msgid, receiverKeyId):
        METHOD_NAME = "getE2EEMessageInfo"
        params = [
            [11, 2, mid],
            [11, 3, msgid],
            [8, 4, receiverKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEMessageInfo', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getMessageBoxCompactWrapUpList(self):
        raise Exception("getMessageBoxCompactWrapUpList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol('getMessageBoxCompactWrapUpList',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getRecentMessages(self, to):
        """ old func? still return 0 """
        METHOD_NAME = "getRecentMessages"
        params = [[11, 2, to], [8, 3, 101]]
        sqrd = self.generateDummyProtocol('getRecentMessages', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getRecentMessagesV2(self, to: str, count: int = 300):
        METHOD_NAME = "getRecentMessagesV2"
        params = [[11, 2, to], [8, 3, count]]
        sqrd = self.generateDummyProtocol('getRecentMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getPreviousMessageIds(self, to, count=100):
        METHOD_NAME = "getPreviousMessageIds"
        params = [[12, 2, [
            [11, 1, to],
            [8, 4, count],
        ]]]
        sqrd = self.generateDummyProtocol('getPreviousMessageIds', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getMessagesByIds(self, msgIds=[]):
        # messagesByIdsRequests
        # - messagesByIdsRequest
        # {1: 1626172142246, 2: 14386851950042}
        raise Exception("getMessagesByIds is not implemented")
        params = [[15, 2, [12, []]]]
        sqrd = self.generateDummyProtocol('getMessagesByIds', params, 3)
        return self.postPackDataAndGetUnpackRespData("/S3", sqrd, 3)

    def getMessageBoxesByIds(self, mids=[]):
        METHOD_NAME = "getMessageBoxesByIds"
        params = [[12, 2, [[15, 1, [11, mids]]]]]
        sqrd = self.generateDummyProtocol('getMessageBoxesByIds', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getMessageBoxCompactWrapUpListV2(self, start=0, end=1):
        METHOD_NAME = "getMessageBoxCompactWrapUpListV2"
        params = [[8, 2, start], [8, 3, end]]
        sqrd = self.generateDummyProtocol('getMessageBoxCompactWrapUpListV2',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getPreviousMessagesV2(self, mid, time, id, count=3000):
        METHOD_NAME = "getPreviousMessagesV2"
        params = [[11, 2, mid], [12, 3, [[10, 1, time], [10, 2, id]]],
                  [8, 4, count]]
        sqrd = self.generateDummyProtocol('getPreviousMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getPreviousMessagesV2WithReadCount(self, mid, time, id, count=101):
        METHOD_NAME = "getPreviousMessagesV2WithReadCount"
        params = [[11, 2, mid], [12, 3, [[10, 1, time], [10, 2, id]]],
                  [8, 4, count]]
        sqrd = self.generateDummyProtocol('getPreviousMessagesV2WithReadCount',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getNextMessagesV2(self, mid, time, id):
        METHOD_NAME = "getNextMessagesV2"
        params = [
            [11, 2, mid],
            [12, 3, [[10, 1, time], [10, 2, id]]],
            [8, 4, 101]  # count, 101 is max? maybe, hehe...
        ]
        sqrd = self.generateDummyProtocol('getNextMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getAllRoomIds(self):
        METHOD_NAME = "getAllRoomIds"
        params = []
        sqrd = self.generateDummyProtocol('getAllRoomIds', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getCompactRooms(self, roomIds):
        METHOD_NAME = "getCompactRooms"
        params = [[15, 2, [11, roomIds]]]
        sqrd = self.generateDummyProtocol('getCompactRooms', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def acquireCallTicket(self, to):
        METHOD_NAME = "acquireCallTicket"
        params = [[11, 1, to]]
        sqrd = self.generateDummyProtocol('acquireCallTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def isAbusive(self):
        """ idk """
        METHOD_NAME = "isAbusive"
        # 2021/09/16 it removed...
        params = [
            [8, 1, 0],
            [8, 2, 1],  # reportSource
        ]
        sqrd = self.generateDummyProtocol('isAbusive', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def removeBuddySubscriptionAndNotifyBuddyUnregistered(self, contactMids):
        """ OA only """
        METHOD_NAME = "removeBuddySubscriptionAndNotifyBuddyUnregistered"
        params = [[15, 1, [11, contactMids]]]
        sqrd = self.generateDummyProtocol(
            'removeBuddySubscriptionAndNotifyBuddyUnregistered', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def makeUserAddMyselfAsContact(self, contactMids):
        """ OA only """
        METHOD_NAME = "makeUserAddMyselfAsContact"
        params = [[15, 1, [11, contactMids]]]
        sqrd = self.generateDummyProtocol('makeUserAddMyselfAsContact', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getFollowers(self, mid=None, eMid=None, cursor=None):
        METHOD_NAME = "getFollowers"
        data = [11, 1, mid]
        if eMid is not None:
            data = [11, 2, eMid]
        params = [[12, 2, [[12, 1, [data]], [11, 2, cursor]]]]
        sqrd = self.generateDummyProtocol('getFollowers', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getFollowings(self, mid=None, eMid=None, cursor=None):
        METHOD_NAME = "getFollowings"
        params = [[
            12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]], [11, 2, cursor]]
        ]]
        sqrd = self.generateDummyProtocol('getFollowings', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def removeFollower(self, mid=None, eMid=None):
        METHOD_NAME = "removeFollower"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        sqrd = self.generateDummyProtocol('removeFollower', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def follow(self, mid=None, eMid=None):
        METHOD_NAME = "follow"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        sqrd = self.generateDummyProtocol('follow', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def unfollow(self, mid=None, eMid=None):
        METHOD_NAME = "unfollow"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        sqrd = self.generateDummyProtocol('unfollow', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def bulkFollow(self, contactMids):
        """ disallow """
        METHOD_NAME = "bulkFollow"
        params = [[12, 2, [[15, 2, [11, contactMids]]]]]
        sqrd = self.generateDummyProtocol('bulkFollow', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def decryptFollowEMid(self, eMid):
        METHOD_NAME = "decryptFollowEMid"
        params = [[11, 2, eMid]]
        sqrd = self.generateDummyProtocol('decryptFollowEMid', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getMessageReadRange(self, chatIds):
        METHOD_NAME = "getMessageReadRange"
        params = [[15, 2, [11, chatIds]]]
        sqrd = self.generateDummyProtocol('getMessageReadRange', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getChatRoomBGMs(self, chatIds: list):
        METHOD_NAME = "getChatRoomBGMs"
        params = [[14, 2, [11, chatIds]]]
        sqrd = self.generateDummyProtocol('getChatRoomBGMs', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            "/S5", sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def updateChatRoomBGM(self, chatId: str, chatRoomBGMInfo: str):
        METHOD_NAME = "updateChatRoomBGM"
        params = [[8, 1, self.getCurrReqId()], [11, 2, chatId],
                  [11, 3, chatRoomBGMInfo]]
        sqrd = self.generateDummyProtocol('updateChatRoomBGM', params, 4)

    def addSnsId(self, snsAccessToken):
        METHOD_NAME = "addSnsId"
        params = [
            [8, 2, 1],  # FB?
            [11, 3, snsAccessToken],
        ]
        sqrd = self.generateDummyProtocol('addSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def removeSnsId(self):
        METHOD_NAME = "removeSnsId"
        params = [
            [8, 2, 1],  # FB?
        ]
        sqrd = self.generateDummyProtocol('removeSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getContactRegistration(self, mid, type=0):
        METHOD_NAME = "getContactRegistration"
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
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getHiddenContactMids(self):
        METHOD_NAME = "getHiddenContactMids"
        params = []
        sqrd = self.generateDummyProtocol('getHiddenContactMids', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def blockRecommendation(self, mid):
        METHOD_NAME = "blockRecommendation"
        params = [[11, 2, mid]]
        sqrd = self.generateDummyProtocol('blockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def unblockRecommendation(self, mid):
        METHOD_NAME = "unblockRecommendation"
        params = [[11, 2, mid]]
        sqrd = self.generateDummyProtocol('unblockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getRecommendationIds(self):
        METHOD_NAME = "getRecommendationIds"
        params = []
        sqrd = self.generateDummyProtocol('getRecommendationIds', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getBlockedRecommendationIds(self):
        METHOD_NAME = "getBlockedRecommendationIds"
        params = []
        sqrd = self.generateDummyProtocol('getBlockedRecommendationIds',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def sync(self,
             revision: int,
             count: int = 100,
             fullSyncRequestReason: int = None,
             lastPartialFullSyncs: dict = None):
        """ 
        fetchOps for IOS 

        - fullSyncRequestReason:
            OTHER(0),
            INITIALIZATION(1),
            PERIODIC_SYNC(2),
            MANUAL_SYNC(3),
            LOCAL_DB_CORRUPTED(4);

        """
        METHOD_NAME = "sync"
        # 2021/7/26 it blocked, but 2021/7/20 it working
        # LINE are u here?
        # OH, just work for IOS, but 2021/07/20 it works with ANDROID :)
        # 2022/04/20, sync() added to ANDROID apk
        isDebugOnly = True
        self.log(f"Using sync() for {self.DEVICE_TYPE}...", isDebugOnly)
        self.log(f"globalRev: {self.globalRev}", isDebugOnly)
        self.log(f"individualRev: {self.individualRev}", isDebugOnly)
        params = [[
            12, 1,
            [[10, 1, revision], [8, 2, count], [10, 3, self.globalRev],
             [10, 4, self.individualRev], [8, 5, fullSyncRequestReason],
             [13, 6, [8, 10, lastPartialFullSyncs]]]
        ]]
        sqrd = self.generateDummyProtocol('sync', params, 4)
        res = self.postPackDataAndGetUnpackRespData(
            '/SYNC5',
            sqrd,
            5,
            0,
            readWith=f"SyncService.{METHOD_NAME}",
            timeout=180)
        if res is None:
            return []
        operationResponse = self.checkAndGetValue(res, 'operationResponse', 1)
        fullSyncResponse = self.checkAndGetValue(res, 'fullSyncResponse', 2)
        partialFullSyncResponse = self.checkAndGetValue(
            res, 'partialFullSyncResponse', 2)
        self.log(f"Resp: {res}", isDebugOnly)
        if operationResponse is not None:
            ops = self.checkAndGetValue(operationResponse, 'operations', 1)
            hasMoreOps = self.checkAndGetValue(operationResponse, 'hasMoreOps',
                                               2)
            globalEvents = self.checkAndGetValue(operationResponse,
                                                 'globalEvents', 3)
            individualEvents = self.checkAndGetValue(operationResponse,
                                                     'individualEvents', 4)
            if globalEvents is not None:
                events = self.checkAndGetValue(globalEvents, 'events', 1)
                lastRevision = self.checkAndGetValue(globalEvents,
                                                     'lastRevision', 2)
                self.globalRev = lastRevision
                self.log(f"new globalRev: {self.globalRev}", isDebugOnly)
                self.log(f"globalEvents: {events}", isDebugOnly)

            if individualEvents is not None:
                events = self.checkAndGetValue(individualEvents, 'events', 1)
                lastRevision = self.checkAndGetValue(individualEvents,
                                                     'lastRevision', 2)
                self.individualRev = lastRevision
                self.log(f"new individualRev: {self.individualRev}",
                         isDebugOnly)
                self.log(f"individualEvents: {events}", isDebugOnly)
            self.log(f"operations: {ops}", isDebugOnly)
            return ops
        elif fullSyncResponse is not None:
            # revision - 1 for sync revision on next req
            reasons = self.checkAndGetValue(fullSyncResponse, 'reasons', 1)
            syncRevision = self.checkAndGetValue(fullSyncResponse,
                                                 'nextRevision', 2)
            self.log(f"[ sync ] got fullSyncResponse: {reasons}")
            return self.sync(syncRevision - 1, count)
        else:
            raise EOFError(f"sync failed, unknown response: {res}")

    def updateChatRoomAnnouncement(self, gid: str, announcementId: int,
                                   messageLink: str, text: str, imgLink: str):
        METHOD_NAME = "updateChatRoomAnnouncement"
        params = [
            [11, 2, gid],
            [10, 3, announcementId],
            [
                12, 4,
                [[8, 1, 5], [11, 2, text], [11, 3, messageLink],
                 [11, 4, imgLink]]
            ],
        ]
        sqrd = self.generateDummyProtocol('updateChatRoomAnnouncement', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def reissueTrackingTicket(self):
        METHOD_NAME = "reissueTrackingTicket"
        params = []
        sqrd = self.generateDummyProtocol('reissueTrackingTicket', params, 4)

    def getExtendedProfile(self, syncReason=7):
        METHOD_NAME = "getExtendedProfile"
        params = [[8, 1, syncReason]]
        sqrd = self.generateDummyProtocol('getExtendedProfile', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def updateExtendedProfileAttribute(self, year: str,
                                       yearPrivacyLevelType: int,
                                       yearEnabled: bool, day: str,
                                       dayPrivacyLevelType: int,
                                       dayEnabled: bool):
        """
        - PrivacyLevelType
            PUBLIC(0),
            PRIVATE(1);
        """
        METHOD_NAME = "updateExtendedProfileAttribute"
        params = [
            [8, 1, self.getCurrReqId()],
            [8, 2, 0],  # attr
            [
                12, 3,
                [[
                    12, 1,
                    [
                        [11, 1, year],
                        [8, 2, yearPrivacyLevelType],
                        [2, 3, yearEnabled],
                        [11, 5, day],
                        [8, 6, dayPrivacyLevelType],
                        [2, 7, dayEnabled],
                    ]
                ]]
            ]
        ]
        sqrd = self.generateDummyProtocol('updateExtendedProfileAttribute',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def setNotificationsEnabled(self,
                                type: int,
                                target: str,
                                enablement: bool = True):
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
        METHOD_NAME = "setNotificationsEnabled"
        params = [
            [8, 1, self.getCurrReqId()],
            [8, 2, type],  # attr
            [11, 3, target],
            [2, 4, enablement]
        ]
        sqrd = self.generateDummyProtocol('setNotificationsEnabled', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findAndAddContactsByPhone(
            self,
            phones: list,
            reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        METHOD_NAME = "findAndAddContactsByPhone"
        if type(phones) != list:
            raise Exception(
                "[findAndAddContactsByPhone] phones must be a list")
        params = [
            [8, 1, self.getCurrReqId()],
            [14, 2, [11, phones]],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol('findAndAddContactsByPhone', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findAndAddContactsByUserid(
            self,
            searchId: str,
            reference: str = '{"screen":"friendAdd:idSearch","spec":"native"}'
    ):
        METHOD_NAME = "findAndAddContactsByUserid"
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol('findAndAddContactsByUserid', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def syncContacts(self,
                     phones: list = [],
                     emails: list = [],
                     userids: list = []):
        """
        - type
            ADD(0),
            REMOVE(1),
            MODIFY(2);

        ** NOTE: need turn on the 'allow_sync' setting.
        """
        METHOD_NAME = "syncContacts"
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
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getContactWithFriendRequestStatus(self, mid: str):
        METHOD_NAME = "getContactWithFriendRequestStatus"
        params = [[8, 1, self.getCurrReqId()], [11, 2, mid]]
        sqrd = self.generateDummyProtocol('getContactWithFriendRequestStatus',
                                          params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findContactsByPhone(self, phones: list):
        METHOD_NAME = "findContactsByPhone"
        if type(phones) != list:
            raise Exception("[findContactsByPhone] phones must be a list")
        params = [[14, 2, [11, phones]]]
        sqrd = self.generateDummyProtocol('findContactsByPhone', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findContactByUserid(self, searchId: str):
        METHOD_NAME = "findContactByUserid"
        params = [[11, 2, searchId]]
        sqrd = self.generateDummyProtocol('findContactByUserid', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findContactByMetaTag(
            self,
            searchId: str,
            reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        METHOD_NAME = "findContactByMetaTag"
        params = [[11, 2, searchId], [11, 3, reference]]
        sqrd = self.generateDummyProtocol('findContactByMetaTag', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findAndAddContactByMetaTag(
            self,
            searchId: str,
            reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        METHOD_NAME = "findAndAddContactByMetaTag"
        params = [[8, 1, self.getCurrReqId()], [11, 2, searchId],
                  [11, 3, reference]]
        sqrd = self.generateDummyProtocol('findAndAddContactByMetaTag', params,
                                          4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def updateContactSetting(self, mid: str, flag: int, value: str):
        """
        - flag
            CONTACT_SETTING_NOTIFICATION_DISABLE(1),
            CONTACT_SETTING_DISPLAY_NAME_OVERRIDE(2),
            CONTACT_SETTING_CONTACT_HIDE(4),
            CONTACT_SETTING_FAVORITE(8),
            CONTACT_SETTING_DELETE(16);
        """
        METHOD_NAME = "updateContactSetting"
        params = [[8, 1, self.getCurrReqId()], [11, 2, mid], [8, 3, flag],
                  [11, 4, value]]
        sqrd = self.generateDummyProtocol('updateContactSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def getFavoriteMids(self):
        METHOD_NAME = "getFavoriteMids"
        params = []
        sqrd = self.generateDummyProtocol('getFavoriteMids', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def sendMessageAwaitCommit(self):
        METHOD_NAME = "sendMessageAwaitCommit"
        params = []
        sqrd = self.generateDummyProtocol('sendMessageAwaitCommit', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def findContactByUserTicket(self, ticketIdWithTag: str):
        METHOD_NAME = "findContactByUserTicket"
        params = [[11, 2, ticketIdWithTag]]
        sqrd = self.generateDummyProtocol('findContactByUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def invalidateUserTicket(self):
        METHOD_NAME = "invalidateUserTicket"
        params = []
        sqrd = self.generateDummyProtocol('invalidateUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def unregisterUserAndDevice(self):
        METHOD_NAME = "unregisterUserAndDevice"
        params = []
        sqrd = self.generateDummyProtocol('unregisterUserAndDevice', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5', sqrd, 5, readWith=f"TalkService.{METHOD_NAME}")

    def verifyQrcode(self, verifier, pinCode):
        METHOD_NAME = "verifyQrcode"
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
        METHOD_NAME = "reportAbuseEx"
        if message is None and lineMeeting is None:
            raise Exception(
                "Should use reportAbuseExWithMessage() or reportAbuseExWithLineMeeting()"
            )
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

    def reportAbuseExWithMessage(self,
                                 reportSource: int,
                                 spammerReasons: int,
                                 messageIds: list,
                                 messages: list,
                                 senderMids: list,
                                 contentTypes: list,
                                 createdTimes: list,
                                 metadatas: list,
                                 metadata: dict,
                                 applicationType: int = 384):
        abuseMessages = []

        def _get(a, b, c):
            return a[b] if len(a) > b else c

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

    def reportAbuseExWithLineMeeting(self, reporteeMid: str,
                                     spammerReasons: int, spaceIds: list,
                                     objectIds: list, chatMid: str):
        evidenceIds = []

        def _get(a, b, c):
            return a[b] if len(a) > b else c

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
        METHOD_NAME = "getCountryWithRequestIp"
        params = []
        sqrd = self.generateDummyProtocol('getCountryWithRequestIp', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            '/S5',
            sqrd,
            5,
            readWith="TalkService.getCountryWithRequestIp_result")

    def notifyBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyBuddyOnAir is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("notifyBuddyOnAir", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getSuggestRevisions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestRevisions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSuggestRevisions", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateProfileAttributes(self,
                                profileAttribute: int,
                                value: str,
                                meta: dict = {}):
        # NO TEST
        # if u can check it, plz report on DC group
        METHOD_NAME = "updateProfileAttributes"
        params = [[8, 1, self.getCurrReqId()],
                  [
                      12, 2,
                      [[
                          13, 1,
                          [
                              8, 12,
                              [[
                                  8, 12, {
                                      profileAttribute: [
                                          [11, 1, value],
                                          [13, 2, [11, 11, meta]],
                                      ]
                                  }
                              ]]
                          ]
                      ]]
                  ]]
        sqrd = self.generateDummyProtocol("updateProfileAttributes", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateNotificationToken(self, token: str, type: int = 21):
        METHOD_NAME = "updateNotificationToken"
        params = [
            [11, 2, token],  # generated by google api
            [8, 3, type]
        ]
        sqrd = self.generateDummyProtocol("updateNotificationToken", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def disableNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("disableNearby is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("disableNearby", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def createRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("createRoom", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def tryFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("tryFriendRequest is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("tryFriendRequest", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def generateUserTicket(self, expirationTime: int, maxUseCount: int):
        METHOD_NAME = "generateUserTicket"
        params = [[10, 3, expirationTime], [8, 4, maxUseCount]]
        sqrd = self.generateDummyProtocol("generateUserTicket", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRecentFriendRequests(self):
        METHOD_NAME = "getRecentFriendRequests"
        params = []
        sqrd = self.generateDummyProtocol("getRecentFriendRequests", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateSettingsAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttribute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSettingsAttribute", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def resendPinCode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("resendPinCode", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def notifyRegistrationComplete(
        self,
        udidHash: str,
        applicationTypeWithExtensions: str = "ANDROID\t11.19.1\tAndroid OS\t7.0"
    ):
        METHOD_NAME = "notifyRegistrationComplete"
        params = [
            [11, 2, udidHash],  # len 32 hash
            [11, 3, applicationTypeWithExtensions],
        ]
        sqrd = self.generateDummyProtocol("notifyRegistrationComplete", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def createGroupV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroupV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("createGroupV2", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportSpam(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpam is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSpam", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def requestResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestResendMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("requestResendMessage", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def inviteFriendsBySms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteFriendsBySms is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("inviteFriendsBySms", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def findGroupByTicketV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicketV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("findGroupByTicketV2", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getInstantNews(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getInstantNews is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getInstantNews", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def createQrcodeBase64Image(self, url: str):
        METHOD_NAME = "createQrcodeBase64Image"
        params = [[11, 2, url]]
        sqrd = self.generateDummyProtocol("createQrcodeBase64Image", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def findSnsIdUserStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSnsIdUserStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("findSnsIdUserStatus", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getPendingAgreements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPendingAgreements is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getPendingAgreements", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyIdentityCredentialWithResult(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "verifyIdentityCredentialWithResult is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyIdentityCredentialWithResult",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerWithSnsId(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithSnsId is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("registerWithSnsId", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyAccountMigration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigration is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyAccountMigration", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getEncryptedIdentityV3(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getEncryptedIdentityV3 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getEncryptedIdentityV3", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reissueGroupTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueGroupTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reissueGroupTicket", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUserTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getUserTicket", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def changeVerificationMethod(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("changeVerificationMethod is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("changeVerificationMethod", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRooms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRooms is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getRooms", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAcceptedProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAcceptedProximityMatches is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getAcceptedProximityMatches",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getChatEffectMetaList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChatEffectMetaList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getChatEffectMetaList", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def notifyInstalled(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyInstalled is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("notifyInstalled", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reissueUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueUserTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reissueUserTicket", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def sendDummyPush(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("sendDummyPush is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("sendDummyPush", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyAccountMigrationPincode",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def acquireCallRoute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acquireCallRoute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("acquireCallRoute", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerDeviceWithoutPhoneNumberWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential is not implemented"
        )
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerDeviceWithoutPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDeviceWithoutPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("registerDeviceWithoutPhoneNumber",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def inviteIntoGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("inviteIntoGroup", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def removeAllMessages(self, lastMessageId: str):
        METHOD_NAME = "removeAllMessages"
        params = [[8, 1, self.getCurrReqId()], [11, 1, lastMessageId]]
        sqrd = self.generateDummyProtocol("removeAllMessages", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerWithPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("registerWithPhoneNumber", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRingbackTone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getRingbackTone", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportSpammer(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpammer is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSpammer", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def loginWithVerifierForCerificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCerificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("loginWithVerifierForCerificate",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def logoutSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logoutSession is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("logoutSession", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def clearIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("clearIdentityCredential", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateGroupPreferenceAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroupPreferenceAttribute is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateGroupPreferenceAttribute",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def closeProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("closeProximityMatch is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("closeProximityMatch", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def loginWithVerifierForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCertificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("loginWithVerifierForCertificate",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def respondResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("respondResendMessage is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("respondResendMessage", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getProximityMatchCandidateList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidateList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getProximityMatchCandidateList",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportDeviceState(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportDeviceState is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportDeviceState", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def sendChatRemoved(self, chatMid: str, lastMessageId: str):
        METHOD_NAME = "sendChatRemoved"
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, chatMid],
            [11, 3, lastMessageId],
            # [3, 4, sessionId]
        ]
        sqrd = self.generateDummyProtocol("sendChatRemoved", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAuthQrcode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAuthQrcode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getAuthQrcode", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateAccountMigrationPincode",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerWithSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithSnsIdAndIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithSnsIdAndIdentityCredential", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def startUpdateVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startUpdateVerification is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("startUpdateVerification", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def notifySleep(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifySleep is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("notifySleep", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportContacts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportContacts is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportContacts", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def acceptGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("acceptGroupInvitation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def loginWithVerifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifier is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("loginWithVerifier", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttributes is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateSettingsAttributes", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyPhoneNumberForLogin(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumberForLogin is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyPhoneNumberForLogin", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getUpdatedMessageBoxIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUpdatedMessageBoxIds is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getUpdatedMessageBoxIds", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def inviteIntoRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("inviteIntoRoom", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def removeFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeFriendRequest is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("removeFriendRequest", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def acceptGroupInvitationByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitationByTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("acceptGroupInvitationByTicket",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportProfile is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportProfile", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateProfile is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateProfile", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def createGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("createGroup", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def resendEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendEmailConfirmation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("resendEmailConfirmation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerWithPhoneNumberAndPassword(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithPhoneNumberAndPassword is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("registerWithPhoneNumberAndPassword",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def openProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("openProximityMatch is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("openProximityMatch", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyPhone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyPhone", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getSessions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSessions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSessions", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def clearRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearRingbackTone is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("clearRingbackTone", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def leaveGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("leaveGroup", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getProximityMatchCandidates(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidates is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getProximityMatchCandidates",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def createAccountMigrationPincodeSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "createAccountMigrationPincodeSession is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "createAccountMigrationPincodeSession", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getRoom", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def startVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startVerification is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("startVerification", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def logout(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logout is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("logout", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateNotificationTokenWithBytes(self,
                                         bData: bytes,
                                         bindType: int = 1):
        """
        2022/04/25
        """
        METHOD_NAME = "updateNotificationTokenWithBytes"
        params = [[11, 2, bData], [8, 3, bindType]]
        sqrd = self.generateDummyProtocol("updateNotificationTokenWithBytes",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def confirmEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("confirmEmail is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("confirmEmail", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getIdentityIdentifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getIdentityIdentifier is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getIdentityIdentifier", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateDeviceInfo(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateDeviceInfo is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateDeviceInfo", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerDeviceWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerDeviceWithIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "registerDeviceWithIdentityCredential", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def wakeUpLongPolling(self, clientRevision: int):
        METHOD_NAME = "wakeUpLongPolling"
        params = [[10, 2, clientRevision]]
        sqrd = self.generateDummyProtocol("wakeUpLongPolling", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateAndGetNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAndGetNearby is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateAndGetNearby", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSettingsAttributes is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSettingsAttributes", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def rejectGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("rejectGroupInvitation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def loginWithIdentityCredentialForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "loginWithIdentityCredentialForCertificate is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "loginWithIdentityCredentialForCertificate", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportSettings", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerWithExistingSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithExistingSnsIdAndIdentityCredential is not implemented"
        )
        params = []
        sqrd = self.generateDummyProtocol(
            "registerWithExistingSnsIdAndIdentityCredential", params,
            self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def requestAccountPasswordReset(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestAccountPasswordReset is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("requestAccountPasswordReset",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def requestEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestEmailConfirmation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("requestEmailConfirmation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def resendPinCodeBySMS(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCodeBySMS is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("resendPinCodeBySMS", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getSuggestIncrements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestIncrements is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSuggestIncrements", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def noop(self):
        METHOD_NAME = "noop"
        params = []
        sqrd = self.generateDummyProtocol("noop", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getSuggestSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getSuggestSettings", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def acceptProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptProximityMatches is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("acceptProximityMatches", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def kickoutFromGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("kickoutFromGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("kickoutFromGroup", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyIdentityCredential", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def loginWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("loginWithIdentityCredential",
                                          params, self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def setIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setIdentityCredential is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("setIdentityCredential", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getBuddyLocation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def verifyPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("verifyPhoneNumber", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerDevice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDevice is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("registerDevice", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getRingtone(self):
        METHOD_NAME = "getRingtone"
        params = []
        sqrd = self.generateDummyProtocol("getRingtone", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def findGroupByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicket is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("findGroupByTicket", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportClientStatistics(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportClientStatistics is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportClientStatistics", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def updateGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("updateGroup", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getEncryptedIdentityV2(self):
        METHOD_NAME = "getEncryptedIdentityV2"
        params = []
        sqrd = self.generateDummyProtocol("getEncryptedIdentityV2", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportAbuse(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportAbuse is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("reportAbuse", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getAnalyticsInfo(self):
        METHOD_NAME = "getAnalyticsInfo"
        params = []
        sqrd = self.generateDummyProtocol("getAnalyticsInfo", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getCompactGroups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactGroups is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getCompactGroups", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def setBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("setBuddyLocation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def isUseridAvailable(self, searchId: str):
        METHOD_NAME = "isUseridAvailable"
        params = [[11, 2, searchId]]
        sqrd = self.generateDummyProtocol("isUseridAvailable", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def removeBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeBuddyLocation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("removeBuddyLocation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def report(self, syncOpRevision: int, category: int, report: str):
        """
        - category:
            PROFILE(0),
        SETTINGS(1),
        OPS(2),
        CONTACT(3),
        RECOMMEND(4),
        BLOCK(5),
        GROUP(6),
        ROOM(7),
        NOTIFICATION(8),
        ADDRESS_BOOK(9);
        """
        METHOD_NAME = "report"
        params = [
            [10, 2, syncOpRevision],
            [8, 3, category],
            [11, 4, report],
        ]
        sqrd = self.generateDummyProtocol("report", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def registerUserid(self, searchId: str):
        METHOD_NAME = "registerUserid"
        params = [[8, 1, self.getCurrReqId()], [11, 2, searchId]]
        sqrd = self.generateDummyProtocol("registerUserid", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def finishUpdateVerification(self, sessionId: str):
        METHOD_NAME = "finishUpdateVerification"
        params = [[11, 2, sessionId]]
        sqrd = self.generateDummyProtocol("finishUpdateVerification", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def notifySleepV2(self, revision: int):
        """
        2022/04/25
        """
        METHOD_NAME = "notifySleepV2"
        params = [[
            2, 12,
            [[1, 12, [[10, 1, revision], [8, 2, 1]]],
             [2, 12, [
                 [8, 1, 0],
                 [8, 2, 0],
             ]]]
        ]]
        sqrd = self.generateDummyProtocol("notifySleepV2", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_NOTIFY_SLEEP_ENDPOINT,
            sqrd,
            4,
            readWith=f"TalkService.{METHOD_NAME}")

    def getCompactRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactRoom is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getCompactRoom", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def cancelGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("cancelGroupInvitation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("cancelGroupInvitation", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def clearRingtone(self, oid: str):
        METHOD_NAME = "clearRingtone"
        params = [[11, 1, oid]]
        sqrd = self.generateDummyProtocol("clearRingtone", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def notifyUpdated(self,
                      lastRev: int,
                      udidHash: str,
                      oldUdidHash: str,
                      deviceName: str = "DeachSword",
                      systemName: str = "Android OS",
                      systemVersion: str = "9.1",
                      model: str = "DeachSword",
                      webViewVersion: str = "96.0.4664.45",
                      carrierCode: int = 0,
                      carrierName: str = "",
                      applicationType: int = 32):
        METHOD_NAME = "notifyUpdated"
        params = [
            [10, 2, lastRev],
            [
                12,
                3,
                [
                    [11, 1, deviceName],  # DeachSword
                    [11, 2, systemName],  # Android OS
                    [11, 3, systemVersion],  # 9.1
                    [11, 4, model],  # DeachSword
                    [11, 5, webViewVersion],  # 96.0.4664.45
                    [8, 10, carrierCode],  # 0
                    [11, 10, carrierName],
                    [8, 20, applicationType],  # 32
                ]
            ],
            [11, 4, udidHash],  # 57f44905fd117a5661828440bb7d1bd5
            [11, 4, oldUdidHash],  # 5284047f4ffb4e04824a2fd1d1f0cd62
        ]
        sqrd = self.generateDummyProtocol("notifyUpdated", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getGroupWithoutMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getGroupWithoutMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getGroupWithoutMembers", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getShakeEventV1(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getShakeEventV1 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getShakeEventV1", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def reportPushRecvReports(self,
                              pushTrackingId: str,
                              recvTimestamp: int,
                              battery: int = 22,
                              batteryMode: int = 1,
                              clientNetworkType: int = 1,
                              carrierCode: str = "",
                              displayTimestamp: int = 0):
        METHOD_NAME = "reportPushRecvReports"
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
        params = [[8, 1, 0], [15, 2, [12, pushRecvReports]]]
        sqrd = self.generateDummyProtocol("reportPushRecvReports", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getFriendRequests(self, direction: int = 1, lastSeenSeqId: int = None):
        """
        -  direction:
            INCOMING(1),
            OUTGOING(2);
        """
        METHOD_NAME = "getFriendRequests"
        params = [[8, 1, direction], [10, 2, lastSeenSeqId]]
        sqrd = self.generateDummyProtocol("getFriendRequests", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def requestIdentityUnbind(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestIdentityUnbind is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("requestIdentityUnbind", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def addToFollowBlacklist(self, mid: str = None, eMid: str = None):
        METHOD_NAME = "addToFollowBlacklist"
        params = [[12, 2, [[12, 1, [
            [11, 1, mid],
            [11, 2, eMid],
        ]]]]]
        sqrd = self.generateDummyProtocol("addToFollowBlacklist", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def removeFromFollowBlacklist(self, mid: str = None, eMid: str = None):
        METHOD_NAME = "removeFromFollowBlacklist"
        params = [[12, 2, [[12, 1, [
            [11, 1, mid],
            [11, 2, eMid],
        ]]]]]
        sqrd = self.generateDummyProtocol("removeFromFollowBlacklist", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def getFollowBlacklist(self, cursor: str = None):
        METHOD_NAME = "getFollowBlacklist"
        params = [[12, 2, [[11, 1, cursor]]]]
        sqrd = self.generateDummyProtocol("getFollowBlacklist", params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"TalkService.{METHOD_NAME}")

    def determineMediaMessageFlow(self, chatMid: str):
        METHOD_NAME = "determineMediaMessageFlow"
        params = TalkServiceStruct.DetermineMediaMessageFlowRequest(chatMid)
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")

    def getPublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPublicKeychain is not implemented")
        METHOD_NAME = "getPublicKeychain"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendMessageReceipt(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageReceipt is not implemented")
        METHOD_NAME = "sendMessageReceipt"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def commitSendMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitSendMessages is not implemented")
        METHOD_NAME = "commitSendMessages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getNotificationPolicy(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getNotificationPolicy is not implemented")
        METHOD_NAME = "getNotificationPolicy"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendMessageToMyHome(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageToMyHome is not implemented")
        METHOD_NAME = "sendMessageToMyHome"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getWapInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getWapInvitation is not implemented")
        METHOD_NAME = "getWapInvitation"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getBuddySubscriberStates(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBuddySubscriberStates is not implemented")
        METHOD_NAME = "getBuddySubscriberStates"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def storeUpdateProfileAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("storeUpdateProfileAttribute is not implemented")
        METHOD_NAME = "storeUpdateProfileAttribute"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def notifyIndividualEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifyIndividualEvent is not implemented")
        METHOD_NAME = "notifyIndividualEvent"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def clearMessageBox(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("clearMessageBox is not implemented")
        METHOD_NAME = "clearMessageBox"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateCustomModeSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateCustomModeSettings is not implemented")
        METHOD_NAME = "updateCustomModeSettings"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateSettings is not implemented")
        METHOD_NAME = "updateSettings"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendMessageIgnored(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageIgnored is not implemented")
        METHOD_NAME = "sendMessageIgnored"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def findAndAddContactsByEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("findAndAddContactsByEmail is not implemented")
        METHOD_NAME = "findAndAddContactsByEmail"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxCompactWrapUp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxCompactWrapUp is not implemented")
        METHOD_NAME = "getMessageBoxCompactWrapUp"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getPreviousMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPreviousMessages is not implemented")
        METHOD_NAME = "getPreviousMessages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def commitUpdateProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitUpdateProfile is not implemented")
        METHOD_NAME = "commitUpdateProfile"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def registerBuddyUser(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerBuddyUser is not implemented")
        METHOD_NAME = "registerBuddyUser"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessagesBySequenceNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessagesBySequenceNumber is not implemented")
        METHOD_NAME = "getMessagesBySequenceNumber"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def commitSendMessagesToMid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitSendMessagesToMid is not implemented")
        METHOD_NAME = "commitSendMessagesToMid"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def isIdentityIdentifierAvailable(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("isIdentityIdentifierAvailable is not implemented")
        METHOD_NAME = "isIdentityIdentifierAvailable"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxList is not implemented")
        METHOD_NAME = "getMessageBoxList"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def registerWapDevice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerWapDevice is not implemented")
        METHOD_NAME = "registerWapDevice"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendContentReceipt(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendContentReceipt is not implemented")
        METHOD_NAME = "sendContentReceipt"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateC2DMRegistrationId(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateC2DMRegistrationId is not implemented")
        METHOD_NAME = "updateC2DMRegistrationId"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxListByStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxListByStatus is not implemented")
        METHOD_NAME = "getMessageBoxListByStatus"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def createSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("createSession is not implemented")
        METHOD_NAME = "createSession"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getOldReadMessageOpsWithRange(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getOldReadMessageOpsWithRange is not implemented")
        METHOD_NAME = "getOldReadMessageOpsWithRange"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def inviteViaEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("inviteViaEmail is not implemented")
        METHOD_NAME = "inviteViaEmail"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def reportRooms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reportRooms is not implemented")
        METHOD_NAME = "reportRooms"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def reportGroups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reportGroups is not implemented")
        METHOD_NAME = "reportGroups"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def removeMessageFromMyHome(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("removeMessageFromMyHome is not implemented")
        METHOD_NAME = "removeMessageFromMyHome"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxV2 is not implemented")
        METHOD_NAME = "getMessageBoxV2"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def destroyMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("destroyMessage is not implemented")
        METHOD_NAME = "destroyMessage"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getCompactContactsModifiedSince(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCompactContactsModifiedSince is not implemented")
        METHOD_NAME = "getCompactContactsModifiedSince"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def notifiedRedirect(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifiedRedirect is not implemented")
        METHOD_NAME = "notifiedRedirect"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateSettings2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateSettings2 is not implemented")
        METHOD_NAME = "updateSettings2"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def reissueDeviceCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reissueDeviceCredential is not implemented")
        METHOD_NAME = "reissueDeviceCredential"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def registerBuddyUserid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerBuddyUserid is not implemented")
        METHOD_NAME = "registerBuddyUserid"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBox(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBox is not implemented")
        METHOD_NAME = "getMessageBox"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxWrapUpListV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpListV2 is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpListV2"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def fetchAnnouncements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("fetchAnnouncements is not implemented")
        METHOD_NAME = "fetchAnnouncements"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendEvent is not implemented")
        METHOD_NAME = "sendEvent"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def syncContactBySnsIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("syncContactBySnsIds is not implemented")
        METHOD_NAME = "syncContactBySnsIds"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def validateContactsOnBot(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("validateContactsOnBot is not implemented")
        METHOD_NAME = "validateContactsOnBot"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def trySendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("trySendMessage is not implemented")
        METHOD_NAME = "trySendMessage"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getNextMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getNextMessages is not implemented")
        METHOD_NAME = "getNextMessages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updatePublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updatePublicKeychain is not implemented")
        METHOD_NAME = "updatePublicKeychain"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxWrapUpList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpList is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpList"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def removeMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("removeMessage is not implemented")
        METHOD_NAME = "removeMessage"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxWrapUp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUp is not implemented")
        METHOD_NAME = "getMessageBoxWrapUp"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def releaseSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("releaseSession is not implemented")
        METHOD_NAME = "releaseSession"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxWrapUpV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpV2 is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpV2"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getActiveBuddySubscriberIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getActiveBuddySubscriberIds is not implemented")
        METHOD_NAME = "getActiveBuddySubscriberIds"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getSystemConfiguration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getSystemConfiguration is not implemented")
        METHOD_NAME = "getSystemConfiguration"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def notifyUpdatePublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifyUpdatePublicKeychain is not implemented")
        METHOD_NAME = "notifyUpdatePublicKeychain"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getBlockedContactIdsByRange(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBlockedContactIdsByRange is not implemented")
        METHOD_NAME = "getBlockedContactIdsByRange"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getLastAnnouncementIndex(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getLastAnnouncementIndex is not implemented")
        METHOD_NAME = "getLastAnnouncementIndex"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getMessageBoxCompactWrapUpV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxCompactWrapUpV2 is not implemented")
        METHOD_NAME = "getMessageBoxCompactWrapUpV2"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def sendContentPreviewUpdated(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendContentPreviewUpdated is not implemented")
        METHOD_NAME = "sendContentPreviewUpdated"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getBuddyBlockerIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBuddyBlockerIds is not implemented")
        METHOD_NAME = "getBuddyBlockerIds"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateBuddySetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateBuddySetting is not implemented")
        METHOD_NAME = "updateBuddySetting"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def updateApnsDeviceToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateApnsDeviceToken is not implemented")
        METHOD_NAME = "updateApnsDeviceToken"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def findContactsByEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("findContactsByEmail is not implemented")
        METHOD_NAME = "findContactsByEmail"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def agreeToLabFeature(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("agreeToLabFeature is not implemented")
        METHOD_NAME = "agreeToLabFeature"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def toggleLabFeature(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("toggleLabFeature is not implemented")
        METHOD_NAME = "toggleLabFeature"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getSymmetricKey(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getSymmetricKey is not implemented")
        METHOD_NAME = "getSymmetricKey"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def getAgreedToLabFeatures(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getAgreedToLabFeatures is not implemented")
        METHOD_NAME = "getAgreedToLabFeatures"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.TalkService_API_PATH,
                                                     sqrd,
                                                     self.TalkService_RES_TYPE)

    def cancelReaction(self, messageId: int):
        """
        cancel message reaction by message id.

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 06/30/2022, 01:51:15
        """
        METHOD_NAME = "cancelReaction"
        params = TalkServiceStruct.CancelReactionRequest(messageId)
        sqrd = self.generateDummyProtocol(METHOD_NAME, params,
                                          self.TalkService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
            readWith=f"{__class__.__name__}.{METHOD_NAME}")


class TalkServiceStruct(object):

    @staticmethod
    def BaseRequest(request: list):
        return [[12, 1, request]]

    @staticmethod
    def CancelReactionRequest(messageId: int):
        return __class__.BaseRequest([[10, 2, messageId]])

    @staticmethod
    def DetermineMediaMessageFlowRequest(chatMid: str):
        return __class__.BaseRequest([[11, 1, chatMid]])
