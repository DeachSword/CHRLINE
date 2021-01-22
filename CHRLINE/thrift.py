from struct import pack, unpack
from io import BytesIO as BufferIO

class Thrift(object):
    
    def __init__(self):
        pass
    
    class TCompactProtocol(object):
    
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
            
        def __init__(self):
            self.__last_fid = 0
    
        def getFieldHeader(self, type, fid):
            delta = fid - self.__last_fid
            res = []
            if 0 < delta <= 15:
                res.append(delta << 4 | type)
            else:
                self.__writeByte(type)
                self.__writeI16(fid)
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
                
        def __readVarint(self, data, return_len=False):
            return self.readVarint(data, return_len)
                
        def __readUByte(self, data):
            result, = unpack('!B', data)
            return result
            
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
            res = data[len:size + len].decode()
            return [res, len + size + 1]
                
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
            if size == 15:
                size = self.__readSize(data[1:])
            return type, size
        __readI16 = __readZigZag
        readI16 = __readZigZag
        readI32 = __readZigZag
        readI64 = __readZigZag
            