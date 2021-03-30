# -*- coding: utf-8 -*-
from .server import Server
import requests, time, json, rsa, binascii
import httpx

from .services.TalkService import TalkService
from .services.ShopService import ShopService
from .services.LiffService import LiffService
from .services.ChannelService import ChannelService
from .services.SquareService import SquareService
from .services.BuddyService import BuddyService
from .services.PrimaryAccountInitService import PrimaryAccountInitService

class API(TalkService, ShopService, LiffService, ChannelService, SquareService, BuddyService, PrimaryAccountInitService):
    _msgSeq = 0
    url = "https://gf.line.naver.jp/enc"
    
    def __init__(self):
        self.server = Server()
        self.req = requests.session()
        self.req_h2 = httpx.Client(http2=True)
        self.server.Headers = {
            "x-line-application": self.APP_NAME,
            "x-le": self.le,
            "x-lap": "4",
            "x-lpv": "1",
            "x-lcs": self._encryptKey,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "content-type": "application/x-thrift; protocol=TBINARY",
            "x-lal": self.LINE_LANGUAGE,
            "x-lhm": "POST",
        }
        self.authToken = None
        self.revision = 0
        self.globalRev = 0
        self.individualRev = 0
        PrimaryAccountInitService.__init__(self)

    def requestEmailLogin(self, email, pw):
        rsaKey = self.getRSAKeyInfo()
        keynm = rsaKey[1]
        nvalue = rsaKey[2]
        evalue = rsaKey[3]
        sessionKey = rsaKey[4]
        certificate = self.getEmailCert(email)
        message = (chr(len(sessionKey)) + sessionKey +
           chr(len(email)) + email +
           chr(len(pw)) + pw).encode('utf-8')
        pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
        crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()
        res = self.loginZ(keynm, crypto, certificate=certificate)
        if 1 not in res:
            verifier = self.checkLoginZPinCode(res[3])['verifier']
            res = self.loginZ(keynm, crypto, verifier=verifier)
            self.saveEmailCert(email, res[2])
        self.authToken = res[1]
        print(f"AuthToken: {self.authToken}")
        return True

    def requestSQR(self, isSelf=True):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 13, 99, 114, 101, 97, 116, 101, 83, 101, 115, 115, 105, 111, 110, 0, 0, 0, 0, 12, 0, 1, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        
        data = self.decData(res.content)
        sqr = data[39:105].decode()
        url = self.createSession(sqr)
        yield f"URL: {url}"
        if self.checkQrCodeVerified(sqr):
            b = self.verifyCertificate(sqr, self.getSqrCert())
            print(b)
            isCheck = False
            if 'error' in b:
                c = self.createPinCode(sqr)
                yield f"請輸入pincode: {c}"
                if self.checkPinCodeVerified(sqr):
                    isCheck = True
            else:
                isCheck = True
            if isCheck:
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        if res.status_code == 200:
            return True
        return False
        
    def verifyCertificate(self, qrcode, cert=None):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 118, 101, 114, 105, 102, 121, 67, 101, 114, 116, 105, 102, 105, 99, 97, 116, 101, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        if cert is not None:
            sqrd += [11, 0, 2] + self.getStringBytes(cert)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['verifyCertificate']

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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        pem = data[37:101]
        self.saveSqrCert(pem.decode())
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return bytes(data)
        
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        #data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getCountrySettingV4(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/PY3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getCountrySettingV4') + [0, 0, 0, 0]
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getCountrySettingV4']
        
    def getRSAKeyInfo(self, provider=1):
        """
        provider:
         - UNKNOWN(0),
         - LINE(1),
         - NAVER_KR(2),
         - LINE_PHONE(3)
        """
        _headers = {
            'x-lpqs': "/api/v3/TalkService.do"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getRSAKeyInfo') + [0, 0, 0, 0]
        sqrd += [8, 0, 2] + self.getIntBytes(provider)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getRSAKeyInfo']
        
    def loginV2(self, provider, keynm, encData, deviceName='Chrome'):
        """ same loginZ , but i using it for E2EE :D and not work now :P"""
        _headers = {
            'x-lpqs': "/api/v3p/rs"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('loginV2') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [8, 0, 1] + self.getIntBytes(2)
        sqrd += [8, 0, 2] + self.getIntBytes(provider)
        sqrd += [11, 0, 3] + self.getStringBytes(keynm)
        sqrd += [11, 0, 4] + self.getStringBytes(encData)
        sqrd += [2, 0, 5, 1]
        sqrd += [11, 0, 7] + self.getStringBytes(deviceName)
        sqrd += [8, 0, 11] + self.getIntBytes(1)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['loginV2']
        
    def loginZ(self, keynm, encData, systemName='DeachSword-2021', certificate=None, verifier=None):
        _headers = {
            'x-lpqs': "/api/v3p/rs"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('loginZ') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        loginType = 0
        if verifier is not None:
            loginType = 1
        sqrd += [8, 0, 1] + self.getIntBytes(loginType) # 2 if e2ee
        sqrd += [8, 0, 2] + self.getIntBytes(1) #provider
        sqrd += [11, 0, 3] + self.getStringBytes(keynm)
        sqrd += [11, 0, 4] + self.getStringBytes(encData)
        sqrd += [2, 0, 5, 0]
        sqrd += [11, 0, 6] + self.getStringBytes("") #accessLocation
        sqrd += [11, 0, 7] + self.getStringBytes(systemName)
        sqrd += [11, 0, 8] + self.getStringBytes(certificate)
        if verifier is not None:
            sqrd += [11, 0, 9] + self.getStringBytes(verifier)
        #sqrd += [11, 0, 10] + self.getStringBytes("") #secret
        sqrd += [8, 0, 11] + self.getIntBytes(1)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['loginZ']
        
    def checkLoginZPinCode(self, accessSession):
        _headers = {
            'X-Line-Access': accessSession,
            'x-lpqs': "/Q"
        }
        a = self.encHeaders(_headers)
        sqr_rd = a
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        hr = self.server.additionalHeaders(self.server.Headers, {
            'x-lhm': 'GET'
        })
        res = self.server.postContent(self.url, data=data, headers=hr)
        if res.status_code != 200:
            raise Exception("checkLoginZPinCode failed")
        data = self.decData(res.content)
        return json.loads(data[4:].split(b'\n', 1)[0].decode())['result']
        
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return data
    
    def testTMoreCompactSendMessage(self, to, text):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/S4"
        }
        a = self.encHeaders(_headers)
        
        #sqrd = bytearray.fromhex('92 00 00 00 02 02 84 05 7B B0 19 9D 94 9F EE 69 DD 44 5E AA D3 21 CD 2B 34 EF BB BF 69 6F 67 69 6F 64 67 6A 7A 69 6F 64 66 67 75 79 69 6F 78 67 6A 73 64 66 6B 78 67 68 75 69 78 64 72 67 7A 69 73 6A 73 65 75 67 6A 75 75 75 75 75 75 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
        #print(sqrd)
        #00 02 00 00 92 41 01 04 D9 CB 6A 40 01 75 04 0C 24 7A 87 DC 1A 32 92 28 0C D5 B5 FE 42 CE 01 B2 80 23 00 BA B9 C4 A7 8F 99 06 80 D3 A9 ED FB 5D 00 00 00 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 98 CD A2 82 AA E5 3F D9 5F BF B2 9F 9E AD D9 E4
        #8221000d69737375654c696666566965771c18001c2c182163376262303139396439343966656536396464343435656161643332316364326200000000
        
        #sqrd = bytearray.fromhex('92 00 00 00 02 02 84 05 7B B0 19 9D 94 9F EE 69 DD 44 5E AA D3 21 CD 2B 34 EF BB BF 69 6F 67 69 6F 64 67 6A 7A 69 6F 64 66 67 75 79 69 6F 78 67 6A 73 64 66 6B 78 67 68 75 69 78 64 72 67 7A 69 73 6A 73 65 75 67 6A 75 75 75 75 75 75 02 00 00 00 00')
        #sqrd = bytearray.fromhex('82 21 01 0B 73 65 6E 64 4D 65 73 73 61 67 65 15 98 05 1C 28 21 63 37 62 62 30 31 39 39 64 39 34 39 66 65 65 36 39 64 64 34 34 35 65 61 61 64 33 32 31 63 64 32 62 36 00 16 00 48 16 64 74 63 68 76 74 76 78 63 74 68 6E 76 79 63 79 6E 40 42 41 4F 20 42 15 00 3B 05 88 13 50 52 45 56 49 45 57 5F 55 52 4C 5F 45 4E 41 42 4C 45 44 04 74 72 75 65 10 61 70 70 5F 76 65 72 73 69 6F 6E 5F 63 6F 64 65 09 31 31 30 31 31 30 33 32 37 15 4E 4F 54 49 46 49 43 41 54 49 4F 4E 5F 44 49 53 41 42 4C 45 44 04 6E 75 6C 6C 12 61 70 70 5F 65 78 74 65 6E 73 69 6F 6E 5F 74 79 70 65 04 6E 75 6C 6C 07 4D 45 4E 54 49 4F 4E 4C 7B 22 4D 45 4E 54 49 4F 4E 45 45 53 22 3A 5B 7B 22 53 22 3A 22 31 37 22 2C 22 45 22 3A 22 32 31 22 2C 22 4D 22 3A 22 75 36 37 63 34 33 32 33 39 63 38 36 35 64 66 63 65 36 61 64 64 62 34 31 63 36 62 33 63 30 65 64 64 22 7D 5D 7D 13 00 00 00 00 00 00 00') #S4?
        #92 41 01 0B C0 5A ?
        #92 41 01 0B C0 5A 6C 8F 29 6D 6A 90 59 38 A0 03 75 
        #92 41 01 06 C0 59 38 2C 9C 50 03 63 7B 
        #92 41 01 0F C0 59 E8 0B 4D 91 E
        #92 41 01 04 D9 CB 6A 40 01
        
        #c7bb0199d949fee69dd445eaad321cd2b
        #u5756b96eef9cbb1963bbe3bfc0aec38a

        #75 04 0C 24 7A 87 DC 1A 32 92 28 0C D5 B5 FE 42 CE mid?
        #                                                                                  C
        sqrd = bytearray.fromhex('02 02 55 7B B0 19 9D 94 9F EE 69 DD 44 5E AA D3 21 CD 2B 14 EF BB BF 54 54 45 54 53 54 53 59 55 54 53 59 55 46 53 59 46 0A 02 00 00 00 00 00 00 00')
        sqrd = bytearray.fromhex('02 00 72 57 56 B9 6E EF 9C EE 19 63 BB E3 BF C0 AE C3 8A 0B EF BB BF 35 37 36 35 34 35 36 34 36 38 34 36 35 34 36 35 0A 02 B4 02 15 02 11 16 C0 D3 B5 FC AD 5E 59 1C 16 FC EF 98 E7 02 15 20 00')
        sqrd = bytearray.fromhex('02 02 08 7B B0 19 9D 94 9F EE 69 DD 44 5E AA D3 21 CD 2B 14 EF BB BF 74 65 73 74 2F 43 41 35 36 38 34 36 35 34 36 35 02 B4 02 15 02 11 16 C0 D3 B5 FC AD 5E 59 1C 16 FC EF 98 E7 02 15 20 00')
        #sqrd = bytearray.fromhex('02 02 08 7B B0 19 9D 94 9F EE 69 DD 44 5E AA D3 21 CD 2B 07 EF BB BF 40 35 0A 0A 02 00 00 00 00')
        sqrd = bytearray.fromhex('92 41 01 09 C0 5A 6C 8F 29 6D 6A 91 40 02 75 D4 04 53 03 D1 CF 30 0E CA 5F 32 FB 1B A8 53 76 75 57 56 B9 6E EF 9C BB 19 63 BB E3 BF C0 AE C3 8A 01 2C 9E 88 40 B4 D2 91 0E CE EF D9 C1 FD 5D 32 B6 17 01 30 BE 88 33 00 01 00 E6 A9 EB A2 F5 99 06 CA EF D9 C1 FD 5D 26 73 63 65 6C 74 73 6D 72 68 69 75 73 6C 69 68 76 69 73 64 63 2C 72 6D 64 75 69 72 68 78 63 6C 63 6B 67 63 72 67 68 00 00')
        sqrd = bytearray.fromhex('82 21 01 0B 73 65 6E 64 4D 65 73 73 61 67 65 15 98 05 1C 28 21 63 37 62 62 30 31 39 39 64 39 34 39 66 65 65 36 39 64 64 34 34 35 65 61 61 64 33 32 31 63 64 32 62 36 00 16 00 48 16 64 74 63 68 76 74 76 78 63 74 68 6E 76 79 63 79 6E 40 42 41 4F 20 42 15 00 3B 05 88 13 50 52 45 56 49 45 57 5F 55 52 4C 5F 45 4E 41 42 4C 45 44 04 74 72 75 65 10 61 70 70 5F 76 65 72 73 69 6F 6E 5F 63 6F 64 65 09 31 31 30 31 31 30 33 32 37 15 4E 4F 54 49 46 49 43 41 54 49 4F 4E 5F 44 49 53 41 42 4C 45 44 04 6E 75 6C 6C 12 61 70 70 5F 65 78 74 65 6E 73 69 6F 6E 5F 74 79 70 65 04 6E 75 6C 6C 07 4D 45 4E 54 49 4F 4E 4C 7B 22 4D 45 4E 54 49 4F 4E 45 45 53 22 3A 5B 7B 22 53 22 3A 22 31 37 22 2C 22 45 22 3A 22 32 31 22 2C 22 4D 22 3A 22 75 36 37 63 34 33 32 33 39 63 38 36 35 64 66 63 65 36 61 64 64 62 34 31 63 36 62 33 63 30 65 64 64 22 7D 5D 7D 13 00 00 00 00 00 00 00')
        #4 -> 1
        #7 -> 4
        #9 -> 6
        #10 -> 7
        #15 -> 12
        #16 -> 13
        #20 -> 16
        
        print(sqrd)
        sqr_rd = sqrd
        _data = bytes(a) + bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        print(data.hex())
        return data