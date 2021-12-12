# -*- coding: utf-8 -*-
from .services.TestService import TestService
from .services.TalkService import TalkService
from .services.SquareService import SquareService
from .services.SquareBotService import SquareBotService
from .services.ShopService import ShopService
from .services.SettingsService import SettingsService
from .services.SecondaryPwlessLoginService import SecondaryPwlessLoginService
from .services.SecondaryPwlessLoginPermitNoticeService import \
    SecondaryPwlessLoginPermitNoticeService
from .services.PrimaryAccountInitService import PrimaryAccountInitService
from .services.LiffService import LiffService
from .services.E2EEKeyBackupService import E2EEKeyBackupService
from .services.ChatAppService import ChatAppService
from .services.ChannelService import ChannelService
from .services.CallService import CallService
from .services.BuddyService import BuddyService
from .services.AuthService import AuthService
from .services.AccountAuthFactorEapConnectService import \
    AccountAuthFactorEapConnectService
from .services.AccessTokenRefreshService import AccessTokenRefreshService
from .server import Server
from .exceptions import LineServiceException
import rsa
import requests
import httpx
import base64
import binascii
import json


class API(TalkService, ShopService, LiffService, ChannelService, SquareService, BuddyService, PrimaryAccountInitService, AuthService, SettingsService, AccessTokenRefreshService, CallService, SecondaryPwlessLoginService, SecondaryPwlessLoginPermitNoticeService, ChatAppService, AccountAuthFactorEapConnectService, E2EEKeyBackupService, SquareBotService, TestService):
    _msgSeq = 0
    url = "https://gf.line.naver.jp/enc"

    def __init__(self, forwardedIp=None):
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
            "x-lhm": "POST",
        }
        if forwardedIp is not None:
            self.server.Headers['X-Forwarded-For'] = forwardedIp
        self.authToken = None
        self.revision = 0
        self.globalRev = 0
        self.individualRev = 0
        self._msgSeq = 0
        TalkService.__init__(self)
        ShopService.__init__(self)
        LiffService.__init__(self)
        ChannelService.__init__(self)
        SquareService.__init__(self)
        BuddyService.__init__(self)
        PrimaryAccountInitService.__init__(self)
        AuthService.__init__(self)
        SettingsService.__init__(self)
        AccessTokenRefreshService.__init__(self)
        CallService.__init__(self)
        SecondaryPwlessLoginService.__init__(self)
        SecondaryPwlessLoginPermitNoticeService.__init__(self)
        ChatAppService.__init__(self)
        AccountAuthFactorEapConnectService.__init__(self)
        E2EEKeyBackupService.__init__(self)
        SquareBotService.__init__(self)
        TestService.__init__(self)

    def requestPwlessLogin(self, phone, pw):
        pwless_code = self.checkAndGetValue(self.createPwlessSession(phone), 1, 'val_1')
        print(f'PWLESS SESSION: {pwless_code}')
        cert = self.getCacheData('.pwless', phone)
        try:
            self.verifyLoginCertificate(pwless_code, '' if cert is None else cert)
        except:
            pwless_pincode = self.checkAndGetValue(self.requestPinCodeVerif(pwless_code), 1, 'val_1')
            print(f'PWLESS PINCODE: {pwless_pincode}')
            self.checkPwlessPinCodeVerified(pwless_code)
        secret, secretPK = self.createSqrSecret(True)
        self.putExchangeKey(pwless_code, secretPK)
        self.requestPaakAuth(pwless_code)
        print(f'need Paak Auth Confind')
        self.checkPaakAuthenticated(pwless_code)
        ek = self.getE2eeKey(pwless_code)
        try:
            loginInfo = self.pwlessLoginV2(pwless_code)
            cert = self.checkAndGetValue(loginInfo, 2, 'val_2')
            tokenInfo = self.checkAndGetValue(loginInfo, 3, 'val_3')
            token = self.checkAndGetValue(tokenInfo, 1, 'val_1')
            token2 = self.checkAndGetValue(tokenInfo, 2, 'val_2')
            mid = self.checkAndGetValue(loginInfo, 5, 'val_5')
        except:
            loginInfo = self.pwlessLogin(pwless_code)
            token = self.checkAndGetValue(loginInfo, 1, 'val_1')
            cert = self.checkAndGetValue(loginInfo, 2, 'val_2')
            mid = self.checkAndGetValue(loginInfo, 4, 'val_4')
        self.authToken = token
        print(f'Auth Token: {self.authToken}')
        self.saveCacheData('.pwless', phone, cert)
        self.decodeE2EEKeyV1(self.checkAndGetValue(ek, 1, 'val_1'), secret, mid)
        return True

    def requestEmailLogin(self, email, pw):
        rsaKey = self.getRSAKeyInfo()
        keynm = self.checkAndGetValue(rsaKey, 1, 'val_1')
        nvalue = self.checkAndGetValue(rsaKey, 2, 'val_2')
        evalue = self.checkAndGetValue(rsaKey, 3, 'val_3')
        sessionKey = self.checkAndGetValue(rsaKey, 4, 'val_4')
        certificate = self.getEmailCert(email)
        message = (chr(len(sessionKey)) + sessionKey +
                   chr(len(email)) + email +
                   chr(len(pw)) + pw).encode('utf-8')
        pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
        crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()
        res = self.loginZ(keynm, crypto, self.SYSTEM_NAME, certificate=certificate)
        if self.checkAndGetValue(res, 1, 'val_1') is None:
            print(f"Enter Pincode: {self.checkAndGetValue(res, 4, 'val_4')}")
            verifier = self.checkLoginZPinCode(self.checkAndGetValue(res, 3, 'val_3'))['verifier']
            res = self.loginZ(keynm, crypto, verifier=verifier)
            self.saveEmailCert(email, self.checkAndGetValue(res, 2, 'val_2'))
        self.authToken = self.checkAndGetValue(res, 1, 'val_1')
        print(f"AuthToken: {self.authToken}")
        return True

    def requestEmailLoginV2(self, email, pw):
        rsaKey = self.getRSAKeyInfo()
        keynm = self.checkAndGetValue(rsaKey, 1, 'val_1')
        nvalue = self.checkAndGetValue(rsaKey, 2, 'val_2')
        evalue = self.checkAndGetValue(rsaKey, 3, 'val_3')
        sessionKey = self.checkAndGetValue(rsaKey, 4, 'val_4')
        certificate = self.getEmailCert(email)
        message = (chr(len(sessionKey)) + sessionKey +
                   chr(len(email)) + email +
                   chr(len(pw)) + pw).encode('utf-8')
        pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
        crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()
        secret, secretPK = self.createSqrSecret(True)
        pincode = b"1314520"
        _secret = self._encryptAESECB(self.getSHA256Sum(
            pincode), base64.b64decode(secretPK))
        res = self.loginV2(keynm, crypto, _secret,
                           deviceName=self.SYSTEM_NAME, cert=certificate)
        if self.checkAndGetValue(res, 9, 'val_9') is None:
            verifier = self.checkAndGetValue(res, 3, 'val_3')
            if self.checkAndGetValue(res, 5, 'val_5') == 3:
                print(f'need device confirm')
            print(f"Enter Pincode: {pincode.decode()}")
            e2eeInfo = self.checkLoginV2PinCode(verifier)['metadata']
            try:
                e2eeKeyInfo = self.decodeE2EEKeyV1(e2eeInfo, secret)
            except:
                raise Exception(f"e2eeInfo decode failed, try again")
            blablabao = self.encryptDeviceSecret(base64.b64decode(
                e2eeInfo['publicKey']), secret, base64.b64decode(e2eeInfo['encryptedKeyChain']))
            e2eeLogin = self.confirmE2EELogin(verifier, blablabao)
            try:
                res = self.loginV2(
                    None, None, None, deviceName=self.SYSTEM_NAME, verifier=e2eeLogin)
            except LineServiceException as e:
                print(e)
                if e.code == 20:
                    print(
                        f"can't login: {res['error']['message']}, try use LoginZ...")
                    return self.requestEmailLogin(email, pw)
            self.saveEmailCert(email, self.checkAndGetValue(res, 2, 'val_2'))
        loginInfo = self.checkAndGetValue(res, 9, 'val_9')
        self.authToken = self.checkAndGetValue(loginInfo, 1, 'val_1')
        refreshToken = self.checkAndGetValue(loginInfo, 2, 'val_2')
        self.saveCacheData('.refreshToken', self.authToken, refreshToken)
        print(f"AuthToken: {self.authToken}")
        print(f"RefreshToken: {refreshToken}")
        return True

    def requestSQR(self, isSelf=True):
        sqr = self.checkAndGetValue(self.createSession(), 1, 'val_1')
        print(f'qr: {sqr}')
        url = self.checkAndGetValue(self.createQrCode(sqr), 1, 'val_1')
        secret, secretUrl = self.createSqrSecret()
        url = url + secretUrl
        imgPath = self.genQrcodeImageAndPrint(url)
        yield f"URL: {url}"
        yield f"IMG: {imgPath}"
        if self.checkQrCodeVerified(sqr):
            try:
                self.verifyCertificate(sqr, None)
            except:
                c =  self.checkAndGetValue(self.createPinCode(sqr), 1, 'val_1')
                yield f"請輸入pincode: {c}"
                self.checkPinCodeVerified(sqr)
            e = self.qrCodeLogin(sqr, secret)
            if isSelf:
                self.authToken = e
                print(f"AuthToken: {self.authToken}")
            else:
                yield e
            return
            raise Exception('can not check pin code, try again?')
        raise Exception('can not check qr code, try again?')

    def requestSQR2(self, isSelf=True):
        sqr = self.checkAndGetValue(self.createSession(), 1, 'val_1')
        url = self.checkAndGetValue(self.createQrCode(sqr), 1, 'val_1')
        secret, secretUrl = self.createSqrSecret()
        url = url + secretUrl
        imgPath = self.genQrcodeImageAndPrint(url)
        yield f"URL: {url}"
        yield f"IMG: {imgPath}"
        if self.checkQrCodeVerified(sqr):
            b = self.verifyCertificate(sqr, self.getSqrCert())
            isCheck = False
            if b is not None:
                c = self.createPinCode(sqr)
                yield f"請輸入pincode: {c}"
                if self.checkPinCodeVerified(sqr):
                    isCheck = True
            else:
                isCheck = True
            if isCheck:
                try:
                    e = self.qrCodeLoginV2(
                        sqr, self.APP_TYPE, self.SYSTEM_NAME, True)
                    cert = e[1]
                    self.saveSqrCert(cert)
                    tokenV3Info = e[3]
                    _mid = e[4]
                    bT = e[9]
                    metadata = e[10]
                    e2eeKeyInfo = self.decodeE2EEKeyV1(metadata, secret)
                    authToken = tokenV3Info[1]
                    refreshToken = tokenV3Info[2]
                    self.saveCacheData(
                        '.refreshToken', authToken, refreshToken)
                    print(f"AuthToken: {authToken}")
                    print(f"RefreshToken: {refreshToken}")
                    if isSelf:
                        self.authToken = authToken
                    yield authToken
                    return
                except LineServiceException as e:
                    print(e)
                    yield "try using requestSQR()..."
                    for _ in self.requestSQR(isSelf):
                        yield _
                    return
            raise Exception('can not check pin code, try again?')
        raise Exception('can not check qr code, try again?')

    def createSession(self):
        params = []
        sqrd = self.generateDummyProtocol('createSession', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1', sqrd, 3)

    def createQrCode(self, qrcode):
        params = [
            [12, 1, [
                [11, 1, qrcode]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createQrCode', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1', sqrd, 3)

    def checkQrCodeVerified(self, qrcode):
        _headers = {
            "X-Line-Access": qrcode,
            "x-lpqs": "/acct/lp/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 19, 99, 104, 101, 99, 107, 81, 114, 67, 111, 100, 101,
                86, 101, 114, 105, 102, 105, 101, 100, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        headers = self.server.additionalHeaders(self.server.Headers, {
            'x-lst': '150000'  # timeout
        })
        res = self.server.postContent(
            self.url, data=data, headers=headers)
        if res.status_code == 200:
            return True
        return False

    def verifyCertificate(self, qrcode, cert=None):
        params = [
            [12, 1, [
                [11, 1, qrcode],
                [11, 2, cert],
            ]],
        ]
        sqrd = self.generateDummyProtocol('verifyCertificate', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1', sqrd, 3)

    def createPinCode(self, qrcode):
        params = [
            [12, 1, [
                [11, 1, qrcode],
            ]],
        ]
        sqrd = self.generateDummyProtocol('createPinCode', params, 3)
        return self.postPackDataAndGetUnpackRespData('/acct/lgn/sq/v1', sqrd, 3)

    def checkPinCodeVerified(self, qrcode):
        _headers = {
            "X-Line-Access": qrcode,
            "x-lpqs": "/acct/lp/lgn/sq/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 20, 99, 104, 101, 99, 107, 80, 105, 110, 67, 111, 100,
                101, 86, 101, 114, 105, 102, 105, 101, 100, 0, 0, 0, 0, 12, 0, 1, 11, 0, 1, 0, 0, 0, 66]
        for qr in qrcode:
            sqrd.append(ord(qr))
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        headers = self.server.additionalHeaders(self.server.Headers, {
            'x-lst': '150000'  # timeout
        })
        res = self.server.postContent(
            self.url, data=data, headers=headers)
        if res.status_code == 200:
            return True
        return False

    def qrCodeLogin(self, authSessionId: str, secret: str, autoLoginIsRequired: bool = True):

        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [11, 2, self.SYSTEM_NAME],
                [2, 3, autoLoginIsRequired]
            ]]
        ]
        sqrd = self.generateDummyProtocol('qrCodeLogin', params, 3)
        data = self.postPackDataAndGetUnpackRespData(
            "/acct/lgn/sq/v1", sqrd, 3)
        pem = self.checkAndGetValue(data, 1, 'val_1')
        self.saveSqrCert(pem)
        print("證書: ", pem)
        _token = self.checkAndGetValue(data, 2, 'val_2')
        e2eeInfo = self.checkAndGetValue(data, 4, 'val_4')
        _mid = self.checkAndGetValue(data, 5, 'val_5')
        if e2eeInfo is not None:
            self.decodeE2EEKeyV1(e2eeInfo, secret, _mid)
        return _token

    def qrCodeLoginV2(self, authSessionId, modelName="彥彥好睡", systemName="鴻鴻好暈", autoLoginIsRequired=True):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [11, 2, systemName],
                [11, 3, modelName],
                [2, 4, autoLoginIsRequired]
            ]]
        ]
        sqrd = self.generateDummyProtocol('qrCodeLoginV2', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 3)

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
        res = self.server.postContent(
            self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return bytes(data)

    def getRSAKeyInfo(self, provider=1):
        """
        provider:
         - UNKNOWN(0),
         - LINE(1),
         - NAVER_KR(2),
         - LINE_PHONE(3)
        """
        params = [
            [8, 2, provider],
        ]
        sqrd = self.generateDummyProtocol('getRSAKeyInfo', params, 3)
        return self.postPackDataAndGetUnpackRespData('/api/v3/TalkService.do', sqrd, 3)

    def loginV2(self, keynm, encData, secret, deviceName='Chrome', cert=None, verifier=None):
        loginType = 2
        if verifier is not None:
            loginType = 1
        params = [
            [12, 2, [
                [8, 1, loginType],
                [8, 2, 1],  # provider
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
        return self.postPackDataAndGetUnpackRespData("/api/v3p/rs", sqrd, 3)

    def loginZ(self, keynm, encData, systemName='DeachSword-2021', certificate=None, verifier=None):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('loginZ') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        loginType = 0
        if verifier is not None:
            loginType = 1
        sqrd += [8, 0, 1] + self.getIntBytes(loginType)  # 2 if e2ee
        sqrd += [8, 0, 2] + self.getIntBytes(1)  # provider
        sqrd += [11, 0, 3] + self.getStringBytes(keynm)
        sqrd += [11, 0, 4] + self.getStringBytes(encData)
        sqrd += [2, 0, 5, 0]
        sqrd += [11, 0, 6] + self.getStringBytes("")  # accessLocation
        sqrd += [11, 0, 7] + self.getStringBytes(systemName)
        sqrd += [11, 0, 8] + self.getStringBytes(certificate)
        if verifier is not None:
            sqrd += [11, 0, 9] + self.getStringBytes(verifier)
        # sqrd += [11, 0, 10] + self.getStringBytes("") #secret
        sqrd += [8, 0, 11] + self.getIntBytes(1)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData("/api/v3p/rs" ,sqrd, 3)

    def checkLoginZPinCode(self, accessSession):
        _headers = {
            'X-Line-Access': accessSession,
            'x-lpqs': "/Q"  # LF1
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
            'x-lpqs': self.SECONDARY_DEVICE_LOGIN_VERIFY_PIN_WITH_E2EE
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

    def testTBinary(self):
        _headers = {
            'X-Line-Access': self.authToken,
            'x-lpqs': "/P3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10]
        for value in "getProfile":
            sqrd.append(ord(value))
        sqrd += [0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(
            self.url, data=data, headers=self.server.Headers)
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
        # for value in "fetchOps":
        #    sqrd.append(ord(value))
        # sqrd += [38, 136, 176, 2, 21, 200, 1, 22, 238, 179, 106, 22, 226, 1, 0] fetchOps
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(
            self.url, data=data, headers=self.server.Headers)
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
        res = self.server.postContent(
            self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        tmore = self.TMoreCompactProtocol(data)
        data = tmore.res
        return data
