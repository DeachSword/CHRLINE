from .exceptions import LineServiceException
import base64
import binascii
import json
import os
import struct
import time
import urllib
from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import md5, sha1

import axolotl_curve25519 as curve
import Crypto.Cipher.PKCS1_OAEP as rsaenc
import gevent.monkey
import xxhash
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

gevent.monkey.patch_all()


class Models(object):

    def __init__(self):
        self.lcsStart = "0005"
        self.le = "18"
        self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0LRokSkGDo8G5ObFfyKiIdPAU5iOpj+UT+A3AcDxLuePyDt8IVp9HpOsJlf8uVk3Wr9fs+8y7cnF3WiY6Ro526hy3fbWR4HiD0FaIRCOTbgRlsoGNC2rthp2uxYad5up78krSDXNKBab8t1PteCmOq84TpDCRmainaZQN9QxzaSvYWUICVv27Kk97y2j3LS3H64NCqjS88XacAieivELfMr6rT2GutRshKeNSZOUR3YROV4THa77USBQwRI7ZZTe6GUFazpocTN58QY8jFYODzfhdyoiym6rXJNNnUKatiSC/hmzdpX8/h4Y98KaGAZaatLAgPMRCe582q4JwHg7rwIDAQAB\n-----END PUBLIC KEY-----"
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.encryptKey = b"DearSakura+2021/"
        self.IV = bytes([78, 9, 72, 62, 56, 245, 255, 114,
                        128, 18, 123, 158, 251, 92, 45, 51])
        self.cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.d_cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.encEncKey()
        # self.initWithBiz()
        # self.initWithAndroid(4)

    def log(self, text, debugOnly=False):
        if debugOnly and not self.isDebug:
            return
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {text}")

    def genOBSParams(self, newList, returnAs='json', ext='jpg'):
        oldList = {'name': f'CHRLINE-{int(time.time())}.{ext}', 'ver': '1.0'}
        if returnAs not in ['json', 'b64', 'default']:
            raise Exception('Invalid parameter returnAs')
        oldList.update(newList)
        if 'range' in oldList:
            new_range = 'bytes 0-%s\/%s' % (
                str(oldList['range']-1), str(oldList['range']))
            oldList.update({'range': new_range})
        if returnAs == 'json':
            oldList = json.dumps(oldList)
            return oldList
        elif returnAs == 'b64':
            oldList = json.dumps(oldList)
            return b64encode(oldList.encode('utf-8'))
        elif returnAs == 'default':
            return oldList

    def checkNextToken(self):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.tokens')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.authToken.encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            self.authToken = open(savePath + f"/{fn}", "r").read()
            self.log(f"New Token: {self.authToken}")
            self.checkNextToken()
        return self.authToken

    def handleNextToken(self, newToken):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.tokens')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.authToken.encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(newToken)
        self.authToken = newToken
        self.log(f"New Token: {newToken}")
        self.server.timelineHeaders['X-Line-Access'] = self.authToken
        # need?
        self.server.timelineHeaders['X-Line-ChannelToken'] = self.issueChannelToken()[
            5]

    def getCustomData(self):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.customDataId.encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            self.custom_data = json.loads(
                open(savePath + f"/{fn}", "r").read())
        self.log(f'Loading Custom Data: {fn}')
        return True

    def saveCustomData(self):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.customDataId.encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(json.dumps(self.custom_data))
        return True

    def getSqrCert(self):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = "cert.pem"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveSqrCert(self, cert):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = "cert.pem"
        open(savePath + f"/{fn}", "w").write(cert)
        return True

    def getEmailCert(self, email):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{email}.crt"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveEmailCert(self, email, cert):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{email}.crt"
        open(savePath + f"/{fn}", "w").write(cert)
        return True

    def initWithAndroid(self, ver=7):
        if ver == 1:
            self.lcsStart = "0001"
            self.le = "1"
            self.PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCZAAoZNRwIlLUXaUgrgYi8bAYq\nQeFVtXvCNIEm+F4/jAyTU3YoDwmoLaKQ6itGOonykGtwy2k/3BeWefL/q5eUGjVG\nBEa1vBeUNEb4IFU8n9WK3N/GIIPuD6ZiusB+U1FPg/NaEiVX8ldmEQJgmuG1hykk\n2dU3oy7O1M+Kwl1lJQIDAQAB\n-----END PUBLIC KEY-----'
        elif ver == 4:
            self.lcsStart = "0004"
            self.le = "3"  # LegyEncHelper.cpp::decryptStream -> legy xle value
            self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwpAwTVluR1Z++tVzxtOD\nr7XxSv6oqrwvj/8c8SkfFsS8zM7CvIT8j+x+6Qs1JjNRDtYjAwPKO3tO+qOAdA+8\n7FHpx0THDJIi4VYxSZ2uDh0U8Luxh02whwM8gPbPQNN3sEd5++kJ3cCh5eeAIiUd\nDrwPhHzxO8swpBRdxJB/pzibEqpG2U2764JlPscN9D896qmBN6CBRKpXk/MmUDAI\n4xg+uQk/ykn3SNXJSgQwI1UD9KuiR+X9tbJlKRMN5JpUrSuEwRPQQDMaWpSIdCJM\noFqJLNwt9b1RR/JEB01Eup+3QCub20/CObCmHZY6G26KTDHLoTRZ1xzymdYhdJ43\nCwIDAQAB\n-----END PUBLIC KEY-----"
        elif ver == 6:
            self.lcsStart = "0007"
            self.le = "7"
            self.PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5ABzJbexh+HH1+RzVTH4\nDFj8b/42vRqUp0NWLIBAgi5+bAgeJYzyVBI7Pk6YkQnd44HPvUvFMF3V3TocRXLP\nZV/NSawgcAh+VrXe3VIlruCOe14qrd/ZMpTRTxtBJ5aRpVhTsnGpZtGggPYnPh4c\n6V/R7Wxymj4SBZ1Ipsa7ZI83z/XIPFXT38qTJN3UAW5YhjQon1eNbwaxALVajuvI\npUE52aIBi05gE/V0HEoOUjfOg1V6RHFbcchTgmcze6Vbye+7kmdsIboDXnNpm/fJ\nuItub+iwLKSWf9OPc/bYpU4YVBxZXzmSCXFMLeCe2i5wJeMg4iG8NpVpwVv2W+Hb\nQQIDAQAB\n-----END PUBLIC KEY-----'
        elif ver == 7:
            self.lcsStart = "0008"
            self.le = "7"
            self.PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsMC6HAYeMq4R59e2yRw6\nW1OWT2t9aepiAp4fbSCXzRj7A29BOAFAvKlzAub4oxN13Nt8dbcB+ICAufyDnN5N\nd3+vXgDxEXZ/sx2/wuFbC3B3evSNKR4hKcs80suRs8aL6EeWi+bAU2oYIc78Bbqh\nNzx0WCzZSJbMBFw1VlsU/HQ/XdiUufopl5QSa0S246XXmwJmmXRO0v7bNvrxaNV0\ncbviGkOvTlBt1+RerIFHMTw3SwLDnCOolTz3CuE5V2OrPZCmC0nlmPRzwUfxoxxs\n/6qFdpZNoORH/s5mQenSyqPkmH8TBOlHJWPH3eN1k6aZIlK5S54mcUb/oNRRq9wD\n1wIDAQAB\n-----END PUBLIC KEY-----'
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.IV = bytes([78, 9, 72, 62, 56, 245, 255, 114,
                        128, 18, 123, 158, 251, 92, 45, 51])
        self.encryptKey = b"DearSakura+2021/"
        self.encEncKey()
        print(self._encryptKey)

    def encHeaders(self, headers):
        t = headers.keys()
        data = []
        self.mFhrnmxnNF(len(t), data)
        for i in t:
            self.mFhrnmxnNF(len(i), data)
            self.wYEpEYldst(i, data)
            self.mFhrnmxnNF(len(headers[i]), data)
            self.wYEpEYldst(headers[i], data)
        o = len(data)
        data = [255 & o] + data
        data = [255 & o >> 8] + data
        return data

    def decHeaders(self, data):
        headers = {}
        tbin = self.TBinaryProtocol()
        tbin.data = data
        dataLen = tbin.readI16() + 2
        headerLen = tbin.readI16()
        for i in range(headerLen):
            size = tbin.readI16()
            _k = tbin.y(size)
            size = tbin.readI16()
            _v = tbin.y(size)
            headers[_k] = _v
        return headers, data[dataLen:]

    def encEncKey(self):
        # heh
        a = rsaenc.new(self.key)
        self._encryptKey = self.lcsStart + \
            b64encode(a.encrypt(self.encryptKey)).decode()

    def encData(self, data):
        _data = AES.new(self.encryptKey, AES.MODE_CBC,
                        iv=self.IV).encrypt(pad(data, AES.block_size))
        debug = []
        return _data + self.XQqwlHlXKK(self.encryptKey, _data)

    def decData(self, data):
        data = pad(data, AES.block_size)
        _data = AES.new(self.encryptKey, AES.MODE_CBC,
                        iv=self.IV).decrypt(data)[:-16]
        _data = unpad(_data, AES.block_size)
        i = 1
        data = self.yVdzCLDwMN(_data, i)
        i = 3
        return _data

    def mFhrnmxnNF(self, t, e):
        i = 65536
        if t < -1 * 32768 or t >= i:
            raise Exception(t + " is incorrect for i16.")
        e.append(255 & t >> 8)
        e.append(255 & t)

    def wYEpEYldst(self, t, e):
        for i in range(len(t)):
            e.append(ord(t[i]))

    def xZVpUuXFru(t):
        if 8 == len(t):
            return t
        e = ""
        i = 0
        n = 8 - len(t)
        while i < n:
            e += "0"
            i += 1
        return e + t

    def pmAWhahfKx(self, t):
        e = []
        i = 0
        n = len(t)
        while i < n:
            _i = 0
            try:
                _i = int(t[i:i + 2], 16)
            except:
                _i = 16
            e.append(_i)
            i += 2
        return e

    def XQqwlHlXKK(self, e, i):
        r = []
        for o in range(16):
            r.append(92 ^ e[o])
        n = xxhash.xxh32(b'', seed=0)
        s = xxhash.xxh32(b'', seed=0)
        n.update(bytes(r))
        for o in range(16):
            r[o] ^= 106
        s.update(bytes(r))
        s.update(i)
        a = s.hexdigest()  # is b8a7c677?
        n.update(bytes(self.pmAWhahfKx(a)))
        c = n.hexdigest()  # is 3f97d2f6?
        d = self.pmAWhahfKx(c)
        return bytes(d)

    def yVdzCLDwMN(self, d, i):
        return (255 & self.xnEmbaRWhy(d, i)) << 8 | 255 & self.xnEmbaRWhy(d, i+1)

    def xnEmbaRWhy(self, d, i):
        t = d[i]
        if t > 127:
            t = 0 - (t - 1 ^ 255)
        return t

    def generateDummyProtocol(self, name, params, type):
        if type == 3:
            data = [128, 1, 0, 1] + self.getStringBytes(name) + [0, 0, 0, 0]
        elif type == 4:
            data = [130, 33, 00] + self.getStringBytes(name, isCompact=True)
        data += self.generateDummyProtocolField(params, type) + [0]
        return data

    def generateDummyProtocolField(self, params, type):
        isCompact = False
        data = []
        tcp = self.TCompactProtocol()
        for param in params:
            # [10, 2, revision]
            _type = param[0]
            _id = param[1]
            _data = param[2]
            if _data is None:
                continue
            if type == 3:
                data += [_type, 0, _id]
                isCompact = False
            elif type == 4:
                data += tcp.getFieldHeader(tcp.CTYPES[_type], _id)
                isCompact = True
            data += self.generateDummyProtocolData(_data, _type, isCompact)
        return data

    def generateDummyProtocolData(self, _data, type, isCompact=False):
        data = []
        tcp = self.TCompactProtocol()
        ttype = 4 if isCompact else 3
        if type == 2:
            if isCompact:
                _compact = self.TCompactProtocol()
                a = _compact.getFieldHeader(1 if _data == True else 2, 0)
            else:
                data += [1] if _data == True else [0]
        elif type == 8:
            data += self.getIntBytes(_data, isCompact=isCompact)
        elif type == 10:
            data += self.getIntBytes(_data, 8, isCompact=isCompact)
        elif type == 11:
            data += self.getStringBytes(_data, isCompact=isCompact)
        elif type == 12:
            data += self.generateDummyProtocolField(_data, ttype) + [0]
        elif type == 13:
            _ktype = _data[0]
            _vtype = _data[1]
            _vdata = _data[2]
            if isCompact:
                data += tcp.writeMapBegin(_ktype, _vtype, len(_vdata))
            else:
                data += [_ktype, _vtype] + \
                    self.getIntBytes(len(_vdata), isCompact=isCompact)
            for vd in _vdata:
                data += self.generateDummyProtocolData(vd, _ktype, isCompact)
                data += self.generateDummyProtocolData(
                    _vdata[vd], _vtype, isCompact)
        elif type == 14 or type == 15:
            # [11, targetUserMids]
            _vtype = _data[0]
            _vdata = _data[1]
            if isCompact:
                data += tcp.writeCollectionBegin(_vtype, len(_vdata))
            else:
                data += [_vtype] + \
                    self.getIntBytes(len(_vdata), isCompact=isCompact)
            for vd in _vdata:
                data += self.generateDummyProtocolData(vd, _vtype, isCompact)
        else:
            raise Exception(
                f"[generateDummyProtocolData] not support type: {type}")
        return data

    def postPackDataAndGetUnpackRespData(self, path: str, bdata: bytes, ttype: int = 3, encType: int=None, headers: dict=None, access_token: str=None, baseException: dict=None):
        if headers is None:
            headers = self.server.Headers.copy()
        if access_token is None:
            access_token = self.authToken
        ptype = "TBINARY" if ttype == 3 else "TCOMPACT"
        headers["content-type"] = "application/x-thrift; protocol=" + ptype
        headers["x-lal"] = self.LINE_LANGUAGE
        headers["accept"] = "application/x-thrift"
        if encType is None:
            encType = self.encType
        self.log(
            f"--> POST {path} {f'({self.LINE_ENCRYPTION_ENDPOINT})' if encType == 1 else ''}", True)
        if encType == 0:
            data = bytes(bdata)
            if "x-le" in headers:
                del headers['x-le']
                del headers['x-lcs']
            if access_token is not None:
                headers['X-Line-Access'] = access_token
            res = self.req_h2.post(
                self.LINE_GW_HOST_DOMAIN + path, data=data, headers=headers, timeout=180)
            data = res.content
        elif encType == 1:
            if access_token is not None:
                _headers = {
                    'x-lt': access_token,
                    'x-lpqs': path
                }
            else:
                _headers = {
                    'x-lpqs': path
                }
            a = self.encHeaders(_headers)
            b = bdata
            c = a + b
            _data = bytes(c)
            data = self.encData(_data)
            headers['x-cl'] = str(len(data))
            res = self.req.post(
                self.LINE_GF_HOST_DOMAIN + self.LINE_ENCRYPTION_ENDPOINT, data=data, headers=headers)
            data = self.decData(res.content)
        else:
            raise Exception(f"Unknown encType: {encType}")
        self.log(f"<--  {res.status_code}", True)
        self.log(f"{data}", True)
        if res.status_code == 200:
            if res.headers['x-lc'] not in ['200', '410']:
                raise Exception(
                    f'Invalid response code: {res.headers["x-lc"]}')
            if encType == 1:
                respHeaders, data = self.decHeaders(data)
            else:
                respHeaders = {}
            respHeaders.update(res.headers)
            self.log(f"RespHraders: {respHeaders}", True)
            if 'x-line-next-access' in respHeaders:
                print(respHeaders)
                self.handleNextToken(respHeaders['x-line-next-access'])
            res = None
            if ttype == 0:
                pass
            elif ttype == 3:
                res = self.TBinaryProtocol(data, baseException=baseException).res
            elif ttype == 4:
                res = self.TCompactProtocol(data).res
            elif ttype == 5:
                res = self.TMoreCompactProtocol(data).res
            else:
                raise ValueError(f"Unknown ThriftType: {ttype}")
            if type(res) == dict and 'error' in res:
                if res['error']['message'] is not None and (res['error']['message'] in ["EXPIRED", "REVOKE", "LOG_OUT", "AUTHENTICATION_DIVESTED_BY_OTHER_DEVICE", "DEVICE_LOSE", "IDENTIFY_MODIFIED", "V3_TOKEN_CLIENT_LOGGED_OUT", "DELETED_ACCOUNT"] or res['error']['message'].startswith('suspended')):
                    self.is_login = False
                    self.log(f"LOGIN OUT: {res['error']['message']}")
                elif res['error']['code'] == 119:
                    refreshToken = self.getCacheData(
                        '.refreshToken', self.authToken)
                    print(f'try to refresh access token... {refreshToken}')
                    if refreshToken is not None:
                        newToken = self.refreshAccessToken(refreshToken)[1]
                        if 'error' not in newToken:
                            self.handleNextToken(newToken)
                            return self.postPackDataAndGetUnpackRespData(path, bdata, ttype, encType, headers)
                        else:
                            print(f"refresh access token failed. : {newToken}")
                    self.log(f"LOGIN OUT: {res['error']['message']}")
                raise LineServiceException(res['error'])
            return res
        elif res.status_code in [400, 401, 403]:
            self.is_login = False
            raise Exception(f'Invalid response status code: {res.status_code}')
        else:
            print(f"get resp failed: {res.status_code}")
            return None

    def getCurrReqId(self):
        self._msgSeq = 0
        if "_reqseq" in self.custom_data:
            self._msgSeq = self.custom_data["_reqseq"]
        self._msgSeq += 1
        self.custom_data["_reqseq"] = self._msgSeq
        self.saveCustomData()
        return self._msgSeq

    def getIntBytes(self, i, l=4, isCompact=False):
        i = int(i)
        if isCompact:
            _compact = self.TCompactProtocol()
            a = _compact.makeZigZag(i, 32 if l**2 == 16 else 64)
            b = _compact.writeVarint(a)
            return b
        if l**2 == 16:
            res = struct.pack("!i", i)
        else:
            res = struct.pack("!q", i)
        return list(res)

    def getStringBytes(self, text, isCompact=False):
        if text is None:
            text = ""
        if type(text) == bytes:
            pass
        else:
            text = str(text).encode()
        if isCompact:
            _compact = self.TCompactProtocol()
            sqrd = _compact.writeVarint(len(text))
        else:
            sqrd = self.getIntBytes(len(text))
        for value in text:
            sqrd.append(value)
        return sqrd

    def getFloatBytes(self, val):
        res = []
        for value in struct.pack('!d', val):
            res.append(value)
        return res

    def getMagicStringBytes(self, val, rev=False):
        res = []
        i = 0
        if rev:
            res = binascii.b2a_hex(val)
        else:
            if len(val) == 32:
                for ii in range(16):
                    iii = ii * 2
                    i = iii + 1
                    mgc = (int(val[iii], 16) << 4) + int(val[i], 16)
                    res.append(mgc)
            else:
                raise ValueError(
                    f"getMagicStringBytes() expected 32, but got {len(val)}")
        return res

    def createSqrSecret(self, base64Only=False):
        private_key = curve.generatePrivateKey(os.urandom(32))
        public_key = curve.generatePublicKey(private_key)
        secret = urllib.parse.quote(b64encode(public_key).decode())
        version = 1
        if base64Only:
            return [private_key, b64encode(public_key).decode()]
        return [private_key, f"?secret={secret}&e2eeVersion={version}"]

    def getE2EESelfKeyData(self, mid):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.e2eeKeys')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{mid}.json"
        if os.path.exists(savePath + f"/{fn}"):
            return json.loads(open(savePath + f"/{fn}", "r").read())
        keys = self.getE2EEPublicKeys()
        for key in keys:
            _keyData = self.getE2EESelfKeyDataByKeyId(key[2])
            if _keyData is not None:
                return _keyData
        return None

    def getE2EESelfKeyDataByKeyId(self, keyId):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.e2eeKeys')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"key_{keyId}.json"
        if os.path.exists(savePath + f"/{fn}"):
            return json.loads(open(savePath + f"/{fn}", "r").read())
        return None

    def saveE2EESelfKeyData(self, mid, pubK, privK, kI, e2eeVersion):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.e2eeKeys')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{mid}.json"
        fn2 = f"key_{kI}.json"
        data = json.dumps({
            "keyId": kI,
            "privKey": b64encode(privK).decode(),
            "pubKey": b64encode(pubK).decode(),
            "e2eeVersion": e2eeVersion,
        })
        if mid is not None:
            open(savePath + f"/{fn}", "w").write(data)
        open(savePath + f"/{fn2}", "w").write(data)
        return True

    def getCacheData(self, cT, cN, needHash=True):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), cT)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{cN}"
        if needHash:
            fn = md5(cN.encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveCacheData(self, cT, cN, cD, needHash=True):
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), cT)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{cN}"
        if needHash:
            fn = md5(cN.encode()).hexdigest()
        data = cD
        open(savePath + f"/{fn}", "w").write(data)
        return True

    def decodeE2EEKeyV1(self, data, secret, mid=None):
        if 'encryptedKeyChain' in data:
            print("Try to decode E2EE Key")
            encryptedKeyChain = base64.b64decode(data['encryptedKeyChain'])
            # hashKeyChain = data['hashKeyChain']
            keyId = data['keyId']
            publicKey = base64.b64decode(data['publicKey'])
            e2eeVersion = data['e2eeVersion']
            e2eeKey = self.decryptKeyChain(
                publicKey, secret, encryptedKeyChain)
            print(f"E2EE Priv Key: {e2eeKey[0]}")
            print(f"E2EE Pub Key: {e2eeKey[1]}")
            print(f"keyId: {keyId}")
            print(f"e2eeVersion: {e2eeVersion}")
            self.saveE2EESelfKeyData(
                mid, e2eeKey[1], e2eeKey[0], keyId, e2eeVersion)
            return {
                "keyId": keyId,
                "privKey": e2eeKey[0],
                "pubKey": e2eeKey[1],
                "e2eeVersion": e2eeVersion,
            }

    def tryReadData(self, data, mode=1):
        _data = {}
        if mode == 0:
            data = bytes(4) + data + bytes(4)
        if data[4] == 128:
            a = 12 + data[11]
            b = data[12:a].decode()
            _data[b] = {}
            c = data[a + 4]
            if c == 0:
                return None
            id = data[a + 6]
            if id == 0:
                if c == 10:
                    a = int.from_bytes(data[a + 9:a + 15], "big")
                    _data[b] = a
                elif c == 11:
                    d = data[a + 10]
                    e = data[a + 11:a + 11 + d].decode()
                    _data[b] = e
                elif c == 12:
                    _data[b] = self.readContainerStruct(data[a + 7:])
                elif c == 13:
                    _data[b] = self.readContainerStruct(data[a + 4:])
                elif c == 14 or c == 15:
                    _data[b] = self.readContainerStruct(
                        data[a + 4:], stopWithFirst=True)[0]
                else:
                    print(f"[tryReadData]不支援Type: {c} => ID: {id}")
            else:
                if c != 0:
                    error = {}
                    if c == 11:
                        t_l = data[a + 10]
                        error = data[a + 11:a + 11 + t_l].decode()
                    else:
                        ed = self.readContainerStruct(data[a + 4:])[1]
                        error = {
                            'code': ed.get(1),
                            'message': ed.get(2),
                            'metadata': ed.get(3),
                            '_data': ed
                        }
                    _data[b] = {
                        "error": error
                    }
            return _data[b]
        else:
            if data[6:24] == b"x-line-next-access":
                a = data[25]
                b = data[26:26 + a]
                self.handleNextToken(b.decode())
                data = bytes([0, 0, 0, 0]) + data[26 + a:]
                return self.tryReadData(data)
        return _data

    def readContainerStruct(self, data, get_data_len=False, stopWithFirst=False):
        _data = {}
        nextPos = 0
        if len(data) < 3:
            return None
        dataType = data[0]
        id = data[2]
        #print(f"{id} -> {dataType}")
        if data[0] == 2:
            a = data[3]
            if a == 1:
                _data[id] = True
            else:
                _data[id] = False
            nextPos = 4
        elif data[0] == 3:
            a = int.from_bytes(data[3:4], "big")
            _data[id] = a
            nextPos = 4
        elif data[0] == 4:
            a = data[3:11]
            a = struct.unpack('!d', a)[0]
            _data[id] = a
            nextPos = 11
        elif data[0] == 8:
            a, = struct.unpack('!i', data[3:7])
            _data[id] = a
            nextPos = 7
        elif data[0] == 10:
            a, = struct.unpack('!q', data[3:11])
            _data[id] = a
            nextPos = 11
        elif data[0] == 11:
            a = int.from_bytes(data[5:7], "big")
            if a == 0:
                _data[id] = ''
                nextPos = a + 7
            else:
                b = data[7:a+7]
                try:
                    _data[id] = b.decode()
                except:
                    _data[id] = b
                nextPos = a + 7
        elif data[0] == 12:
            if data[3] == 0:
                _data[id] = {}
                nextPos = 4
            else:
                a = self.readContainerStruct(data[3:], True)
                _data[id] = a[0]
                nextPos = a[1] + 4
        elif data[0] == 13:
            # dict
            # 0D 00 24 0B 0B 00 00 00 02 00 00 00 07
            kt = data[3]  # key type
            a = data[4]  # value type
            b, = struct.unpack('!i', data[5:9])  # count
            c = 9
            _d = {}
            if b != 0:
                #print(f"ktype: {kt}")
                #print(f"kvalue: {a}")
                for d in range(b):
                    if True:
                        __key = self.readContainerStruct(
                            bytes([kt, 0, 0]) + data[c:], get_data_len=True, stopWithFirst=True)
                        _key = __key[0][0]
                        vp = c + __key[1] - 3  # value pos
                        __value = self.readContainerStruct(
                            bytes([a, 0, 0]) + data[vp:], get_data_len=True, stopWithFirst=True)
                        _value = __value[0][0]
                        c = vp + __value[1] - 3
                    # old code...
                    elif kt == 8:
                        # f = c + 1
                        # g = data[c + 4]
                        _key = data[c]
                        _value = self.readContainerStruct(
                            bytes([a, 0, 0]) + data[f + 1:])[0]
                        # h = f + 4 + g
                        # _value = data[f + 4:h].decode()
                        c += 5
                    else:
                        g = int.from_bytes(
                            data[f + 1:f + 5], "big")  # value len
                        _key = data[c + 1:f + 1].decode()
                        h = f + g + 5
                        if a == 10:
                            __value = int.from_bytes(data[f+1:f+9], "big")
                            _value = __value
                            h = f + 9
                            c = h + 3
                        elif a == 12:
                            __value = self.readContainerStruct(
                                data[f+1:], True)
                            _value = __value[0]
                            h = f + __value[1]
                            c = h
                        elif a == 15:
                            __value = self.readContainerStruct(
                                data[f+1:], True)
                            _value = __value[0]
                            h = f + __value[1]
                            c = h + 1
                        else:
                            _value = data[f + 5:h].decode()
                            c = h + 3
                    _d[_key] = _value
                _data[id] = _d
                nextPos = c
                # old code...
                # if a in [10, 11]:
                #     nextPos -= 3
            else:
                nextPos = 9
                _data[id] = {}
        elif data[0] == 14:
            type = data[3]
            count = int.from_bytes(data[4:8], "big")
            _data[id] = []
            nextPos = 8
            if count != 0:
                for i in range(count):
                    if type == 8:
                        a = 0
                        b = self.readContainerStruct(
                            bytes([type, 0, 0]) + data[nextPos:])[0]
                    else:
                        a = int.from_bytes(data[nextPos:nextPos + 4], "big")
                        b = data[nextPos + 4:nextPos + 4 + a].decode()
                    _data[id].append(b)
                    nextPos += 4 + a
        elif data[0] == 15:
            type = data[3]
            d = data[7]
            _data[id] = []
            e = 8
            for _d in range(d):
                if type == 8:
                    f = int.from_bytes(data[e:e+4], "big")
                    _data[id].append(f)
                    e += 4
                elif type == 11:
                    f = data[e+3]
                    dd = data[e+4:e+4+f]
                    try:
                        dd = dd.decode()
                    except:
                        pass
                    _data[id].append(dd)
                    e += f + 4
                elif type == 12:
                    f = self.readContainerStruct(data[e:], True)
                    _data[id].append(f[0])
                    if f[2] in [12, 13]:
                        e += f[1] + 1
                    else:
                        e += f[1] + 1
                else:
                    print(f"[readContainerStruct_LIST(15)]不支援Type: {type}")
            nextPos += e
        elif data[0] != 0:
            print(f"[readContainerStruct]不支援Type: {data[0]} => ID: {id}")
        if nextPos > 0 and not stopWithFirst:
            data = data[nextPos:]
            if len(data) > 2:
                c = self.readContainerStruct(data, True)
                if c[0]:
                    _data.update(c[0])
                    nextPos += c[1]  # lol, why i forget it
                    if c[2] != 0:
                        dataType = c[2]
        if get_data_len:
            return [_data, nextPos, dataType]
        return _data

    def tryReadTCompactData(self, data):
        _data = {}
        data = bytes(4) + data
        if data[4] == 130:
            a = 8 + data[7]
            b = data[8:a].decode()
            _data[b] = {}
            _dec = self.TCompactProtocol()
            (fname, ftype, fid, offset) = _dec.readFieldBegin(data[a:])
            offset += a + 1
            if ftype == 12:
                _data[b] = self.tryReadTCompactContainerStruct(data[a:])
                if 0 in _data[b]:
                    _data[b] = _data[b][0]
                else:
                    error = {
                        'code': _data[b][1][1],
                        'message': _data[b][1].get(2, None),
                        'metadata': _data[b][1].get(3, None)
                    }
                    _data[b] = {
                        "error": error
                    }
            return _data[b]
        return None

    def tryReadTCompactContainerStruct(self, data, id=0, get_data_len=False):
        _data = {}
        _dec = self.TCompactProtocol()
        (fname, ftype, fid, offset) = _dec.readFieldBegin(data)
        nextPos = 0
        fid += id
        if ftype == 0:
            pass
        elif ftype == 1:
            _data[fid] = _dec.readBool()
            nextPos = 1
        elif ftype == 2:
            _data[fid] = _dec.readBool()
            nextPos = 1
        elif ftype == 5:
            (_data[fid], nextPos) = _dec.readI32(data[offset:], True)
            nextPos += 1
        elif ftype == 6:
            (_data[fid], nextPos) = _dec.readI64(data[offset:], True)
            #nextPos += -2
        elif ftype == 8:
            (_data[fid], nextPos) = _dec.readBinary(data[offset:])
        elif ftype == 9 or ftype == 10:
            # todo:
            #       ftype == 10 == SET
            (vtype, vsize, vlen) = _dec.readCollectionBegin(data[offset:])
            offset += vlen
            _data[fid] = []
            _nextPos = 0
            for i in range(vsize):
                if vtype == 8:
                    (__data, _nextPos) = _dec.readBinary(data[offset:])
                    _data[fid].append(__data)
                    offset += _nextPos - 1
            nextPos += offset
        elif ftype == 12:
            (__data, nextPos) = self.tryReadTCompactContainerStruct(
                data[offset:], get_data_len=True)
            nextPos += 2
            _data[fid] = __data
        elif ftype != 0:
            print(
                f"[tryReadTCompactContainerStruct]不支援Type: {ftype} => ID: {fid}")
        if nextPos > 0:
            data = data[nextPos:]
            c = self.tryReadTCompactContainerStruct(
                data, id=fid, get_data_len=True)
            if c[0]:
                _data.update(c[0])
                nextPos += c[1]
        if get_data_len:
            return [_data, nextPos]
        return _data

    def tryReadThriftContainerStruct(self, data, id=0, get_data_len=False):
        _data = {}
        _dec = self.TCompactProtocol()
        ftype = data[0] & 15
        fid = (data[0] >> 4) + id
        offset = 1
        nextPos = 0
        if ftype == 0:
            _data = None
        elif ftype == 4:
            _data[fid] = _dec.readDouble(data[offset:])
            nextPos += 8
        elif ftype == 5:
            (_data[fid], nextPos) = _dec.readI32(data[offset:], True)
            nextPos += 1
        elif ftype == 6:
            (_data[fid], nextPos) = _dec.readI64(data[offset:], True)
            nextPos += 1
        elif ftype == 8:
            (_data[fid], nextPos) = _dec.readBinary(data[offset:])
        elif ftype == 9 or ftype == 10:
            (vtype, vsize, vlen) = _dec.readCollectionBegin(data[offset:])
            offset += vlen
            _data[fid] = []
            _nextPos = 0
            for i in range(vsize):
                if vtype == 12:
                    _aaa, _bbb = self.tryReadThriftContainerStruct(
                        data[offset:], get_data_len=True)
                    _data[fid].append(_aaa)
                    offset += _bbb + 1
        else:
            print(
                f"[tryReadThriftContainerStruct]不支援Type: {ftype} => ID: {fid}")
        if nextPos > 0:
            data = data[nextPos:]
            c = self.tryReadThriftContainerStruct(
                data, id=fid, get_data_len=True)
            if c[0] is not None:
                _data.update(c[0])
            nextPos += c[1]
        if get_data_len:
            return [_data, nextPos]
        return _data
