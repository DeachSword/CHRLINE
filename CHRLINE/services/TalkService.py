# -*- coding: utf-8 -*-
import time
import json
import requests
import http.client as http_client

class TalkService(object):
    url = "https://ga2.line.naver.jp/enc"
    testConn = http_client.HTTPSConnection("gf.line.naver.jp", 443)
    
    def __init__(self):
        pass

    def sendMessage(self, to, text, contentType=0, contentMetadata={}, relatedMessageId=None, location=None, raw=False):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 115, 101, 110, 100, 77, 101, 115, 115, 97, 103, 101, 0, 0, 0, 0, 8, 0, 1]
        sqrd += self.getIntBytes(self._msgSeq)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        if raw:
            return data
        
        #self.testConn.request("POST", "/enc", data, self.server.Headers)
        #response = self.testConn.getresponse()
        #print(response.status, response.reason)
        #data = response.read()
        res = self.server.postContent(self.LINE_HOST_DOMAIN + self.LINE_TALK_ENDPOINT, data=data, headers=self.server.Headers)
        data = res.content
        data = self.decData(data)
        return self.tryReadData(data)['sendMessage']
        
    def sendContact(self, to, mid):
        return self.sendMessage(to, None, contentType=13, contentMetadata={"mid": mid})
        
    def sendLocation(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, None, contentType=15, location=data)
        
    def sendLocationMessage(self, to, title, la=0.0, lb=0.0, subTile='CHRLINE API'):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, "test", location=data)
    
    def getEncryptedIdentity(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 69, 110, 99, 114, 121, 112, 116, 101, 100, 73, 100, 101, 110, 116, 105, 116, 121, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getEncryptedIdentity']
        
    def getProfile(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 80, 114, 111, 102, 105, 108, 101, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        print(self.server.Headers)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getProfile']
        
    def getSettings(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 83, 101, 116, 116, 105, 110, 103, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getSettings']
    
    def sendChatChecked(self, chatMid, lastMessageId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['sendChatChecked']
        
    def unsendMessage(self, messageId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 117, 110, 115, 101, 110, 100, 77, 101, 115, 115, 97, 103, 101, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(messageId)]
        for value in messageId:
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getContact(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getContacts(self, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getContactsV2(self, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 67, 111, 110, 116, 97, 99, 116, 115, 86, 50, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0, 0]
        
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def findAndAddContactsByMid(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        
        sqrd = [128, 1, 0, 1, 0, 0, 0, 23, 102, 105, 110, 100, 65, 110, 100, 65, 100, 100, 67, 111, 110, 116, 97, 99, 116, 115, 66, 121, 77, 105, 100, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 0]
        #sqrd += [11, 0, 4, 0, 0, 0, 0] # reference
        sqrd += [0]
        
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getGroup(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getGroup']
        
    def getGroups(self, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 9, 103, 101, 116, 71, 114, 111, 117, 112, 115, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getGroups']
        
    def getGroupsV2(self, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 103, 101, 116, 71, 114, 111, 117, 112, 115, 86, 50, 0, 0, 0, 0, 15, 0, 2, 11, 0, 0, 0, len(mids)]
        for mid in mids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getGroupsV2']
        
    def getChats(self, mids, withMembers=True, withInvitees=True):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        if type(mids) is not list:
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getChats']
        
    def getAllChatMids(self, withMembers=True, withInvitees=True):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getAllChatMids') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [2, 0, 1, int(withMembers)]
        sqrd += [2, 0, 2, int(withInvitees)]
        sqrd += [0]
        sqrd += [8, 0, 2] + self.getIntBytes(7)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getAllChatMids']
        
    def getCompactGroup(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 15, 103, 101, 116, 67, 111, 109, 112, 97, 99, 116, 71, 114, 111, 117, 112, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, 33]
        for value in mid:
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def deleteOtherFromChat(self, to, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        if type(mid) is 'list':
            _lastReq = None
            for _mid in mid:
                print(f'[deleteOtherFromChat] The parameter \'mid\' should be str')
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def inviteIntoChat(self, to, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def cancelChatInvitation(self, to, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['cancelChatInvitation']
        
    def deleteSelfFromChat(self, to):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['deleteSelfFromChat']
        
    def acceptChatInvitation(self, to):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 97, 99, 99, 101, 112, 116, 67, 104, 97, 116, 73, 110, 118, 105, 116, 97, 116, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0] # seq?
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        self.sendMessage(to, 'Powered by CHRLINE API')
        return self.tryReadData(data)['acceptChatInvitation']
        
    def reissueChatTicket(self, groupMid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes("reissueChatTicket") + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(groupMid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['reissueChatTicket']
        
    def findChatByTicket(self, ticketId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 102, 105, 110, 100, 67, 104, 97, 116, 66, 121, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 1] + self.getStringBytes(ticketId)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['findChatByTicket']
        
    def acceptChatInvitationByTicket(self, to, ticket):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        self.sendMessage(to, 'Powered by CHRLINE API')
        return self.tryReadData(data)['acceptChatInvitationByTicket']
        
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
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 117, 112, 100, 97, 116, 101, 67, 104, 97, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [8, 0, 1, 0, 0, 0, 2] # type
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        if chatSet.get(4) is not None:
            sqrd += [12, 0, 8]
            sqrd += [12, 0, 1]
            sqrd += [2, 0, 2, int(chatSet[4])]
            sqrd += [0, 0]
        if chatSet.get(6) is not None:
            sqrd += [11, 0, 6] + self.getStringBytes(chatSet[6])
        sqrd += [0]
        sqrd += [8, 0, 3] + self.getIntBytes(updatedAttribute)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['updateChat']
        
    def updateChatName(self, chatMid, name):
        return self.updateChat(chatMid, {6: name}, 1)
        
    def updateChatPreventedUrl(self, chatMid, bool):
        return self.updateChat(chatMid, {4: bool}, 4)
    
    def getGroupIdsJoined(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 71, 114, 111, 117, 112, 73, 100, 115, 74, 111, 105, 110, 101, 100, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getGroupIdsJoined']
        
    def getGroupIdsInvited(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 103, 101, 116, 71, 114, 111, 117, 112, 73, 100, 115, 73, 110, 118, 105, 116, 101, 100, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getGroupIdsInvited']
        
    def getAllContactIds(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 65, 108, 108, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getAllContactIds']
        
    def getBlockedContactIds(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 103, 101, 116, 66, 108, 111, 99, 107, 101, 100, 67, 111, 110, 116, 97, 99, 116, 73, 100, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getBlockedContactIds']
        
    def getBlockedRecommendationIds(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 27, 103, 101, 116, 66, 108, 111, 99, 107, 101, 100, 82, 101, 99, 111, 109, 109, 101, 110, 100, 97, 116, 105, 111, 110, 73, 100, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getBlockedRecommendationIds']
        
    def getAllReadMessageOps(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        print('Korone is my wife :p')
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getAllReadMessageOps']
        
    def sendPostback(self, messageId, url, chatMID, originMID):
        """
        :url: linepostback://postback?_data=
        """
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 12, 115, 101, 110, 100, 80, 111, 115, 116, 98, 97, 99, 107, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        messageId = str(messageId).encode()
        sqrd += [11, 0, 1] + self.getIntBytes(len(messageId))
        for value2 in messageId:
            sqrd.append(value2)
        url = str(url).encode()
        sqrd += [11, 0, 2] + self.getIntBytes(len(url))
        for value2 in url:
            sqrd.append(value2)
        chatMID = str(chatMID).encode()
        sqrd += [11, 0, 3] + self.getIntBytes(len(chatMID))
        for value2 in chatMID:
            sqrd.append(value2)
        originMID = str(originMID).encode()
        sqrd += [11, 0, 4] + self.getIntBytes(len(originMID))
        for value2 in originMID:
            sqrd.append(value2)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['sendPostback']
        
    def getPreviousMessagesV2WithRequest(self, messageBoxId, endMessageId=0, messagesCount=200, withReadCount=0, receivedOnly=False):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getPreviousMessagesV2WithRequest']
        
    def getMessageBoxes(self, minChatId=0, maxChatId=0, activeOnly=0, messageBoxCountLimit=0, withUnreadCount=False, lastMessagesPerMessageBoxCount=False, unreadOnly=False):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getMessageBoxes']
        
    def getMessageReadRange(self, chatIds):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 103, 101, 116, 77, 101, 115, 115, 97, 103, 101, 82, 101, 97, 100, 82, 97, 110, 103, 101, 0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(chatIds)]
        for mid in chatIds:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 7]
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getMessageReadRange']
        
    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 28, 103, 101, 116, 67, 104, 97, 116, 82, 111, 111, 109, 65, 110, 110, 111, 117, 110, 99, 101, 109, 101, 110, 116, 115, 66, 117, 108, 107, 0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(chatRoomMids)]
        for mid in chatRoomMids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [8, 0, 3, 0, 0, 0, 7]
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getChatRoomAnnouncementsBulk']
        
    def getChatRoomAnnouncements(self, chatRoomMid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getChatRoomAnnouncements') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(chatRoomMid)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getChatRoomAnnouncements']
        
    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 26, 114, 101, 109, 111, 118, 101, 67, 104, 97, 116, 82, 111, 111, 109, 65, 110, 110, 111, 117, 110, 99, 101, 109, 101, 110, 116, 0, 0, 0, 0]
        sqrd += [8, 0, 1, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, len(chatRoomMid)]
        for value in chatRoomMid:
            sqrd.append(ord(value))
        sqrd += [10, 0, 3] + self.getIntBytes(int(announcementSeq), 8)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['removeChatRoomAnnouncement']
        
    def createChatRoomAnnouncement(self, chatRoomMid, text, link='', thumbnail='', type=0, displayFields=5, contentMetadata=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['createChatRoomAnnouncement']

    def leaveRoom(self, roomIds):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('leaveRoom') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(roomIds)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['leaveRoom']

    def getRoomsV2(self, roomIds):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getRoomsV2') + [0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(roomIds)]
        for mid in roomIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getRoomsV2']

    def createRoomV2(self, contactIds):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('createRoomV2') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(contactIds)]
        for mid in contactIds:
            sqrd += self.getStringBytes(mid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['createRoomV2']

    def getCountries(self, countryGroup=1):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getCountries') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(countryGroup)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getCountries']

    def acquireEncryptedAccessToken(self, featureType=2):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('acquireEncryptedAccessToken') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(featureType)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['acquireEncryptedAccessToken']

    def blockContact(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('blockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['blockContact']

    def unblockContact(self, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('unblockContact') + [0, 0, 0, 0]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(mid)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['unblockContact']

    def getLastOpRevision(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 76, 97, 115, 116, 79, 112, 82, 101, 118, 105, 115, 105, 111, 110, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getLastOpRevision']
        
    def getServerTime(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 103, 101, 116, 83, 101, 114, 118, 101, 114, 84, 105, 109, 101, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getServerTime']
        
    def getConfigurations(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 103, 101, 116, 67, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getConfigurations']
        
    def fetchOps(self, revision, count=500):
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
            "x-lst": "180000",
        })
        res = self.server.postContent("https://gfp.line.naver.jp/enc", data=data, headers=hr)
        if res.status_code == 200:
            data = self.decData(res.content)
            data = self.tryReadData(data)
            if 'fetchOps' in data:
                for op in data['fetchOps']:
                    if op[3] == 0:
                        if 10 in op:
                            a = op[10].split('\x1e')
                            self.individualRev = a[0]
                        if 11 in op:
                            b = op[11].split('\x1e')
                            self.globalRev = b[0]
                return data['fetchOps']
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
        return self.tryReadData(data)['fetchOperations']
        
    def sendEchoPush(self, text):
        # for long poll? check conn is alive
        # text: 1614384862517 = time
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('sendEchoPush') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(text)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['sendEchoPush']
        
    def getRepairElements(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getRepairElements') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [2, 0, 1, 1] # profile
        sqrd += [2, 0, 2, 1] # settings
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getRepairElements']
        
    def getSettingsAttributes2(self, attributesToRetrieve):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        if type(attributesToRetrieve) != 'list':
            attributesToRetrieve = [attributesToRetrieve]
            print('[attributesToRetrieve] plz using LIST')
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getSettingsAttributes2') + [0, 0, 0, 0]
        sqrd += [14, 0, 2, 11, 0, 0, 0, len(attributesToRetrieve)]
        for value in attributesToRetrieve:
            sqrd += self.getStringBytes(value)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getSettingsAttributes2']
        
    def rejectChatInvitation(self, chatMid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('rejectChatInvitation') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [11, 0, 2] + self.getStringBytes(chatMid)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['rejectChatInvitation']
        
    def updateProfileAttribute(self, int: attr, string: value):
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
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('updateProfileAttribute') + [0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [8, 0, 1] + self.getIntBytes(0) #reqSeq
        sqrd += [8, 0, 2] + self.getIntBytes(attr)
        sqrd += [11, 0, 3] + self.getStringBytes(value)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['updateProfileAttribute']
        
        