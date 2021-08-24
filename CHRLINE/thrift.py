from struct import pack, unpack
import binascii

class Thrift(object):
    
    def __init__(self):
        pass
    
    class TBinaryProtocol(object):

        VERSION_MASK = -65536
        VERSION_1 = -2147418112
        TYPE_MASK = 0x000000ff

        def __init__(self, data: bytes = None):
            self.__last_fid = 0
            self.__last_pos = 0
            self.__last_sid = 0
            self.res = None
            self.data = data
            if self.data is not None:
                self.x()

        def readBool(self):
            byte = self.readByte()
            if byte == 0:
                return False
            return True

        def readI16(self):
            buff = self.y(2)
            val, = unpack('!h', buff)
            return val

        def readI32(self):
            buff = self.y(4)
            val, = unpack('!i', buff)
            return val

        def readI64(self):
            buff = self.y(8)
            val, = unpack('!q', buff)
            return val

        def readDouble(self):
            buff = self.y(8)
            val, = unpack('!d', buff)
            return val

        def readBinary(self):
            size = self.readI32()
            s = self.y(size)
            try:
                s = s.decode()
            except:
                pass
            return s

        def readByte(self):
            buff = self.y(1)
            val, = unpack('!b', buff)
            return val

        def readMessageBegin(self):
            sz = self.readI32()
            data = {}
            if sz < 0:
                version = sz & self.VERSION_MASK
                if version != self.VERSION_1:
                    raise Exception('Bad version in readMessageBegin: %d' % (sz))
                type = sz & self.TYPE_MASK
                name = self.readBinary()
                seqid = self.readI32()
            else:
                raise Exception('Bad version in readMessageBegin: %d' % (sz))
            return (name, type, seqid)

        def readFieldBegin(self):
            type = self.readByte()
            if type == 0:
                return (None, type, 0)
            id = self.readI16()
            return (None, type, id)

        def readMapBegin(self):
            ktype = self.readByte()
            vtype = self.readByte()
            size = self.readI32()
            return (ktype, vtype, size)

        def readListBegin(self):
            etype = self.readByte()
            size = self.readI32()
            return (etype, size)

        def x(self):
            name, type, seqid = self.readMessageBegin()
            _, ftype, fid = self.readFieldBegin()
            data = None
            if fid == 0:
                data = self.z(ftype)
            elif fid == 1:
                error = self.z(ftype)
                data = {
                    "error": {
                        "code": error.get(1),
                        "message": error.get(2),
                        "metadata": error.get(3),
                        "_data": error
                    }
                }
            else:
                raise Exception(f"unknown fid: {fid}")
            self.res = data

        def y(self, num: int):
            data = self.data[self.__last_pos:self.__last_pos + num]
            self.__last_pos += num
            return data

        def z(self, ftype: int):
            data = None
            if ftype == 0:
                pass
            if ftype == 2:
                data = self.readBool()
            elif ftype == 3:
                data = self.readByte()
            elif ftype == 4:
                data = self.readDouble()
            elif ftype == 6:
                data = self.readI16()
            elif ftype == 8:
                data = self.readI32()
            elif ftype == 10:
                data = self.readI64()
            elif ftype == 11:
                data = self.readBinary()
            elif ftype == 12:
                data = {}
                while True:
                    _, _ftype, _fid = self.readFieldBegin()
                    if _ftype == 0:
                        break
                    data[_fid] = self.z(_ftype)
            elif ftype == 13:
                ktype, vtype, size = self.readMapBegin()
                data = {}
                for i in range(size):
                    _key = self.z(ktype)
                    _val = self.z(vtype)
                    data[_key] = _val
            elif ftype == 14 or ftype == 15:
                etype, size = self.readListBegin()
                data = []
                for i in range(size):
                    data.append(self.z(etype))
            else:
                raise Exception(f"can't not read type {ftype}")
            return data

    class TCompactProtocol(object):

        class TType(object):
            STOP = 0
            VOID = 1
            BOOL = 2
            BYTE = 3
            I08 = 3
            DOUBLE = 4
            I16 = 6
            I32 = 8
            I64 = 10
            STRING = 11
            UTF7 = 11
            STRUCT = 12
            MAP = 13
            SET = 14
            LIST = 15
            UTF8 = 16
            UTF16 = 17

        class CompactType(object):
            STOP = 0x00
            TRUE = 0x01
            FALSE = 0x02
            BYTE = 0x03
            I16 = 0x04
            I32 = 0x05
            I64 = 0x06
            DOUBLE = 0x07
            BINARY = 0x08
            LIST = 0x09
            SET = 0x0A
            MAP = 0x0B
            STRUCT = 0x0C
        
        CTYPES = {
            TType.STOP: CompactType.STOP,
            TType.BOOL: CompactType.TRUE,  # used for collection
            TType.BYTE: CompactType.BYTE,
            TType.I16: CompactType.I16,
            TType.I32: CompactType.I32,
            TType.I64: CompactType.I64,
            TType.DOUBLE: CompactType.DOUBLE,
            TType.STRING: CompactType.BINARY,
            TType.STRUCT: CompactType.STRUCT,
            TType.LIST: CompactType.LIST,
            TType.SET: CompactType.SET,
            TType.MAP: CompactType.MAP,
        }

        TTYPES = {}
        for k, v in CTYPES.items():
            TTYPES[v] = k
        TTYPES[CompactType.FALSE] = TType.BOOL
        del k
        del v
            
        def __init__(self):
            self.__last_fid = 0
    
        def getFieldHeader(self, type, fid):
            delta = fid - self.__last_fid
            res = []
            if 0 < delta <= 15:
                res.append(delta << 4 | type)
            else:
                res += self.__writeByte(type)
                res += self.__writeI16(fid)
            self.__last_fid = fid
            return res
            
        def readVarint(self, data, return_len=False):
            result = 0
            shift = 0
            i = 0
            while True:
                byte = data[i]
                i += 1
                result |= (byte & 0x7f) << shift
                if byte >> 7 == 0:
                    if return_len:
                        return [result, i]
                    return result
                shift += 7
            
        def writeVarint(self, data):
            out = []
            while True:
                if data & ~0x7f == 0:
                  out.append(data)
                  break
                else:
                  out.append((data & 0xff) | 0x80)
                  data = data >> 7
            return out
            
        def __writeByte(self, byte):
            return list(pack('!b', byte))
                
        def __readVarint(self, data, return_len=False):
            return self.readVarint(data, return_len)
                
        def __readByte(self, data):
            result, = unpack('!b', data[:1])
            return result
            
        def __readUByte(self, data):
            result, = unpack('!B', data)
            return result
            
        def __writeI16(self, i16):
            return self.writeVarint(self.makeZigZag(i16, 16))
            
        def __writeI32(self, i32):
            return self.writeVarint(self.makeZigZag(i32, 32))
            
        def makeZigZag(self, n, bits):
            # checkIntegerLimits(n, bits)
            return (n << 1) ^ (n >> (bits - 1))

        def fromZigZag(self, n):
            return (n >> 1) ^ -(n & 1)
            
        def __readZigZag(self, data, return_len=False):
            if return_len:
                (res, len) = self.__readVarint(data, True)
                return [self.fromZigZag(res), len]
            return self.fromZigZag(self.__readVarint(data))
        
        def readBool(self):
            return self.__bool_value == 0x01
            
        def __readSize(self, data):
            result = self.__readVarint(data, True)
            if result[0] < 0:
                raise Exception("[__readSize] Length < 0")
            return result
        
        def readBinary(self, data):
            (size, len) = self.__readSize(data)
            res = data[len:size + len]
            try:
                res = res.decode()
            except:
                pass
            return [res, len + size + 1]
            
        def __writeUByte(self, byte):
            return list(pack('!B', byte))

        def __writeSize(self, i32):
            return self.writeVarint(i32)
                
        def readFieldBegin(self, data):
            type = data[0]
            offset = 1
            if type & 0x0f == 0x00:
                return (None, 0, 0, offset)
            delta = type >> 4
            if delta == 0:
                _fid = self.__readI16(data[offset:], True)
                fid = _fid[0]
                offset += _fid[1]
            else:
                fid = self.__last_fid + delta
            self.__last_fid = fid
            type = type & 0x0f
            if type == 0x01:
                self.__bool_value = True
            elif type == 0x02:
                self.__bool_value = False
            return (None, type, fid, offset)
        
        def readCollectionBegin(self, data):
            size_type = data[0]
            size = size_type >> 4
            type = size_type & 0x0f
            len = 0
            if size == 15:
                size, len = self.__readSize(data[1:])
            return type, size, len + 1

        def writeCollectionBegin(self, etype, size):
            a = []
            if size <= 14:
                a += self.__writeUByte(size << 4 | self.CTYPES[etype])
            else:
                a += self.__writeUByte(0xf0 | self.CTYPES[etype])
                a += self.__writeSize(size)
            return a

        def writeMapBegin(self, ktype, vtype, size):
            a = []
            if size == 0:
                a += self.__writeByte(0)
            else:
                a += self.__writeSize(size)
                a += self.__writeUByte(self.CTYPES[ktype] << 4 | self.CTYPES[vtype])
            return a
        
        def readDouble(self, data):
            buff = data[:8]
            val, = unpack('<d', buff)
            return val

        readByte = __readByte
        __readI16 = __readZigZag
        readI16 = __readZigZag
        readI32 = __readZigZag
        readI64 = __readZigZag
        readSetBegin = readCollectionBegin
        readListBegin = readCollectionBegin

    class TMoreCompactProtocol(TCompactProtocol):
        """
        Author: YinMo (https://github.com/WEDeach)
        Source: CHRLINE (https://github.com/DeachSword/CHRLINE)
        Version: 1.0.4 (令和最新版)
        """

        def __init__(self, a=None):
            self.__a = []       # 1st init
            self.__b = []       # 1st init
            self.__c = self._b  # 1st init
            self.__d = []       # 2nd init
            self.__e = []       # 2nd init
            self.__f = []       # 3rd init
            self.__h = self._c  # 2nd init
            self.__last_fid = 0 # base fid
            self.__last_pos = 0 # base pos
            self.__last_sid = 0 # base sid
            self._a()           # 4th init
            self.res = None     # base res
            if a is not None:   # not None
                self.d(a)       # for data
            
        def a(self, cArr, b2):
            self.__b[b2] = cArr         # bk array!!
            i2 = 0                      # base init!
            for c2 in cArr:             # 
                if c2 == '0':           #       is 0
                    i2 = (i2 << 1) + 1  #        + 1
                elif c2 == '1':         #       is 1
                    i2 = (i2 << 1) + 2  #        + 2
            self.__a[i2] = b2           # init array

        def b(self):
            i2 = 0                              # base init
            i3 = 0                              # base init
            while True:                         # 
                l2 = self.data[self.__last_pos] # so good!!
                self.__last_pos += 1            # fixed pos
                i2 |= (l2 & 127) << i3          # yea baby!
                if (l2 & 128) != 128:           # come on!!
                    return i2                   # break!!!!
                i3 += 7                         # + 7!!!!!!

        def c(self, p, i2):
            if (i2 == 0):               # is 0!!
                return []               # break!
            bArr = self.data[p:p + i2]  # read!!
            return list(bArr)           # break!

        def d(self, d):
            self.data = d   # base init!
            return self.t() # base init?

        def e(self):
            a = None                                        # base init
            b = None                                        # base init
            c = 0                                           # base init
            fid = self.y()                                  # can i del
            if fid == 0:                                    # 
                pass                                        # no data!!
            elif  fid == 1:                                 # 
                a = self.g(self.w())                        # read data
            elif fid == 2:                                  # 
                a = self.g(self.w())                        # read data
                a = {                                       # 
                    'error': {                              # 
                        'code': a.get(1),                   # error code
                        'message': a.get(2),                # error msg.
                        'metadata': a.get(3),               # error data
                        '_data': a                          # for debug.
                    }                                       # 
                }                                           # 
            elif fid == 6:                                  # 
                a = self.g(self.w())                        # read data
                raise Exception(a)                          # exception!
            else:                                           #
                raise EOFError(f"fid {fid} not implemented")# exception!
            self.res = a                                    # write data
            
        def f(self, n):
            return (n >> 1) ^ -(n & 1) # hmm...
            
        def g(self, t):
            a = None                                                                        # base
            b = None                                                                        # base
            c = 0                                                                           # base
            if t == 2:                                                                      # 
                b = self.b()                                                                # read
                a = bool(b)                                                                 # bool
            elif t == 3:                                                                    # 
                dec = Thrift.TCompactProtocol()                                             # init
                a = dec.readByte(self.data[self.__last_pos:])                               # byte
                self.__last_pos += 1                                                        # fix!
            elif t == 4:
                dec = Thrift.TCompactProtocol()                                             # init
                a = dec.readDouble(self.data[self.__last_pos:])                             # read
                self.__last_pos += 8                                                        # fix!
            elif t == 8:                                                                    # 
                _a = self.x(self.data[self.__last_pos:])                                    # read
                a = self.f(_a)                                                              # int!
            elif t == 10:                                                                   # 
                _a = self.b()                                                               # read
                a = self.f(_a)                                                              # int?
            elif t == 11:                                                                   # 
                a = self.s()                                                                # str!
            elif t == 12:                                                                   # 
                a = {}                                                                      # base
                b = self.b()                                                                # read
                c = self.n(b)                                                               # read
                for d in c:                                                                 # 
                    a[d] = self.g(self.w())                                                 # fld!
            elif t == 13:                                                                   # 
                a = {}                                                                      # base
                c = self.b()                                                                # read
                if c != 0:                                                                  # 
                    d = self.y()                                                            # read
                    t1, t2 = self.q(d)                                                      # read
                    for i in range(c):                                                      # 
                        k = self.g(t1)                                                      # key!
                        v = self.g(t2)                                                      # val!
                        a[k] = v                                                            # dict
            elif t == 14 or t == 15:                                                        # 
                a = []                                                                      # base
                dec = Thrift.TCompactProtocol()                                             # init
                ftype, count, offset = dec.readCollectionBegin(self.data[self.__last_pos:]) # read
                self.__last_pos += offset                                                   # fix!
                for i in range(count):                                                      # 
                    b = self.g(self._d(ftype))                                              # read
                    a.append(b)                                                             # list
            elif t == 16:                                                                   # 
                b = self.b()                                                                # read
                c = -(b & 1) ^ self._e(b, 1)                                                # wtf?
                d = c + self.__last_sid                                                     # fix?
                self.__last_sid = d                                                         # idk.
                a = str(d)                                                                  # str!
            elif t == 17:                                                                   # 
                b = self.b()                                                                # read
                if len(self.__e) > b:                                                       # 
                    a = self.__e[b]                                                         # str?
                else:                                                                       # 
                    print(f"未知mid: {b}")                                                  # ????
            else:                                                                           # 
                raise Exception(f"cAN't rEad TyPE: {t}")                                    # err!
            return a                                                                        # nice

        def m(self):
            a = self.b()                                                            # get count
            for _a in range(a):                                                     # 
                bArr = [self.data[self.__last_pos]]                                 # coooooool
                bArr += self.__h(self.data[self.__last_pos+1:self.__last_pos+17])   # not magic
                self.__e.append(bytes(bArr).decode())                               # wow magic
                self.__last_pos += 17                                               # real pos?
            self.e()                                                                # base init

        def n(self, d):
            a = []              # base init
            i = 0               # base init
            while True:         # 
                b = 1 << i      # set &
                if b > d:       # 
                    break       # break
                elif d & b != 0:# 
                    a.append(i) # add
                i += 1          # + 1
            return a            # break

        def q(self, d):
            return (self._d(d >> 4), self._d(d & 15))   # cool

        def s(self):
            a = self.b()                                                # read value
            b = self.data[self.__last_pos:self.__last_pos + a]          # init first
            try:                                                        # 
                b = b.decode()                                          # any ideas?
            except:                                                     # 
                pass                                                    # lamo idea.
            self.__last_pos += a                                        # fixed pos!
            return b                                                    # - break! -

        def t(self):
            self.__last_pos = 3                                     # fixed pos
            if len(self.data) == 4:                                 # 
                raise Exception(f"無效Data: {self.data} (code: 20)")# 
            a = self.b()                                            # first data
            b = self.c(self.__last_pos, a)                          # 2nd data!!
            self.__d = list(bytes(a << 1))                          # 3rd? no!!!
            d = 0                                                   # base init
            e = 0                                                   # base init
            f = 0                                                   # base init
            g = 0                                                   # base init
            for h in b:                                             # 
                _a = 0                                              # base value!
                _b = 128                                            # base value?
                while _a < 8:                                       # 
                    if h & _b == 0:                                 # 
                        d = (g << 1) + 1                            # + 1
                    else:                                           # 
                        d = (g << 1) + 2                            # + 2
                    if self.__a[d] != 0:                            # 
                        if f >= len(self.__d):                      # 
                            self.__d += [len(self.__d)] * 4         # x 4
                        self.__d[f] = self.__a[d]                   # set
                        f += 1                                      # + 1
                        g = 0                                       # = 0
                    else:                                           # 
                        g = d                                       # set!
                    _b >>= 1                                        # move
                    _a += 1                                         # + 1!
            self.__last_pos += a                                    # fixed pos
            self.m()                                                # base init

        def w(self):
            a = self.__d[self.__last_fid]   # read!
            self.__last_fid += 1            # + 1!!
            return a                        # break

        def x(self, a, b=False):
            c = 0                           # base init
            d = 0                           # base init
            i = 0                           # base init
            while True:                     # 
                e = a[i]                    # read
                i += 1                      # + 1!
                c |= (e & 0x7f) << d        # move
                if e >> 7 == 0:             # 
                    self.__last_pos += i    # + i!
                    if b:                   # 
                        return [c, i]       # break
                    return c                # break
                d += 7                      # + 7!!
        
        def y(self):
            a = self.data[self.__last_pos]  # read!
            self.__last_pos += 1            # + 1!!
            return a                        # break
        
        def z(self):
            if len(self.data) > self.__last_pos:    # Next?
                return True                         # True!
            return False                            # False

        def _a(self):
            self.__a = list(bytes(512))                             # base init
            self.__b = list(bytes(18))                              # base init
            self.__c(['1', '0', '1', '1'], 2)                       # cool yea?
            self.__c(['1', '0', '1', '0', '1', '0', '0', '1'], 3)   # idk why..
            self.__c(['1', '0', '1', '0', '1', '0', '0', '0'], 4)   # too long!
            self.__c(['1', '0', '1', '0', '1', '1', '1'], 6)        # plz make!
            self.__c(['0', '1'], 8)                                 # ez plz!!!
            self.__c(['0', '0'], 10)                                # no! 0 & 0
            self.__c(['1', '0', '1', '0', '0'], 11)                 # what? bin
            self.__c(['1', '1', '0', '1'], 12)                      # stop it!!
            self.__c(['1', '0', '1', '0', '1', '1', '0'], 13)       # aaaaaaaaa
            self.__c(['1', '0', '1', '0', '1', '0', '1'], 14)       # AaAAaaaAa
            self.__c(['1', '1', '0', '0'], 15)                      # * DIED! *
            self.__c(['1', '1', '1'], 16)                           # 1 & 1 & 1
            self.__c(['1', '0', '0'], 17)                           # 1 & 0 & 0

        def _b(self, cArr, b2):
            self.__b[b2] = cArr         # base init
            i2 = 0                      # base init
            for c2 in cArr:             # 
                if c2 == '0':           # 
                    i2 = (i2 << 1) + 1  # + 1!!
                elif c2 == '1':         # 
                    i2 = (i2 << 1) + 2  # + 2!!
            self.__a[i2] = b2           # break

        def _c(self, val):
            return binascii.b2a_hex(val)# magic right?
            
        def _d(self, val):
            if val == 0:                        # 
                return 0                        # break
            if val == 1 or val == 2:            # 
                return 2                        # break
            if val == 3:                        # 
                return 3                        # break
            if val == 4:                        # 
                return 6                        # break
            if val == 5:                        # 
                return 8                        # break
            if val == 6:                        # 
                return 10                       # break
            if val == 7:                        # 
                return 4                        # break
            if val == 8:                        # 
                return 11                       # break
            if val == 9:                        # 
                return 15                       # break
            if val == 10:                       # 
                return 14                       # break
            if val == 11:                       # 
                return 13                       # break
            if val == 12:                       # 
                return 12                       # break
            raise Exception(f'未知type: {val}') # erroe

        def _e(self, val, n):
            if val >= 0:                                # 
                val >>= n                               # >>=?
            else:                                       # 
                val = ((val + 0x10000000000000000) >> n)# wtf?
            return val                                  # ret?

def checkIntegerLimits(i, bits):
    if bits == 8 and (i < -128 or i > 127):
        raise Exception('INVALID_DATA',
                                 "i8 requires -128 <= number <= 127")
    elif bits == 16 and (i < -32768 or i > 32767):
        raise Exception('INVALID_DATA',
                                 "i16 requires -32768 <= number <= 32767")
    elif bits == 32 and (i < -2147483648 or i > 2147483647):
        raise Exception('INVALID_DATA',
                                 "i32 requires -2147483648 <= number <= 2147483647")
    elif bits == 64 and (i < -9223372036854775808 or i > 9223372036854775807):
         raise Exception('INVALID_DATA',
                                  "i64 requires -9223372036854775808 <= number <= 9223372036854775807")