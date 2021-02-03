# -*- coding: utf-8 -*-
from .server import Server
import requests, time, json
import httpx

from .services.TalkService import TalkService
from .services.ShopService import ShopService
from .services.LiffService import LiffService

class API(TalkService, ShopService, LiffService):
    _msgSeq = 0
    
    def __init__(self):
        self.server = Server()
        self.req = requests.session()
        self.req_h2 = httpx.Client(http2=True)
        self.server.Headers = {
            "x-line-application": self.APP_NAME,
            "x-lhm": "POST",
            "x-le": "18",
            "x-lap": "4",
            "x-lpv": "1",
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        
        data = self.decData(res.content)
        sqr = data[39:105].decode()
        url = self.createSession(sqr)
        yield f"URL: {url}"
        if self.checkQrCodeVerified(sqr):
            b = self.verifyCertificate(sqr)
            c = self.createPinCode(sqr)
            yield f"請輸入pincode: {c}"
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return bytes(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['issueChannelToken']
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getChannelInfo']
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req_h2.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req_h2.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req_h2.post("https://gf.line.naver.jp/SQS1", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        #data = self.decData(res.content)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
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
        res = self.req.post("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return data