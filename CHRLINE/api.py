# -*- coding: utf-8 -*-
import requests, time
import httpx

class API(object):
    _msgSeq = 0
    
    def __init__(self):
        self.req = requests.session()
        self.req_h2 = httpx.Client(http2=True)
        self.headers = {
            "x-line-application": self.APP_NAME,
            "x-lhm": "POST",
            "x-le": "18",
            "x-lcs": self._encryptKey,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "content-type": "application/x-thrift; protocol=TBINARY",
            "x-lst": "300000000",
            "x-lal": "zh_TW",
        }
        self.authToken = None
        self.revision = 0
        self.globalRev = 0
        self.individualRev = 0

    def requestSQR(self, isSelf=True):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 99, 114, 101, 97, 116, 101, 83, 101, 115, 115, 105, 111, 110, 0, 0, 0, 0, 12, 0, 1, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        
        data = self.decData(res.content)
        sqr = data[39:105].decode()
        url = self.createSession(sqr)
        print(f"URL: {url}")
        if self.checkQrCodeVerified(sqr):
            b = self.verifyCertificate(sqr)
            c = self.createPinCode(sqr)
            print(f"請輸入pincode: {c}")
            if self.checkPinCodeVerified(sqr):
                e = self.qrCodeLogin(sqr)
                if isSelf:
                    self.authToken = e.decode()
                    print(f"AuthToken: {self.authToken}")
                else:
                    return e.decode()
                return self.authToken
        return False
        
    def createSession(self, qrcode):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 12, 99, 114, 101, 97, 116, 101, 81, 114, 67, 111, 100, 101, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        #[127, 95, 38, 16]
        data = self.decData(res.content)
        url = data[38:128].decode()
        return url
        
    def checkQrCodeVerified(self, qrcode):
        _headers = {
            "X-Line-Access": qrcode,
            "x-lpqs": "/acct/lp/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 99, 104, 101, 99, 107, 81, 114, 67, 111, 100, 101, 86, 101, 114, 105, 102, 105, 101, 100, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        if res.status_code == 200:
            return True
        return False
        
    def verifyCertificate(self, qrcode):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 118, 101, 114, 105, 102, 121, 67, 101, 114, 116, 105, 102, 105, 99, 97, 116, 101, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return data
        
    def createPinCode(self, qrcode):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 99, 114, 101, 97, 116, 101, 80, 105, 110, 67, 111, 100, 101, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return data[39:43].decode()
        
    def checkPinCodeVerified(self, qrcode):
        _headers = {
            "X-Line-Access": qrcode,
            "x-lpqs": "/acct/lp/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 99, 104, 101, 99, 107, 80, 105, 110, 67, 111, 100, 101, 86, 101, 114, 105, 102, 105, 101, 100, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        if res.status_code == 200:
            return True
        return False
        
    def qrCodeLogin(self, qrcode):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 113, 114, 67, 111, 100, 101, 76, 111, 103, 105, 110, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [11, 0, 2, 0, 0, 0, len(self.APP_TYPE)]
        for device in self.APP_TYPE:
            sqrd.append(ord(device))
        sqrd += [2, 0, 3, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        pem = data[36:101] #64dig?
        print("證書: ", pem.decode())
        _token = data[108:]
        return bytes(_token[:88]) # 88dig?
        token = []
        for t in _token:
            token.append(t)
            if t == b"=":
                break
        return bytes(token)
        
    def CPF(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CPF"
        }
        a = self.encHeaders(_headers)
        sqrd = []
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return bytes(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getProfile(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S2"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 80, 114, 111, 102, 105, 108, 101, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def issueChannelToken(self, channelId="1433572998"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 105, 115, 115, 117, 101, 67, 104, 97, 110, 110, 101, 108, 84, 111, 107, 101, 110, 0, 0, 0, 0, 11, 0, 1, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getChannelInfo(self, channelId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 103, 101, 116, 67, 104, 97, 110, 110, 101, 108, 73, 110, 102, 111, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getChats(self, mids):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        
        
        sqrd = [128, 1, 0, 1, 0, 0, 0, 8, 103, 101, 116, 67, 104, 97, 116, 115, 0, 0, 0, 0]
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def deleteOtherFromChat(self, to, mid):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        self.sendMessage(to, 'Power by CHRLINE API')
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        self.sendMessage(to, 'Power by CHRLINE API')
        return self.tryReadData(data)
        
    def updateChat(self, chatMid, chatName):
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
        sqrd += [11, 0, 2, 0, 0, 0, len(chatMid)]
        for value in chatMid:
            sqrd.append(ord(value))
        chatName = str(chatName).encode()
        sqrd += [11, 0, 6] + self.getIntBytes(len(chatName))
        for value2 in chatName:
            sqrd.append(value2)
        sqrd += [0]
        sqrd += [8, 0, 3, 0, 0, 0, 1] # updatedAttribute
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        sqrd += [10, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0] # createTime
        if text is not None:
            text = str(text).encode()
            sqrd += [11, 0, 10] + self.getIntBytes(len(text))
            for value2 in text:
                sqrd.append(value2)
        sqrd += [2, 0, 14, 0] # hasContent
        sqrd += [8, 0, 15] + self.getIntBytes(contentType)
        if location  and type(location) == dict:
            sqrd += [12, 0, 11]
            sqrd += [11, 0, 2] + self.getStringBytes(location.get(2, ''))
            sqrd += [4, 0, 3] + self.getFloatBytes(location.get(3, 0))
            sqrd += [4, 0, 4] + self.getStringBytes(location.get(4, 0))
            sqrd += [11, 0, 6] + self.getStringBytes(location.get(6, ''))
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def sendContact(self, to, mid):
        return self.sendMessage(to, None, contentType=13, contentMetadata={"mid": mid})
        
    def sendLocation(self, to, title, la, lb, subTile=''):
        data = {2: title, 3: la, 4: lb, 6: subTile}
        #return self.sendMessage(to, "test", location=data)
        return self.sendMessage(to, None, contentType=13, location=data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        sqrd += [10, 0, 1] + self.getIntBytes(1611064540822, 8)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def wakeUpLongPolling(self, clientRevision):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/P3" # P3? S3?
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 119, 97, 107, 101, 85, 112, 76, 111, 110, 103, 80, 111, 108, 108, 105, 110, 103, 0, 0, 0, 0]
        sqrd += [10, 0, 2] + self.getIntBytes(clientRevision, 8)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def returnTicket(self, searchId, fromEnvInfo, otp):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3" # V3?
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 12, 114, 101, 116, 117, 114, 110, 84, 105, 99, 107, 101, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1] # AcquireOACallRouteRequest
        sqrd += [11, 0, 1, 0, 0, 0, len(searchId)]
        for value in searchId:
            sqrd.append(ord(value))
        # sqrd += [13, 0, 2, 0, 0, 0, len(otp)] #todo?
        sqrd += [11, 0, 3, 0, 0, 0, len(otp)]
        for value in otp:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getModulesV2(self, etag):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/WALLET3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 12, 103, 101, 116, 77, 111, 100, 117, 108, 101, 115, 86, 50, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [11, 0, 1, 0, 0, 0, len(etag)] # etag
        for value in etag:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getProduct(self, shopId, productId, language="zh-TW", country="TW"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/TSHOP4"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 80, 114, 111, 100, 117, 99, 116, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(shopId)] # e.g. stickershop
        for value in shopId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(productId)]
        for value in productId:
            sqrd.append(ord(value))
        sqrd += [12, 0, 4]
        sqrd += [11, 0, 1, 0, 0, 0, len(language)]
        for value in language:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(country)]
        for value in country:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def setClovaCredential(self, authSessionId, authLoginVersion, metaData, cipherText):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/api/v4p/rs"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 115, 101, 116, 67, 108, 111, 118, 97, 67, 114, 101, 100, 101, 110, 116, 105, 97, 108, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(authSessionId)]
        for value in authSessionId:
            sqrd.append(ord(value))
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 1, 0, 0, 0, 7]
        sqrd += [13, 0, 2, 0, 0, 0, 0] #metaData
        sqrd += [11, 0, 3, 0, 0, 0, len(cipherText)]
        for value in cipherText:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getCommonDomains(self, lastSynced=0):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 67, 111, 109, 109, 111, 110, 68, 111, 109, 97, 105, 110, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getCommonDomains']
        
    def acquireCallRoute(self, to, callType, fromEnvInfo=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/V3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 97, 99, 113, 117, 105, 114, 101, 67, 97, 108, 108, 82, 111, 117, 116, 101, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(to)]
        for value in to:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3] + self.getIntBytes(callType)
        # sqrd += [13, 0, 4]
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['acquireCallRoute']
        
    def acquireGroupCallRoute(self, chatMid, mediaType=0, isInitialHost=None, capabilities=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/V3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 21, 97, 99, 113, 117, 105, 114, 101, 71, 114, 111, 117, 112, 67, 97, 108, 108, 82, 111, 117, 116, 101, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(chatMid)]
        for value in chatMid:
            sqrd.append(ord(value))
        sqrd += [8, 0, 3] + self.getIntBytes(mediaType)
        sqrd += [2, 0, 4, 1]
        # sqrd += [15, 0, 5] # capabilities
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['acquireGroupCallRoute']
        
    def acquireOACallRoute(self, searchId, fromEnvInfo=None, otp=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/V3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 18, 97, 99, 113, 117, 105, 114, 101, 79, 65, 67, 97, 108, 108, 82, 111, 117, 116, 101, 0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 2, 0, 0, 0, len(searchId)]
        for value in searchId:
            sqrd.append(ord(value))
        # sqrd += [13, 0, 2] # fromEnvInfo
        sqrd += [11, 0, 3, 0, 0, 0, len(otp)]
        for value in otp:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def acquireTestCallRoute(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/V3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 97, 99, 113, 117, 105, 114, 101, 84, 101, 115, 116, 67, 97, 108, 108, 82, 111, 117, 116, 101, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['acquireTestCallRoute']
        
    def inviteIntoGroupCall(self, chatMid, memberMids, mediaType=0):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/V3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 105, 110, 118, 105, 116, 101, 73, 110, 116, 111, 71, 114, 111, 117, 112, 67, 97, 108, 108, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(chatMid)]
        for value in chatMid:
            sqrd.append(ord(value))
        sqrd += [15, 0, 3, 11, 0, 0, 0, len(memberMids)]
        for mid in memberMids:
            sqrd += [0, 0, 0, 33]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def issueRequestTokenWithAuthScheme(self, channelId, otpId, authScheme, returnUrl):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 31, 105, 115, 115, 117, 101, 82, 101, 113, 117, 101, 115, 116, 84, 111, 107, 101, 110, 87, 105, 116, 104, 65, 117, 116, 104, 83, 99, 104, 101, 109, 101, 0, 0, 0, 0]
        sqrd += [11, 0, 1, 0, 0, 0, len(channelId)]
        for value in channelId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(otpId)]
        for value in otpId:
            sqrd.append(ord(value))
        sqrd += [15, 0, 3, 11, 0, 0, 0, len(authScheme)]
        for mid in authScheme:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(returnUrl)]
        for value in returnUrl:
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req.post("https://gfp.line.naver.jp/enc", data=data, headers=self.headers)
        data_len = int(res.headers['content-length'])
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['fetchOperations']
        
    def openSession(self, udid, deviceModel):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/ACCT/authfactor/eap/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 111, 112, 101, 110, 83, 101, 115, 115, 105, 111, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        sqrd += [12, 0, 1]
        udid = str(udid).encode()
        sqrd += [11, 0, 1] + self.getIntBytes(len(udid))
        for value2 in udid:
            sqrd.append(value2)
        deviceModel = str(deviceModel).encode()
        sqrd += [11, 0, 2] + self.getIntBytes(len(deviceModel))
        for value2 in deviceModel:
            sqrd.append(value2)
        sqrd += [0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def connectEapAccount(self, authSessionId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/ACCT/authfactor/eap/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 99, 111, 110, 110, 101, 99, 116, 69, 97, 112, 65, 99, 99, 111, 117, 110, 116, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        authSessionId = str(authSessionId).encode()
        sqrd += [11, 0, 1] + self.getIntBytes(len(authSessionId))
        for value2 in authSessionId:
            sqrd.append(value2)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def verifyEapLogin(self, authSessionId, type, accessToken):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/ACCT/authfactor/eap/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 118, 101, 114, 105, 102, 121, 69, 97, 112, 76, 111, 103, 105, 110, 0, 0, 0, 0]
        sqrd += [12, 0, 1]
        authSessionId = str(authSessionId).encode()
        sqrd += [11, 0, 1] + self.getIntBytes(len(authSessionId))
        for value2 in authSessionId:
            sqrd.append(value2)
        sqrd += [12, 0, 2]
        sqrd += [8, 0, 1] + self.getIntBytes(type) # 1: FB  2: APPLE
        accessToken = str(accessToken).encode()
        sqrd += [11, 0, 2] + self.getIntBytes(len(accessToken))
        for value2 in accessToken:
            sqrd.append(value2)
        sqrd += [0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req_h2.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req_h2.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
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
        res = self.req_h2.post("https://gf.line.naver.jp/SQS1", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def inviteFriends(self, friendMids, message, messageMetadata={}, imageObsPath="/r/myhome/c/0f3a02b6f993d3b627eeca97d2095b9b"):
        """ old ? """
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/PY3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 105, 110, 118, 105, 116, 101, 70, 114, 105, 101, 110, 100, 115, 0, 0, 0, 0]
        sqrd += [15, 0, 1, 11, 0, 0, 0, len(friendMids)]
        for mid in friendMids:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 2] + self.getStringBytes(message)
        _keys = messageMetadata.copy().keys()
        sqrd += [13, 0, 3, 11, 11] + self.getIntBytes(len(_keys))# key and val must str
        for _k in _keys:
            _v = messageMetadata[_k]
            sqrd += self.getStringBytes(_k)
            sqrd += self.getStringBytes(_v)
        sqrd += [11, 0, 4] + self.getStringBytes(imageObsPath)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        #data = self.decData(res.content)
        return self.tryReadData(data)
        
    def inviteFriendsBySms(self, phoneNumberList):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 105, 110, 118, 105, 116, 101, 70, 114, 105, 101, 110, 100, 115, 0, 0, 0, 0]
        sqrd += [15, 0, 2, 11, 0, 0, 0, len(phoneNumberList)]
        for mid in phoneNumberList:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        print(data)
        return self.tryReadData(data)
        
    def testFunc(self, path, funcName, funcValue=None, funcValueId=1):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': path
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, len(funcName)]
        for name in funcName:
            sqrd.append(ord(name))
        sqrd += [0, 0, 0, 0]
        print(sqrd)
        if funcValue:
            sqrd += [11, 0, funcValueId, 0, 0, 0, len(funcValue)]
            for value in funcValue: # string only
                sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
    
    def testTBinary(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/P3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10]
        for value in "getProfile":
            sqrd.append(ord(value))
        sqrd += [0,0,0,0,0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return data
    
    def testTCompact(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/P4"
        }
        a = self.encHeaders(_headers)
        sqrd = [130, 33, 1, 10]
        for value in "getProfile":
            sqrd.append(ord(value))
        #for value in "fetchOps":
        #    sqrd.append(ord(value))
        #sqrd += [38, 136, 176, 2, 21, 200, 1, 22, 238, 179, 106, 22, 226, 1, 0] fetchOps
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        self.tryReadTCompactData(data)
        return data
    
    def testTMoreCompact(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/P5"
        }
        a = self.encHeaders(_headers)
        sqrd = [130, 33, 1, 10]
        for value in "getProfile":
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.headers)
        data = self.decData(res.content)
        return data