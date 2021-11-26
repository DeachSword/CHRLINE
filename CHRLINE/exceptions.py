# -*- coding: utf-8 -*- 

class ChrlineException(Exception):

    pass

class LineServiceException(ChrlineException):
    
    def __init__(self, data: dict):
        self.code = data.get('code', -519) # base code for CHR
        self.message = data.get('message', '')
        self.metadata = data.get('metadata', None)
        self.raw = data.get('raw', data)

        fmt = 'Code: {0}'
        if self.message is not None and len(self.message):
            fmt += ', Message: {1}'
        if self.metadata is not None:
            fmt += ', Metadata: {2}'

        super().__init__(fmt.format(self.code, self.message, self.metadata))
