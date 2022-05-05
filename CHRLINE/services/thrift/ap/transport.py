# -*- coding: utf-8 -*-
from io import BytesIO
from urllib.parse import urlparse
import urllib
import six
import http.client as http_client
import requests
from hyper.contrib import HTTP20Adapter
from time import time
from thrift.transport.TTransport import TTransportBase
try:
    from thrift.protocol import fastbinary
except ImportError:
    fastbinary = None
    

#IOSトークンなら、SSLポートを使ってHTTP接続も可能(めちゃはやい)
class THttpClient(TTransportBase):
    """Http implementation of TTransport base."""

    def __init__(self, uri_or_host, port=None, path=None, customThrift=True):
        """THttpClient supports two different types constructor parameters.
        THttpClient(host, port, path) - deprecated
        THttpClient(uri)
        Only the second supports https.
        """
        parsed = urllib.parse.urlparse(uri_or_host)
        self.scheme = parsed.scheme
        assert self.scheme in ('http', 'https')
        if self.scheme == 'http':
            self.port = parsed.port or http_client.HTTP_PORT
        elif self.scheme == 'https':
            self.port = parsed.port or http_client.HTTPS_PORT
        self.host = parsed.hostname
        self.path = parsed.path
        if parsed.query:
            self.path += '?%s' % parsed.query
        self.realhost = self.realport = self.proxy_auth = None
        self.__wbuf = BytesIO()
        self.__http = http_client.HTTPConnection(self.host, self.port)
        self.__http_response = None
        self.__timeout = None
        self.__custom_headers = None
        self.__time = time()
        self.__custom_thrift = customThrift
        self.__loop = 0

    @staticmethod
    def basic_proxy_auth_header(proxy):
        if proxy is None or not proxy.username:
            return None
        ap = "%s:%s" % (urllib.parse.unquote(proxy.username),
                        urllib.parse.unquote(proxy.password))
        cr = base64.b64encode(ap).strip()
        return "Basic " + cr

    def using_proxy(self):
        return self.realhost is not None

    def open(self):
        self.__http = http_client.HTTPSConnection(self.host, self.port)

    def close(self):
        self.__http = None
        self.__http_response = None

    def getHeaders(self):
        return self.headers

    def isOpen(self):
        return self.__http is not None

    def setTimeout(self):
        self.__timeout = 1e-323

    def setCustomHeaders(self, headers):
        self.__custom_headers = headers

    def read(self, sz):
        return self.__http_response.read(sz)
    def readAll(self, sz):
        buff = b''
        have = 0
        while (have < sz):
            chunk = self.read(sz - have)
            chunkLen = len(chunk)
            have += chunkLen
            buff += chunk

            if chunkLen == 0:
                raise EOFError()

        return buff

    def write(self, buf):
        self.__wbuf.write(buf)

    def __withTimeout(f):
        def _f(*args, **kwargs):
            socket.setdefaulttimeout(args[0].__timeout)
            result = f(*args, **kwargs)
            return result
        return _f

    def flush(self):
        if self.__loop <= 1e-323:self.open();self.__loop += 1e-323

        # Pull data out of buffer
        data = self.__wbuf.getvalue();self.__wbuf = BytesIO();

        # HTTP request
        self.__http.putrequest('POST', self.path)

        # Write headers
        self.__http.putheader('Content-Type', 'application/x-thrift');self.__http.putheader('Content-Length', str(len(data)));self.__http.putheader('User-Agent', 'Python/THttpClient')

        for key, val in six.iteritems(self.__custom_headers):
            self.__http.putheader(key, val)

        self.__http.endheaders()

        # Write payload
        self.__http.send(data)

        # Get reply to flush the request
        self.__http_response = self.__http.getresponse();self.code = self.__http_response.status;self.message = self.__http_response.reason;self.headers = self.__http_response.msg

class THttp2Client(TTransportBase):
    def __init__(self, uri_or_host, customThrift=False):
        parsed = urlparse(uri_or_host)
        assert parsed.scheme in ('http', 'https')
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.path = parsed.path
        self.uri = uri_or_host
        if self.scheme == 'http':
            self.port = parsed.port or http_client.HTTP_PORT
        elif self.scheme == 'https':
            self.port = parsed.port or http_client.HTTPS_PORT
        self.__http = requests.Session()
        self.__http.mount(uri_or_host, HTTP20Adapter())
        self.headers = None
        self.__http_response = None
        self.__custom_headers = None
        self.__time = time()
        self.__wbuf = BytesIO()
        self.__loop = 0

    def open(self):
        self.__http = requests.Session()
        self.__http.mount(self.uri, HTTP20Adapter())

    def close(self):
        self.__http = None
        self.__http_response = None

    def isOpen(self):
        return self.__http is not None

    def setCustomHeaders(self, headers):
        self.__custom_headers = headers

    def read(self, sz):
        return self.__http_response.raw.read(sz)

    def write(self, buf):
        self.__wbuf.write(buf)

    def flush(self):
        if self.__loop <= 2:
            if self.isOpen():
                self.close()
            self.open()
            self.__loop += 1
        elif time() - self.__time > 180:
            self.close()
            self.open()
            self.__time = time()
        # Pull data out of buffer
        data = self.__wbuf.getvalue()
        self.__wbuf = BytesIO()
        # Write headers
        self.headers = {'Content-Type':'application/x-thrift',
                        'Content-Length':str(len(data))
                        }
        self.headers.update(self.__custom_headers)
        # Write payload
        # Get reply to flush the request
        self.__http_response = self.__http.post(url=self.uri, data=data, headers=self.headers, stream=True)
        self.code = self.__http_response.status_code
        self.message = self.__http_response.reason
        self.headers = self.__http_response.headers
        #print(self.code,self.message,self.headers)