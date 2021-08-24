# -*- coding: utf-8 -*-
from .server import Server
import requests, time, json, rsa, binascii, base64
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
from .services.CallService import CallService
from .services.SecondaryPwlessLoginService import SecondaryPwlessLoginService
from .services.SecondaryPwlessLoginPermitNoticeService import SecondaryPwlessLoginPermitNoticeService

class API(TalkService, ShopService, LiffService, ChannelService, SquareService, BuddyService, PrimaryAccountInitService, AuthService, SettingsService, AccessTokenRefreshService, CallService, SecondaryPwlessLoginService, SecondaryPwlessLoginPermitNoticeService):
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
        CallService.__init__(self)
        SecondaryPwlessLoginService.__init__(self)
        SecondaryPwlessLoginPermitNoticeService.__init__(self)
    
    def requestPwlessLogin(self, phone, pw):
        pwless_code = self.createPwlessSession(phone)
        pwless_code = pwless_code[1]
        print(f'PWLESS SESSION: {pwless_code}')
        certVerify = self.verifyLoginCertificate(pwless_code, self.getCacheData('.pwless', phone))
        if 'error' in certVerify:
            pwless_pincode = self.requestPinCodeVerif(pwless_code)[1]
            print(f'PWLESS PINCODE: {pwless_pincode}')
            certVerify = self.checkPwlessPinCodeVerified(pwless_code)
        if certVerify is not None and 'error' not in certVerify:
            secret, secretPK = self.createSqrSecret(True)
            self.putExchangeKey(pwless_code, secretPK)
            self.requestPaakAuth(pwless_code)
            print(f'need Paak Auth Confind')
            pa = self.checkPaakAuthenticated(pwless_code)
            if pa is not None and 'error' not in pa:
                ek = self.getE2eeKey(pwless_code)
                loginInfo = self.pwlessLoginV2(pwless_code)
                if 'error' not in loginInfo:
                    cert = loginInfo[2]
                    tokenInfo = loginInfo[3]
                    token = tokenInfo[1]
                    token2 = tokenInfo[2]
                    mid = loginInfo[5]
                else:
                    loginInfo = self.pwlessLogin(pwless_code)
                    token = loginInfo[1]
                    cert = loginInfo[2]
                    mid = loginInfo[4]
                self.authToken = token
                self.decodeE2EEKeyV1(ek[1], secret, mid)
                self.saveCacheData('.pwless', phone, cert)
                print(f'Auth Token: {self.authToken}')
                return True
        raise Exception('login failed.')

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

    def requestEmailLoginV2(self, email, pw):
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
        secret, secretPK = self.createSqrSecret(True)
        pincode = b"1314520"
        _secret = self._encryptAESECB(self.getSHA256Sum(pincode), base64.b64decode(secretPK))
        res = self.loginV2(keynm, crypto, _secret, deviceName=self.SYSTEM_NAME, cert=certificate)
        if res.get('error', {}).get('code', -1) == 20:
            print(f"can't login: {res['error']['message']}, try use LoginZ...")
            return self.requestEmailLogin(email, pw)
        if 9 not in res:
            verifier = res[3]
            if res[5] == 3:
                print(f'need device confirm')
            print(f"Enter Pincode: {pincode.decode()}")
            e2eeInfo = self.checkLoginV2PinCode(verifier)['metadata']
            try:
                e2eeKeyInfo = self.decodeE2EEKeyV1(e2eeInfo, secret)
            except:
                raise Exception(f"e2eeInfo decode failed, try again")
            blablabao = self.encryptDeviceSecret(base64.b64decode(e2eeInfo['publicKey']), secret, base64.b64decode(e2eeInfo['encryptedKeyChain']))
            e2eeLogin = self.confirmE2EELogin(verifier, blablabao)
            if 'error' not in e2eeLogin:
                res = self.loginV2(None, None, None, deviceName=self.SYSTEM_NAME, verifier=e2eeLogin)
                if res.get('error', {}).get('code', -1) == 20:
                    print(f"can't login: {res['error']['message']}, try use LoginZ...")
                    return self.requestEmailLogin(email, pw)
                self.saveEmailCert(email, res[2])
            else:
                raise Exception(f"confirmE2EELogin failed, try again")
        self.authToken = res[9][1]
        refreshToken = res[9][2]
        self.saveCacheData('.refreshToken', self.authToken, refreshToken)
        print(f"AuthToken: {self.authToken}")
        print(f"RefreshToken: {refreshToken}")
        return True

    def requestSQR(self, isSelf=True):
        sqr = self.createSession()[1]
        url = self.createQrCode(sqr)[1]
        secret, secretUrl = self.createSqrSecret()
        yield f"URL: {url}{secretUrl}"
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
                e = self.qrCodeLogin(sqr, secret)
                print(e)
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
        
    def createSession(self):
        params = []
        sqrd = self.generateDummyProtocol('createSession', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1' ,sqrd, 3)
    
    def createQrCode(self, qrcode):
        params = [
            [12, 1, [
                [11, 1, qrcode]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createQrCode', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1' ,sqrd, 3)
        
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
        
    def qrCodeLogin(self, qrcode, secret):
        _headers = {
            "x-lpqs": "/acct/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 11, 113, 114, 67, 111, 100, 101, 76, 111, 103, 105, 110, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        self.APP_TYPE = 'CHANNELGW'
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
        _mid = data[5]
        if data.get(4) is not None:
            self.decodeE2EEKeyV1(data[4], secret, _mid)
        _token = data[2]
        return _token
    
    def qrCodeLoginV2(self, authSessionId, systemName="彥彥好睡",modelName="鴻鴻好暈", autoLoginIsRequired=True):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [11, 2, self.APP_TYPE],
                [11, 3, self.APP_TYPE],
                [2, 4, autoLoginIsRequired]
            ]]
        ]
        sqrd = self.generateDummyProtocol('qrCodeLoginV2', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1" ,sqrd, 3)
        
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
    
    def loginV2(self, keynm, encData, secret, deviceName='Chrome', cert=None, verifier=None):
        loginType = 2
        if verifier is not None:
            loginType = 1
        params = [
            [12, 2, [
                [8, 1, loginType],
                [8, 2, 1], # provider
                [11, 3, keynm],
                [11, 4, encData],
                [2, 5, 0],
                [11, 6, ''],
                [11, 7, deviceName],
                [11, 8, cert],
                [11, 9, verifier],
                [11, 10, secret],
                [8, 11, 1],
                [11, 12, "System Product Name"],
            ]]
        ]
        sqrd = self.generateDummyProtocol('loginV2', params, 3)
        return self.postPackDataAndGetUnpackRespData("/api/v3p/rs" ,sqrd, 3)
        
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
        
    def checkLoginV2PinCode(self, accessSession):
        _headers = {
            'X-Line-Access': accessSession,
            'x-lpqs': "/LF1"
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
            raise Exception("checkLoginV2PinCode failed")
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