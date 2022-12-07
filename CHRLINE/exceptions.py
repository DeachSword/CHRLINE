# -*- coding: utf-8 -*-


class ChrlineException(Exception):
    pass


class LineServiceException(ChrlineException):
    def __init__(self, data: dict, code=None, reason=None, parameterMap=None, raw=None):
        self.code = data.get("code", -519)  # base code for CHR
        self.message = str(data.get("message", ""))
        self.metadata = data.get("metadata", None)
        self.raw = data.get("raw", data)

        if code is not None:
            self.code = code
        if reason is not None:
            self.message = str(reason)
        if parameterMap is not None:
            self.metadata = parameterMap
        if raw is not None:
            self.raw = raw

        fmt = "Code: {0}"
        if self.message is not None and len(self.message):
            fmt += ", Message: {1}"
        if self.metadata is not None:
            fmt += ", Metadata: {2}"

        super().__init__(fmt.format(self.code, self.message, self.metadata))
