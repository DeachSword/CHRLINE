from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import Crypto.Cipher.PKCS1_OAEP as rsaenc
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
from hashlib import md5, sha1
import xxhash
from datetime import datetime
import struct
import time
import json
import os
import rsa
import binascii
        
class Models(object):

    def __init__(self):
        self.lcsStart = "0005"
        self.le = "18"
        self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0LRokSkGDo8G5ObFfyKiIdPAU5iOpj+UT+A3AcDxLuePyDt8IVp9HpOsJlf8uVk3Wr9fs+8y7cnF3WiY6Ro526hy3fbWR4HiD0FaIRCOTbgRlsoGNC2rthp2uxYad5up78krSDXNKBab8t1PteCmOq84TpDCRmainaZQN9QxzaSvYWUICVv27Kk97y2j3LS3H64NCqjS88XacAieivELfMr6rT2GutRshKeNSZOUR3YROV4THa77USBQwRI7ZZTe6GUFazpocTN58QY8jFYODzfhdyoiym6rXJNNnUKatiSC/hmzdpX8/h4Y98KaGAZaatLAgPMRCe582q4JwHg7rwIDAQAB\n-----END PUBLIC KEY-----"
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.encryptKey = b"DearSakura+2021/"
        self.IV = bytes([78, 9, 72, 62, 56, 245, 255, 114, 128, 18, 123, 158, 251, 92, 45, 51])
        self.cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.d_cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.encEncKey()
        
    def log(self, text):
        print("[{}] {}".format(str(datetime.now()), text))
        
    def genOBSParams(self, newList, returnAs='json', ext='jpg'):
        oldList = {'name': f'CHRLINE-{int(time.time())}.{ext}','ver': '1.0'}
        if returnAs not in ['json','b64','default']:
            raise Exception('Invalid parameter returnAs')
        oldList.update(newList)
        if 'range' in oldList:
            new_range = 'bytes 0-%s\/%s' % ( str(oldList['range']-1), str(oldList['range']) )
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
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.tokens')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.authToken.encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            self.authToken = open(savePath + f"/{fn}", "r").read()
            self.log(f"New Token: {self.authToken}")
            self.checkNextToken()
        return self.authToken

    def handleNextToken(self, newToken):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.tokens')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.authToken.encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(newToken)
        self.authToken = newToken
        self.log(f"New Token: {newToken}")
        self.server.timelineHeaders['X-Line-Access'] = self.authToken
        self.server.timelineHeaders['X-Line-ChannelToken'] = self.issueChannelToken()[5] #need?
        
    def getCustomData(self):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.profile[1].encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            self.custom_data = json.loads(open(savePath + f"/{fn}", "r").read())
        return True
        
    def saveCustomData(self):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = md5(self.profile[1].encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(json.dumps(self.custom_data))
        return True
        
    def getSqrCert(self):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = "cert.pem"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None
        
    def saveSqrCert(self, cert):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = "cert.pem"
        open(savePath + f"/{fn}", "w").write(cert)
        return True
        
    def getEmailCert(self, email):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{email}.crt"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None
        
    def saveEmailCert(self, email, cert):
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.data')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        fn = f"{email}.crt"
        open(savePath + f"/{fn}", "w").write(cert)
        return True
    
    def initWithAndroid(self):
        self.lcsStart = "0008"
        self.le = "7"
        self.PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsMC6HAYeMq4R59e2yRw6\nW1OWT2t9aepiAp4fbSCXzRj7A29BOAFAvKlzAub4oxN13Nt8dbcB+ICAufyDnN5N\nd3+vXgDxEXZ/sx2/wuFbC3B3evSNKR4hKcs80suRs8aL6EeWi+bAU2oYIc78Bbqh\nNzx0WCzZSJbMBFw1VlsU/HQ/XdiUufopl5QSa0S246XXmwJmmXRO0v7bNvrxaNV0\ncbviGkOvTlBt1+RerIFHMTw3SwLDnCOolTz3CuE5V2OrPZCmC0nlmPRzwUfxoxxs\n/6qFdpZNoORH/s5mQenSyqPkmH8TBOlHJWPH3eN1k6aZIlK5S54mcUb/oNRRq9wD\n1wIDAQAB\n-----END PUBLIC KEY-----'
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.encryptKey = b"DearSakura+2021/"
        self.IV = bytes([78, 9, 72, 62, 56, 245, 255, 114, 128, 18, 123, 158, 251, 92, 45, 51])
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
        o = len(data);
        data = [255 & o] + data
        data = [255 & o >> 8] + data
        return data
        
    def encEncKey(self):
        # heh
        a = rsaenc.new(self.key)
        self._encryptKey = self.lcsStart + b64encode(a.encrypt(self.encryptKey)).decode()
        
    def encData(self, data):
        _data = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV).encrypt(pad(data, AES.block_size))
        debug = []
        return _data + self.XQqwlHlXKK(self.encryptKey, _data)
        
    def decData(self, data):
        data = pad(data, AES.block_size)
        _data = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV).decrypt(data)[:-16]
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
            e.append(_i);
            i += 2
        return e
        
    def XQqwlHlXKK(self, e, i):
        r = []
        for o in range(16):
            r.append(92 ^ e[o])
        n = xxhash.xxh32(b'',seed=0)
        s = xxhash.xxh32(b'',seed=0)
        n.update(bytes(r))
        for o in range(16):
            r[o] ^= 106
        s.update(bytes(r))
        s.update(i)
        a = s.hexdigest() # is b8a7c677?
        n.update(bytes(self.pmAWhahfKx(a)))
        c = n.hexdigest() # is 3f97d2f6?
        d = self.pmAWhahfKx(c)
        return bytes(d)
        
    def yVdzCLDwMN(self, d, i):
        return (255 & self.xnEmbaRWhy(d, i)) << 8 | 255 & self.xnEmbaRWhy(d, i+1)
    
        
    def xnEmbaRWhy(self, d, i):
        t = d[i];
        if t > 127:
            t = 0 - (t - 1 ^ 255)
        return t
    
    def generateDummyProtocol(self, name, params, type):
        if type == 3:
            data = [128, 1, 0, 1] + self.getStringBytes(name) + [0, 0, 0, 0]
        elif type == 4:
            data = [130, 33, 00] + self.getStringBytes(name, isCompact=True)
        data += self.generateDummyProtocolData(params, type) + [0]
        return data
    
    def generateDummyProtocolData(self, params, type):
        isCompact = False
        data = []
        tcp = self.TCompactProtocol()
        for param in params:
            # [10, 2, revision]
            _type = param[0]
            _id = param[1]
            _data = param[2]
            if type == 3:
                data += [_type, 0, _id]
                isCompact = False
            elif type == 4:
                data += tcp.getFieldHeader(tcp.CTYPES[_type], _id)
                isCompact = True
            if _type == 8:
                data += self.getIntBytes(_data, isCompact=isCompact)
            elif _type == 10:
                data += self.getIntBytes(_data, 8, isCompact)
            else:
                raise Exception(f"[generateDummyProtocolData] not support type: {_type}")
        return data
        
    def postPackDataAndGetUnpackRespData(self, path: str, bdata: bytes, ttype: int = 3):
        if self.encType == 0:
            _decMode = 0
            headers = self.server.Headers.copy()
            data = bytes(bdata)
            if "x-le" in headers:
                del headers['x-le']
                del headers['x-lcs']
            headers['X-Line-Access'] = self.authToken
            res = self.server.postContent(self.LINE_LEGY_HOST_DOMAIN + path, data=data, headers=headers)
            data = bytes(4) + res.content + bytes(4)
        elif self.encType == 1:
            _headers = {
                'X-Line-Access': self.authToken, 
                'x-lpqs': path
            }
            a = self.encHeaders(_headers)
            b = bdata
            c = a + b
            _data = bytes(c)
            data = self.encData(_data)
            res = self.server.postContent(self.LINE_GF_HOST_DOMAIN + self.LINE_ENCRYPTION_ENDPOINT, data=data, headers=self.server.Headers)
            data = self.decData(res.content)
        else:
            raise Exception(f"Unknown encType: {self.encType}")
        if ttype == 3:
            return self.tryReadData(data)
        elif ttype == 4:
            return self.tryReadTCompactData(data)
        else:
            raise Exception(f"Unknown ThriftType: {ttype}")
        
    def getIntBytes(self, i, l=4, isCompact=False):
        i = int(i)
        if isCompact:
            _compact = self.TCompactProtocol()
            a = _compact.makeZigZag(i, l**2)
            b = _compact.writeVarint(a)
            return b
        _seq = int(i).to_bytes(l, byteorder="big")
        res = []
        for value in _seq:
            res.append(value)
        return res
        
    def getStringBytes(self, text, isCompact=False):
        if text is None:
            text = ""
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
                raise Exception(f"getMagicStringBytes() expected 32, but got {len(val)}")
        return res
        
    def tryReadData(self, data, mode=1):
        _data = {}
        if mode == 0:
            data = bytes(4) + data + bytes(4)
        if data[4] == 128:
            a = 12 + data[11]
            b = data[12:a].decode()
            _data[b] = {}
            c = data[a + 4]
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
                    _data[b] = self.readContainerStruct(data[a + 4:], stopWithFirst=True)[0]
                else:
                    print(f"[tryReadData]不支援Type: {c} => ID: {id}")
            else:
                if c != 0:
                    error = {}
                    if c == 11:
                        t_l = data[a + 10]
                        error = data[a + 11:a + 11 + t_l].decode()
                    else:
                        code = data[a + 10:a + 14]
                        t_l = data[a + 20]
                        error = {
                            'code': int.from_bytes(code, "big"),
                            'message': data[a + 21:a + 21 + t_l].decode(),
                            'metadata': self.readContainerStruct(data[a + 21 + t_l:])
                        }
                        if error['message'] in ["AUTHENTICATION_DIVESTED_BY_OTHER_DEVICE", "REVOKE", "LOG_OUT"]:
                            self.is_login = False
                            raise Exception(f"LOGIN OUT: {error['message']}")
                    _data[b] = {
                        "error": error
                    }
                    print(_data)
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
            kt = data[3] # key type
            a = data[4] # value type
            b, = struct.unpack('!i', data[5:9]) # count
            c = 9
            _d = {}
            if b != 0:
                #print(f"ktype: {kt}")
                #print(f"kvalue: {a}")
                for d in range(b):
                    if True:
                        __key = self.readContainerStruct(bytes([kt, 0, 0]) + data[c:], get_data_len=True, stopWithFirst=True)
                        _key = __key[0][0]
                        vp = c + __key[1] - 3 # value pos
                        __value = self.readContainerStruct(bytes([a, 0, 0]) + data[vp:], get_data_len=True, stopWithFirst=True)
                        _value = __value[0][0]
                        c = vp + __value[1] - 3
                    # old code...
                    elif kt == 8:
                        # f = c + 1
                        # g = data[c + 4]
                        _key = data[c]
                        _value = self.readContainerStruct(bytes([a, 0, 0]) + data[f + 1:])[0]
                        # h = f + 4 + g
                        # _value = data[f + 4:h].decode()
                        c += 5
                    else:
                        g = int.from_bytes(data[f + 1:f + 5], "big") # value len
                        _key = data[c + 1:f + 1].decode()
                        h = f + g + 5
                        if a == 10:
                            __value = int.from_bytes(data[f+1:f+9], "big")
                            _value = __value
                            h = f + 9
                            c = h + 3
                        elif a == 12:
                            __value = self.readContainerStruct(data[f+1:], True)
                            _value = __value[0]
                            h = f + __value[1]
                            c = h
                        elif a == 15:
                            __value = self.readContainerStruct(data[f+1:], True)
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
                        b = self.readContainerStruct(bytes([type, 0, 0]) + data[nextPos:])[0]
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
                    _data[id].append(data[e+4:e+4+f].decode())
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
            if not stopWithFirst:
                if d > 0:
                    nextPos += e
                else:
                    nextPos = 8
        elif data[0] != 0:
            print(f"[readContainerStruct]不支援Type: {data[0]} => ID: {id}")
        if nextPos > 0 and not stopWithFirst:
            data = data[nextPos:]
            if len(data) > 2:
                c = self.readContainerStruct(data, True)
                if c[0]:
                    _data.update(c[0])
                    nextPos += c[1] # lol, why i forget it
                    if c[2] != 0:
                        dataType = c[2]
        if get_data_len:
            return [_data, nextPos, dataType]
        return _data
        
    def tryReadTCompactData(self, data):
        _data = {}
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
                        'message': _data[b][1][2],
                        'metadata': _data[b][1].get(3, None)
                    }
                    if error['message'] in ["AUTHENTICATION_DIVESTED_BY_OTHER_DEVICE", "REVOKE", "LOG_OUT"]:
                        self.is_login = False
                        raise Exception(f"LOGIN OUT: {error['message']}")
                    _data[b] = {
                        "error": error
                    }
                    print(_data)
        return _data
        
    def tryReadTCompactContainerStruct(self, data, id=0, get_data_len=False):
        _data = {}
        _dec = self.TCompactProtocol()
        (fname, ftype, fid, offset) = _dec.readFieldBegin(data)
        nextPos = 0
        fid += id
        if ftype == 1:
            _data[fid] = _dec.readBool()
            nextPos = 1
        elif ftype == 2:
            _data[fid] = _dec.readBool()
            nextPos = 1
        elif ftype == 5:
            (_data[fid], nextPos) = _dec.readI32(data[offset:], True)
            nextPos += 1
        elif ftype == 8:
            (_data[fid], nextPos) = _dec.readBinary(data[offset:])
        elif ftype == 9 or ftype == 10:
            ### todo:
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
            (__data, nextPos) = self.tryReadTCompactContainerStruct(data[offset:], get_data_len=True)
            nextPos += 2
            _data[fid] = __data
        elif ftype != 0:
            print(f"[tryReadTCompactContainerStruct]不支援Type: {ftype} => ID: {fid}")
        if nextPos > 0:
            data = data[nextPos:]
            c = self.tryReadTCompactContainerStruct(data, id=fid, get_data_len=True)
            if c[0]:
                _data.update(c[0])
                nextPos += c[1]
        if get_data_len:
            return [_data, nextPos]
        return _data