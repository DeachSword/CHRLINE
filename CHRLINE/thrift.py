from struct import pack, unpack
from io import BytesIO as BufferIO

class Thrift(object):
    
    def __init__(self):
        self.thrifter = self.TCompact()
    
    class TCompact(object):
        def tryReadData(self, data):
            print(data)