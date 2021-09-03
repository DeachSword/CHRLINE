# -*- coding: utf-8 -*-
import time
import json
import requests
import httpx

class TalkService():
    url = "https://ga2.line.naver.jp/enc"
    
    def __init__(self):
        self.testPollConn = requests.session()

    def sendMessage(self, to, text, contentType=0, contentMetadata={}, relatedMessageId=None, location=None):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 115, 101, 110, 100, 77, 101, 115, 115, 97, 103, 101, 0, 0, 0, 0, 8, 0, 1]
        sqrd += self.getIntBytes(self.getCurrReqId())
        sqrd += [12, 0, 2, 11, 0, 1, 0, 0, 0, len(self.profile[1])]
        for value in self.profile[1]:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3]
        if to[0] == 'u':
            toType = 0
        elif to[0] == 'r':
            toType = 1
        elif to[0] == 'c':
            toType = 2
        else:
            raise Exception(f"未知的toType: {to[0]}")
        _toType = (toType).to_bytes(4, byteorder="big")
        for value in _toType:
            sqrd.append(value)
        sqrd += [11, 0, 4, 0, 0, 0, 0]
        sqrd += [10, 0, 5] + self.getIntBytes(int(time.time()), 8) # createTime
        if text is not None:
            text = str(text).encode()
            sqrd += [11, 0, 10] + self.getIntBytes(len(text))
            for value2 in text:
                sqrd.append(value2)
        sqrd += [2, 0, 14, 0] # hasContent
        sqrd += [8, 0, 15] + self.getIntBytes(contentType)
        if location  and type(location) == dict:
            sqrd += [12, 0, 11]
            sqrd += [11, 0, 1] + self.getStringBytes(location.get(1, 'CHRLINE API'))
            sqrd += [11, 0, 2] + self.getStringBytes(location.get(2, 'CHRLINE API'))
            sqrd += [4, 0, 3] + self.getFloatBytes(location.get(3, 0))
            sqrd += [4, 0, 4] + self.getFloatBytes(location.get(4, 0))
            sqrd += [8, 0, 7] + self.getIntBytes(location.get(7, 1))
            sqrd += [11, 0, 6] + self.getStringBytes(location.get(6, 'PC0'))
            sqrd += [0]
        if contentMetadata and type(contentMetadata) == dict:
            _keys = contentMetadata.copy().keys()
            sqrd += [13, 0, 18, 11, 11] + self.getIntBytes(len(_keys))# key and val must str
            for _k in _keys:
                _v = contentMetadata[_k]
                sqrd += self.getStringBytes(_k)
                sqrd += self.getStringBytes(_v)
        # [15, 0, 20] chunks
        if relatedMessageId is not None:
            sqrd += [11, 0, 21] + self.getStringBytes(relatedMessageId)
            sqrd += [8, 0, 22] + self.getIntBytes(3)
            sqrd += [8, 0, 24] + self.getIntBytes(1)
        # [8, 0, 25] appExtensionType
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def sendContact(self, to, mid):
        return self.sendMessage(to, None, contentType=13, contentMetadata={"mid": mid})
        
    def sendLocation(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, None, contentType=15, location=data)
        
    def sendLocationMessage(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, "test", location=data)
        
    def sendMessageWithChunks(self, to, chunk, contentType=0, contentMetadata={}):
        params = [
            [8, 1, self.getCurrReqId()],
            [12, 2, [
                [11, 1, self.mid],
                [11, 2, to],
                [8, 3, self.getToType(to)],
                [8, 15, contentType],
                [13, 18, [11, 11, contentMetadata]],
                [15, 20, [11, chunk]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('sendMessage', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def sendCompactMessage(self, to, text):
        sqrd = [2] # 5 if E2EE, 6 if E2EE location
        midType = to[0]
        if midType == 'u':
            sqrd.append(0)
        elif midType == 'r':
            sqrd.append(1)
        elif midType == 'c':
            sqrd.append(2)
        else:
            raise Exception(f"unknown midType: {midType}")
        sqrd += [134, 134, 3] # seq?
        sqrd += self.getMagicStringBytes(to[1:])
        sqrd += self.getStringBytes(text, isCompact=True)
        sqrd.append(2)
        return self.postPackDataAndGetUnpackRespData(self.LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT ,sqrd)
    
    def getEncryptedIdentity(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 69, 110, 99, 114, 121, 112, 116, 101, 100, 73, 100, 101, 110, 116, 105, 116, 121, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getProfile(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 80, 114, 111, 102, 105, 108, 101, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getSettings(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 83, 101, 116, 116, 105, 110, 103, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
    
    def sendChatChecked(self, chatMid, lastMessageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 115, 101, 110, 100, 67, 104, 97, 116, 67, 104, 101, 99, 107, 101, 100, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in chatMid:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(lastMessageId)]
        for value in lastMessageId:
            sqrd.append(ord(value))
        # [3, 0, 4] # sessionId
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def unsendMessage(self, messageId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 117, 110, 115, 101, 110, 100, 77, 101, 115, 115, 97, 103, 101, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getContact(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getContacts(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getContactsV2(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 115, 86, 50, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def findAndAddContactsByMid(self, mid, reference='{"screen":"groupMemberList","spec":"native"}'):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 23, 102, 105, 110, 100, 65, 110, 100, 65, 100, 100, 67, 111, 110, 116, 97, 99, 116, 115, 66, 121, 77, 105, 100, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        sqrd += [11, 0, 4] + self.getStringBytes(reference)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getGroup(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getGroups(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 9, 103, 101, 116, 71, 114, 111, 117, 112, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getGroupsV2(self, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 71, 114, 111, 117, 112, 115, 86, 50, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getChats(self, mids, withMembers=True, withInvitees=True):
        if type(mids) != list:
            raise Exception("[getChats] mids must be a list")
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 67, 104, 97, 116, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [2, 0, 2, int(withMembers)]
        sqrd += [2, 0, 3, int(withMembers)]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getAllChatMids(self, withMembers=True, withInvitees=True):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getAllChatMids') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [2, 0, 1, int(withMembers)]
        sqrd += [2, 0, 2, int(withInvitees)]
        sqrd += [0]
        sqrd += [8, 0, 2] + self.getIntBytes(7)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getCompactGroup(self, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 67, 111, 109, 112, 97, 99, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def deleteOtherFromChat(self, to, mid):
        if type(mid) == list:
            _lastReq = None
            for _mid in mid:
                print(f'[deleteOtherFromChat] The parameter \'mid\' should be str')
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 100, 101, 108, 101, 116, 101, 79, 116, 104, 101, 114, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0] # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def inviteIntoChat(self, to, mids):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 105, 110, 118, 105, 116, 101, 73, 110, 116, 111, 67, 104, 97, 116, 0, 0, 0, 0]
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def cancelChatInvitation(self, to, mid):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 99, 97, 110, 99, 101, 108, 67, 104, 97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0] # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [14, 0, 3, 11, 0, 0, 0, 1, 0, 0, 0, len(mid)]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def deleteSelfFromChat(self, to):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 100, 101, 108, 101, 116, 101, 83, 101, 108, 102, 70, 114, 111, 109, 67, 104, 97, 116, 0, 0, 0, 0]
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def acceptChatInvitation(self, to):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 97, 99, 99, 101, 112, 116, 67, 104, 97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(self.getCurrReqId())
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        _d = self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        #self.sendMessage(to, 'Powered by CHRLINE API')
        return _d
        
    def reissueChatTicket(self, groupMid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes("reissueChatTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(groupMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def findChatByTicket(self, ticketId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 102, 105, 110, 100, 67, 104, 97, 116, 66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 1] + self.getStringBytes(ticketId)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def acceptChatInvitationByTicket(self, to, ticket):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 28, 97, 99, 99, 101, 112, 116, 67, 104, 97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(ticket)]
        for value in ticket:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        _d = self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
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
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 117, 112, 100, 97, 116, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        if chatSet.get(1) is not None:
            sqrd += [8, 0, 1] + self.getIntBytes(chatSet[1])
        else:
            sqrd += [8, 0, 1, 0, 0, 0, 1] # type
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def updateChatName(self, chatMid, name):
        return self.updateChat(chatMid, {6: name}, 1)
        
    def updateChatPreventedUrl(self, chatMid, bool):
        return self.updateChat(chatMid, {8: {2: bool}}, 4)
    
    def getGroupIdsJoined(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 71, 114, 111, 117, 112, 73, 100, 115, 74, 111, 105, 110, 101, 100, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getGroupIdsInvited(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 103, 101, 116, 71, 114, 111, 117, 112, 73, 100, 115, 73, 110, 118, 105, 116, 101, 100, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getAllContactIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 65, 108, 108, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getBlockedContactIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 66, 108, 111, 99, 107, 101, 100, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getBlockedRecommendationIds(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 27, 103, 101, 116, 66, 108, 111, 99, 107, 101, 100, 82, 101, 99, 111, 109, 109, 101, 110, 100, 97, 116, 105, 111, 110, 73, 100, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getAllReadMessageOps(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
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
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getPreviousMessagesV2WithRequest(self, messageBoxId, endMessageId=0, messagesCount=200, withReadCount=0, receivedOnly=False):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 32, 103, 101, 116, 80, 114, 101, 118, 105, 111, 117, 115, 77, 101, 115, 115, 97, 103, 101, 115, 86, 50, 87, 105, 116, 104, 82, 101, 113, 117, 101, 115, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1, 0, 0, 0, len(messageBoxId)]
        for value in messageBoxId:
            sqrd.append(ord(value))
        sqrd += [12, 0, 2]
        sqrd += [10, 0, 1] + self.getIntBytes(1611064540822, 8) # 時間... fk u time
        sqrd += [10, 0, 2] + self.getIntBytes(int(endMessageId), 8) + [0]
        sqrd += [8, 0, 3] +  self.getIntBytes(messagesCount)
        sqrd += [2, 0, 4, 1]
        sqrd += [2, 0, 5, 0]
        sqrd += [0]
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getMessageBoxes(self, minChatId=0, maxChatId=0, activeOnly=0, messageBoxCountLimit=0, withUnreadCount=False, lastMessagesPerMessageBoxCount=False, unreadOnly=False):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 77, 101, 115, 115, 97, 103, 101, 66, 111, 120, 101, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1, 0, 0, 0, len(minChatId)]
        for value in minChatId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(maxChatId)]
        for value in maxChatId:
            sqrd.append(ord(value))
        sqrd += [2, 0, 3, 0] # activeOnly
        sqrd += [8, 0, 4, 0, 0, 0, 200] # messageBoxCountLimit
        sqrd += [2, 0, 5, 0] # withUnreadCount
        sqrd += [8, 0, 6, 0, 0, 0, 200] # lastMessagesPerMessageBoxCount
        sqrd += [2, 0, 7] # unreadOnly
        sqrd += [0, 0]
        sqrd += [8, 0, 3, 0, 0, 0, 7]
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        params = [
            [15, 2, [11, chatRoomMids]],
            [8, 3, 0]
        ]
        sqrd = self.generateDummyProtocol('getChatRoomAnnouncementsBulk', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getChatRoomAnnouncements(self, chatRoomMid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getChatRoomAnnouncements') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 26, 114, 101, 109, 111, 118, 101, 67, 104, 97, 116, 82, 111, 111, 109, 65, 110, 110, 111, 117, 110, 99, 101, 109, 101, 110, 116, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, len(chatRoomMid)]
        for value in chatRoomMid:
            sqrd.append(ord(value))
        sqrd += [10, 0, 3] + self.getIntBytes(int(announcementSeq), 8)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def createChatRoomAnnouncement(self, chatRoomMid, text, link='', thumbnail='', type=0, displayFields=5, contentMetadata=None):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('createChatRoomAnnouncement') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [8, 0, 3] + self.getIntBytes(type)
        sqrd += [12, 0, 4]
        sqrd += [8, 0, 1] + self.getIntBytes(displayFields)
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [11, 0, 3] + self.getStringBytes(link)
        sqrd += [11, 0, 4] + self.getStringBytes(thumbnail)
        #sqrd += [12, 0, 5] #contentMetadata
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def leaveRoom(self, roomIds):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('leaveRoom') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(roomIds)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def getRoomsV2(self, roomIds):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getRoomsV2') + [0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(roomIds)]
        for mid in roomIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def createRoomV2(self, contactIds):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('createRoomV2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(contactIds)]
        for mid in contactIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def getCountries(self, countryGroup=1):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getCountries') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(countryGroup)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def acquireEncryptedAccessToken(self, featureType=2):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('acquireEncryptedAccessToken') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(featureType)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def blockContact(self, mid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('blockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def unblockContact(self, mid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('unblockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

    def getLastOpRevision(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getServerTime(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 83, 101, 114, 118, 101, 114, 84, 105, 109, 101, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getConfigurations(self):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 67, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
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
            "x-las": "F", # or "B" if background
            "x-lam": "w", # or "m"
            "x-lac": "46692" # carrier
        })
        try:
            data = self.postPackDataAndGetUnpackRespData("/P5" ,sqrd, 5, encType=0, headers=hr)
            if data is None:
                return []
            if 'error' not in data:
                for op in data:
                    if op[3] == 0:
                        if 10 in op:
                            a = op[10].split('\x1e')
                            self.individualRev = a[0]
                        if 11 in op:
                            b = op[11].split('\x1e')
                            self.globalRev = b[0]
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
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 102, 101, 116, 99, 104, 79, 112, 115, 0, 0, 0, 0]
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
            res = self.testPollConn.post("https://gf.line.naver.jp/enc", data=data, headers=hr, timeout=180)
            if res.status_code == 200:
                data = self.decData(res.content)
                data = self.tryReadData(data)
                if 'fetchOps' in data:
                    for op in data['fetchOps']:
                        if op[3] == 0:
                            if 10 in op:
                                a = op[10].split('\x1e')
                                self.individualRev = a[0]
                                self.log(f"individualRev: {self.individualRev}")
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
        
    def fetchOperations(self, deviceId, offsetFrom):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/P3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 102, 101, 116, 99, 104, 79, 112, 115, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        deviceId = str(deviceId).encode()
        sqrd += [11, 0, 1] + self.getIntBytes(len(deviceId))
        for value2 in deviceId:
            sqrd.append(value2)
        sqrd += [10, 0, 2] + self.getIntBytes(offsetFrom, 8)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        hr = self.server.additionalHeaders(self.server.Headers, {
            "x-lst": "180000",
        })
        res = self.req_poll.post(self.url, data=data, headers=hr)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def sendEchoPush(self, text):
        # for long poll? check conn is alive
        # text: 1614384862517 = time
        sqrd = [128, 1, 0, 1] + self.getStringBytes('sendEchoPush') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def getRepairElements(self):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getRepairElements') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [2, 0, 1, 1] # profile
        sqrd += [2, 0, 2, 1] # settings
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
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
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getSettingsAttributes2') + [0, 0, 0, 0]
        sqrd += [14, 0, 2, 8, 0, 0, 0, len(attributesToRetrieve)]
        for value in attributesToRetrieve:
            sqrd += self.getIntBytes(value)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def updateSettingsAttributes2(self, settings: dict, attributesToUpdate: list):
        if type(attributesToUpdate) != list:
            attributesToRetrieve = [attributesToUpdate]
            print('[attributesToRetrieve] plz using LIST')
        sqrd = [128, 1, 0, 1] + self.getStringBytes('updateSettingsAttributes2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [12, 0, 3]
        for sk, sv in settings.items():
            svt = type(sv)
            if svt == bool:
                sqrd += [2, 0, sk, int(sv)]
            elif svt == int:
                sqrd += [10, 0, sk] + self.getIntBytes(sv, 8)
            else:
                print(f"[updateSettingsAttributes2] not support type {svt} (id: {sk})")
        sqrd += [0]
        sqrd += [14, 0, 4, 8, 0, 0, 0, len(attributesToUpdate)]
        for value in attributesToUpdate:
            sqrd += self.getIntBytes(value)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
    def rejectChatInvitation(self, chatMid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('rejectChatInvitation') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getE2EEPublicKey(self, mid, keyVersion, keyId):
        params = [
            [11, 2, mid],
            [8, 3, keyVersion],
            [8, 4, keyId]
        ]
        sqrd = self.generateDummyProtocol('getE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getE2EEPublicKeys(self):
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getE2EEPublicKeysEx(self, ignoreE2EEStatus: int):
        params = []
        sqrd = self.generateDummyProtocol('getE2EEPublicKeysEx', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def removeE2EEPublicKey(self, spec, keyId, keyData):
        params = [
            [12, 2, [
                [8, 1, spec],
                [8, 2, keyId],
                [11, 4, keyData]
            ]]
        ]
        sqrd = self.generateDummyProtocol('removeE2EEPublicKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def registerE2EEGroupKey(self, keyVersion: int, chatMid: str, members: list, keyIds: list, encryptedSharedKeys: list):
        if type(members) != list:
            raise Exception("[registerE2EEGroupKey] members must be a list")
        if type(keyIds) != list:
            raise Exception("[registerE2EEGroupKey] keyIds must be a list")
        if type(encryptedSharedKeys) != list:
            raise Exception("[registerE2EEGroupKey] encryptedSharedKeys must be a list")
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [15, 4, [11, members]],
            [15, 5, [8, keyIds]],
            [15, 6, [11, encryptedSharedKeys]],
        ]
        sqrd = self.generateDummyProtocol('registerE2EEGroupKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getE2EEGroupSharedKey(self, keyVersion: int, chatMid: str, groupKeyId: int):
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [8, 4, groupKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEGroupSharedKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getLastE2EEGroupSharedKey(self, keyVersion: int, chatMid: str):
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getLastE2EEGroupSharedKey', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getLastE2EEPublicKeys(self, chatMid: str):
        params = [
            [11, 2, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getLastE2EEPublicKeys', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def requestE2EEKeyExchange(self, temporalPublicKey: str, keyVersion: int, keyId: int, verifier: str):
        params = [
            [8, 1, 0], # reqSeq
            [11, 2, temporalPublicKey],
            [12, 3, [
                [8, 1, keyVersion],
                [8, 2, keyId]
            ]],
            [11, 4, verifier]
        ]
        sqrd = self.generateDummyProtocol('requestE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def respondE2EEKeyExchange(self, encryptedKeyChain: str, hashKeyChain: str):
        params = [
            [8, 1, 0], # reqSeq
            [11, 2, encryptedKeyChain],
            [11, 3, hashKeyChain]
        ]
        sqrd = self.generateDummyProtocol('respondE2EEKeyExchange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def negotiateE2EEPublicKey(self, mid: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('negotiateE2EEPublicKey') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_NORMAL_ENDPOINT ,sqrd)

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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def createChat(self, name, targetUserMids, type=0, picturePath=None):
        params = [
            [12, 1, [
                [8, 1, 0],
                [8, 2, type],
                [11, 3, name],
                [14, 4, [11, targetUserMids]],
                [11, 5 , picturePath]
            ]]
            
        ]
        sqrd = self.generateDummyProtocol('createChat', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def updateRegion(self, region='TW'):
        raise Exception("updateRegion is not implemented")
        params = [
            [11, 4, region]
            
        ]
        sqrd = self.generateDummyProtocol('updateRegion', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getChatExistence(self, ids):
        params = [
            [12, 2 , [
                [14, 1, [11, ids]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChatExistence', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getChatMembership(self, chatIds):
        params = [
            [12, 2, [
                [14, 1, [11, chatIds]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getChatMembership', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def setChatHiddenStatus(self, chatId, bF=False):
        raise Exception("setChatHiddenStatus is not implemented")
        params = [
            [12, 1, [
                [11, 2, chatId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('setChatHiddenStatus', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getReadMessageOps(self, chatId):
        params = [
            [11, 2, chatId]
        ]
        sqrd = self.generateDummyProtocol('getReadMessageOps', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getReadMessageOpsInBulk(self, chatIds):
        params = [
            [15, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getReadMessageOpsInBulk', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getE2EEMessageInfo(self, mid, msgid, receiverKeyId):
        params = [
            [11, 2, mid],
            [11, 3, msgid],
            [8, 4, receiverKeyId],
        ]
        sqrd = self.generateDummyProtocol('getE2EEMessageInfo', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getMessageBoxCompactWrapUpList(self):
        raise Exception("getMessageBoxCompactWrapUpList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol('getMessageBoxCompactWrapUpList', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getRecentMessages(self, to):
        """ old func? still return 0 """
        params = [
            [11, 2, to],
            [8, 3, 101]
        ]
        sqrd = self.generateDummyProtocol('getRecentMessages', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getRecentMessagesV2(self, to):
        params = [
            [11, 2, to],
            [8, 3, 500]
        ]
        sqrd = self.generateDummyProtocol('getRecentMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getPreviousMessageIds(self, to, count=100):
        params = [
            [12, 2, [
                [11, 1, to],
                [8, 4, count],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getPreviousMessageIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

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
        return self.postPackDataAndGetUnpackRespData("/S3" ,sqrd, 3)

    def getMessageBoxesByIds(self, mids=[]):
        params = [
            [12, 2, [
                [15, 1, [11, mids]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getMessageBoxesByIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)

    def getMessageBoxCompactWrapUpListV2(self, start=0, end=1):
        params =  [
            [8, 2, start],
            [8, 3, end]
        ]
        sqrd = self.generateDummyProtocol('getMessageBoxCompactWrapUpListV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getPreviousMessagesV2WithReadCount(self, mid, time, id, count=101):
        params = [
            [11, 2, mid],
            [12, 3, [
                [10, 1, time],
                [10, 2, id]
            ]],
            [8, 4, count]
        ]
        sqrd = self.generateDummyProtocol('getPreviousMessagesV2WithReadCount', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getNextMessagesV2(self, mid, time, id):
        params = [
            [11, 2, mid],
            [12, 3, [
                [10, 1, time],
                [10, 2, id]
            ]],
            [8, 4, 101] # count, 101 is max? maybe, hehe...
        ]
        sqrd = self.generateDummyProtocol('getNextMessagesV2', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getAllRoomIds(self):
        params = []
        sqrd = self.generateDummyProtocol('getAllRoomIds', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getCompactRooms(self, roomIds):
        params = [
            [15, 2, [11, roomIds]]
        ]
        sqrd = self.generateDummyProtocol('getCompactRooms', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def acquireCallTicket(self, to):
        params = [
            [11, 1, to]
        ]
        sqrd = self.generateDummyProtocol('acquireCallTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def isAbusive(self):
        """ idk """
        params = [
            [8, 1, 0],
            [8, 2, 1], # reportSource
        ]
        sqrd = self.generateDummyProtocol('isAbusive', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def removeBuddySubscriptionAndNotifyBuddyUnregistered(self, contactMids):
        """ OA only """
        params = [
            [15, 1, [11, contactMids]]
        ]
        sqrd = self.generateDummyProtocol('removeBuddySubscriptionAndNotifyBuddyUnregistered', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def makeUserAddMyselfAsContact(self, contactMids):
        """ OA only """
        params = [
            [15, 1, [11, contactMids]]
        ]
        sqrd = self.generateDummyProtocol('makeUserAddMyselfAsContact', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def bulkFollow(self, contactMids):
        """ disallow """
        params = [
            [12, 2, [
                [15, 2, [11, contactMids]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('bulkFollow', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def decryptFollowEMid(self, eMid):
        params = [
            [11, 2, eMid]
        ]
        sqrd = self.generateDummyProtocol('decryptFollowEMid', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getMessageReadRange(self, chatIds):
        params = [
             [15, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getMessageReadRange', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def getChatRoomBGMs(self, chatIds: list):
        params = [
            [14, 2, [11, chatIds]]
        ]
        sqrd = self.generateDummyProtocol('getChatRoomBGMs', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S5" ,sqrd, 5)
        
    def updateChatRoomBGM(self, chatId: str, chatRoomBGMInfo: str):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, chatId],
            [11, 3, chatRoomBGMInfo]
        ]
        sqrd = self.generateDummyProtocol('updateChatRoomBGM', params, 4)
        
    def addSnsId(self, snsAccessToken):
        params = [
            [8, 2, 1], # FB?
            [11, 3, snsAccessToken],
        ]
        sqrd = self.generateDummyProtocol('addSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def removeSnsId(self):
        params = [
            [8, 2, 1], # FB?
        ]
        sqrd = self.generateDummyProtocol('removeSnsId', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getHiddenContactMids(self):
        params = []
        sqrd = self.generateDummyProtocol('getHiddenContactMids', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def blockRecommendation(self, mid):
        params = [
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol('blockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def unblockRecommendation(self, mid):
        params = [
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol('unblockRecommendation', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getRecommendationIds(self):
        params = []
        sqrd = self.generateDummyProtocol('getRecommendationIds', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getBlockedRecommendationIds(self):
        params = []
        sqrd = self.generateDummyProtocol('getBlockedRecommendationIds', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def sync(self):
        """ what is it? """
        # 2021/7/26 it blocked, but 2021/7/20 it working
        # LINE are u here?
        params = [
            [12, 1, []]
        ]
        sqrd = self.generateDummyProtocol('sync', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def updateChatRoomAnnouncement(self, gid, announcementId, messageLink, text):
        params = [
            [11, 2, gid],
            [10, 3, announcementId],
            [12, 4, [
                [8, 1, 5],
                [11, 2, text],
                [11, 3, messageLink],
                [11, 4, 'https://www.deachsword.com/web/img/ex/korone.png']
            ]],
        ]
        sqrd = self.generateDummyProtocol('updateChatRoomAnnouncement', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def reissueTrackingTicket(self):
        params = []
        sqrd = self.generateDummyProtocol('reissueTrackingTicket', params, 4)
        
    def getExtendedProfile(self, syncReason=7):
        params = [
            [8, 1, syncReason]
        ]
        sqrd = self.generateDummyProtocol('getExtendedProfile', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def updateExtendedProfileAttribute(self, year: str, yearPrivacyLevelType: int, yearEnabled: bool, day: str, dayPrivacyLevelType: int, dayEnabled: bool):
        params = [
            [8, 1, self.getCurrReqId()],
            [8, 2, 0], # attr
            [12, 3, [
                [12, 1, [
                    [11, 1, year],
                    [8, 2, yearPrivacyLevelType],
                    [2, 3, year],
                    [8, 6, dayPrivacyLevelType],
                    [2, 7, dayEnabled],
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('updateExtendedProfileAttribute', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
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
            [8, 2, type], # attr
            [11, 3, target],
            [2, 4, enablement]
        ]
        sqrd = self.generateDummyProtocol('setNotificationsEnabled', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findAndAddContactsByPhone(self, phones: list, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        if type(phones) != list:
            raise Exception("[findAndAddContactsByPhone] phones must be a list")
        params = [
            [8, 1, self.getCurrReqId()],
            [14, 2, [11, phones]],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol('findAndAddContactsByPhone', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findAndAddContactsByUserid(self, searchId: str, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference],
        ]
        sqrd = self.generateDummyProtocol('findAndAddContactsByUserid', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
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
        params = [
            [8, 1, self.getCurrReqId()],
            [15, 2, [12, [
                [8, 1, 0],
                # [11, 2, luid],
                [15, 11, [11, phones]],
                [15, 12, [11, emails]],
                [15, 13, [11, userids]],
                # [11, 14, mobileContactName],
                # [11, 15, phoneticName],
            ]]],
        ]
        sqrd = self.generateDummyProtocol('syncContacts', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getContactWithFriendRequestStatus(self, mid: str):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, mid]
        ]
        sqrd = self.generateDummyProtocol('getContactWithFriendRequestStatus', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findContactsByPhone(self, phones: list):
        if type(phones) != list:
            raise Exception("[findContactsByPhone] phones must be a list")
        params = [
            [14, 2, [11, phones]]
        ]
        sqrd = self.generateDummyProtocol('findContactsByPhone', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findContactByUserid(self, searchId: str):
        params = [
            [11, 2, searchId]
        ]
        sqrd = self.generateDummyProtocol('findContactByUserid', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findContactByMetaTag(self, searchId: str, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        params = [
            [11, 2, searchId],
            [11, 3, reference]
        ]
        sqrd = self.generateDummyProtocol('findContactByMetaTag', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findAndAddContactByMetaTag(self, searchId: str, reference: str = '{"screen":"groupMemberList","spec":"native"}'):
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference]
        ]
        sqrd = self.generateDummyProtocol('findAndAddContactByMetaTag', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
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
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def getFavoriteMids(self):
        params = []
        sqrd = self.generateDummyProtocol('getFavoriteMids', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def sendMessageAwaitCommit(self):
        params = []
        sqrd = self.generateDummyProtocol('sendMessageAwaitCommit', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def findContactByUserTicket(self, ticketIdWithTag: str):
        params = [
            [11, 2, ticketIdWithTag]
        ]
        sqrd = self.generateDummyProtocol('findContactByUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def invalidateUserTicket(self):
        params = []
        sqrd = self.generateDummyProtocol('invalidateUserTicket', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def unregisterUserAndDevice(self):
        params = []
        sqrd = self.generateDummyProtocol('unregisterUserAndDevice', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def checkCanUnregisterEx(self, type=1):
        params = [
            [8, 1, type]
        ]
        sqrd = self.generateDummyProtocol('checkCanUnregisterEx', params, 4)
        return self.postPackDataAndGetUnpackRespData('/S5' ,sqrd, 5)
        
    def verifyQrcode(self, verifier, pinCode):
        params = [
            [11, 2, verifier],
            [11, 3, pinCode],
        ]
        sqrd = self.generateDummyProtocol('verifyQrcode', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S4" ,sqrd, 4)