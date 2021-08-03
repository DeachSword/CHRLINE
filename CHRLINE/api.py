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
from .services.AuthService import AuthService
from .services.SettingsService import SettingsService
from .services.AccessTokenRefreshService import AccessTokenRefreshService

class API(TalkService, ShopService, LiffService, ChannelService, SquareService, BuddyService, PrimaryAccountInitService, AuthService, SettingsService, AccessTokenRefreshService):
    _msgSeq = 0
    url = "https://gf.line.naver.jp/enc"
    
    def __init__(self):
        self.server = Server()
        self.req = requests.session()
        self.req_h2 = httpx.Client(http2=True)
        self.server.Headers = {
            "x-line-application": self.APP_NAME,
            "x-le": self.le,
            "x-lap": "5",
            # "x-lc": "3",
            # "X-LST": "",
            # "X-LCR": "",
            # "X-LOR": "",
            "x-lpv": "1",
            "x-lcs": self._encryptKey,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "content-type": "application/x-thrift; protocol=TBINARY",
            "x-lal": self.LINE_LANGUAGE,
            "x-lhm": "POST"
        }
        self.authToken = None
        self.revision = 0
        self.globalRev = 0
        self.individualRev = 0
        self._msgSeq = 0
        TalkService.__init__(self)
        PrimaryAccountInitService.__init__(self)
        AuthService.__init__(self)
        SettingsService.__init__(self)
        AccessTokenRefreshService.__init__(self)

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
            print(f"Enter Pincode: {res[4]}")
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
        res = self.req.post(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        data = self.tryReadData(data)
        if 'error' in data:
            raise Exception(data['error'])
        sqr = data[1]
        url = self.createSession(sqr)
        yield f"URL: {url}"
        if self.checkQrCodeVerified(sqr):
            b = self.verifyCertificate(sqr, self.getSqrCert())
            isCheck = False
            if b is not None and 'error' in b:
                c = self.createPinCode(sqr)
                yield f"請輸入pincode: {c}"
                if self.checkPinCodeVerified(sqr):
                    isCheck = True
            else:
                isCheck = True
            if isCheck:
                e = self.qrCodeLogin(sqr)
                if isSelf:
                    self.authToken = e
                    print(f"AuthToken: {self.authToken}")
                else:
                    yield e
                    return
                yield self.authToken
                return
            raise Exception('can not check pin code, try again?')
        raise Exception('can not check qr code, try again?')
        
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
        return self.tryReadData(data)

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
        data = self.tryReadData(data)
        pem = data[1]
        self.saveSqrCert(pem)
        print("證書: ", pem)
        _token = data[2]
        return _token
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
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
        return self.tryReadData(data)
        
    def checkLoginZPinCode(self, accessSession):
        _headers = {
            'X-Line-Access': accessSession,
            'x-lpqs': "/Q" #LF1
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
            'x-lpqs': "/S5"
        }
        a = self.encHeaders(_headers)
        sqrd = [130, 33, 1] + self.getStringBytes('getProfile', True)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        tmore = self.TMoreCompactProtocol(data)
        data = tmore.res
        return data