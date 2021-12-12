import base64
import binascii
import io
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
import xxhash
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

from thrift.transport.TTransport import TMemoryBuffer

from .exceptions import LineServiceException
from .serializers.DummyProtocol import DummyProtocol, DummyProtocolData, DummyThrift
from .services.thrift.ap.TBinaryProtocol import \
    TBinaryProtocol as testProtocol2
from .services.thrift.ap.TCompactProtocol import \
    TCompactProtocol as testProtocol
    
from .services.thrift import ttypes, TalkService


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
        tbin = self.TBinaryProtocol(self)
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

    def generateDummyProtocol2(self, params: DummyProtocol, type=3, fixSuccessHeaders: bool=False):
        newParams = []
        c = lambda a: [a.type, a.id, a.data] if a.type in [2, 5, 8, 10, 11] else [c(a2) for a2 in a.data] if a.id is None else [a.type, a.id, [c(a2) for a2 in a.data]] if a.type in [12] else [a.type, a.id, [a.subType[0], a.subType[1], a.data]] if a.type == 13 else [a.type, a.id, [a.subType[0], [c(a2) if isinstance(a2, DummyProtocolData) and a2.type == 12 else a2.data for a2 in a.data]]] if a.type in [14, 15] else (_ for _ in ()).throw(ValueError(f"不支持{a.type}"))
        d = params.data
        newParams.append(c(d))
        if fixSuccessHeaders:
            newParams[0][1] = newParams[0][1] - 1
        return bytes(self.generateDummyProtocolField(newParams, type) + [0])

    def generateDummyProtocolField(self, params, type):
        isCompact = False
        data = []
        tcp = self.TCompactProtocol(self)
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
        tbp = self.TBinaryProtocol(self)
        tcp = self.TCompactProtocol(self)
        ttype = 4 if isCompact else 3
        if type == 2:
            if isCompact:
                _compact = self.TCompactProtocol(self)
                a = _compact.getFieldHeader(1 if _data == True else 2, 0)
            else:
                data += [1] if _data == True else [0]
        elif type == 3:
            if isCompact:
                data += tcp.writeByte(_data)
            else:
                data += tbp.writeByte(_data)
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

    def postPackDataAndGetUnpackRespData(self, path: str, bdata: bytes, ttype: int = 3, encType: int=None, headers: dict=None, access_token: str=None, baseException: dict=None, readWith: str=None):
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
                res = self.TBinaryProtocol(self, data, baseException=baseException)
            elif ttype == 4:
                res = self.TCompactProtocol(self, data, baseException=baseException)
            elif ttype == 5:
                tmore = self.TMoreCompactProtocol(self, data, baseException=baseException)
                res = tmore
            else:
                raise ValueError(f"Unknown ThriftType: {ttype}")
            if self.use_thrift:
                res = self.serializeDummyProtocolToThrift(res.dummyProtocol, baseException, readWith)
            else:
                res = res.res
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
            _compact = self.TCompactProtocol(self)
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
            _compact = self.TCompactProtocol(self)
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

    def tryReadThriftContainerStruct(self, data, id=0, get_data_len=False):
        _data = {}
        _dec = self.TCompactProtocol(self)
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

    def serializeDummyProtocolToThrift(self, data: DummyProtocol, baseException: dict = None, readWith: str = None):
        if readWith is not None:
            new1 = self.generateDummyProtocol2(data, 4, fixSuccessHeaders=True)
            a = eval(readWith)
            a = a()
            e = TMemoryBuffer()
            f = testProtocol(e)
            e._buffer = io.BytesIO(new1)
            a.read(f)
            if a.success:
                return a.success
            raise LineServiceException({}, a.e.code, a.e.reason, a.e.parameterMap, a.e)
        _gen = lambda : DummyThrift()
        def _genFunc(a, b, f):
            c = _gen()
            for d in a.data:
                f(d, c)
            setattr(b, f"val_{a.id}", c)
        a = _gen()
        b = lambda c, refs: _genFunc(c, refs, b) if type(c.data) == list else setattr(refs, f"val_{c.id}", c.data)
        b(data.data, a)
        if self.checkAndGetValue(a, 'val_0') is not None:
            return a.val_0
        _ecode = baseException.get('code', 1)
        _emsg = baseException.get('message', 2)
        _emeta = baseException.get('metadata', 3)
        raise LineServiceException({}, self.checkAndGetValue(a.val_1, f'val_{_ecode}'), self.checkAndGetValue(a.val_1, f'val_{_emsg}'), self.checkAndGetValue(a.val_1, f'val_{_emeta}'), a.val_1)
