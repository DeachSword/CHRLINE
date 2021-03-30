from .models import Models
from .config import Config
from .api import API
from .thrift import Thrift
from .poll import Poll
from .object import Object
from .timeline import Timeline
from .helpers import Helpers
from .cube import LineCube
from os import system

class CHRLINE(Models, Config, API, Thrift, Poll, Object, Timeline, Helpers, LineCube):

    def __init__(self, authTokenOrEmail=None, password=None, device="CHROMEOS", version=None, os_name=None, os_version=None, noLogin=False, encType=1):
        self.encType = encType
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self)
        Thrift.__init__(self)
        if authTokenOrEmail is not None and password is not None:
            self.requestEmailLogin(authTokenOrEmail, password)
        elif authTokenOrEmail:
            self.authToken = authTokenOrEmail
        else:
            if not noLogin:
                for b in self.requestSQR():
                    print(b)
        if self.authToken:
            self.initAll()
       

    def initAll(self):
        NOT_SUPPORT_WEBVIEW_DEVICES = ['CHROMEOS']
        self.checkNextToken()
        self.profile = self.getProfile()
        if 'error' in self.profile:
            raise Exception(f"登入失敗... {self.profile['error']}")
        print(f"[{self.profile[20]}] 登入成功 ({self.profile[1]})")
        system(f"title CHRLINE - {self.profile[20]}")
        self.revision = self.getLastOpRevision()
        self.groups = self.getAllChatMids()[1]
        TIMELINE_CHANNEL_ID = "1341209950"
        if self.APP_TYPE in NOT_SUPPORT_WEBVIEW_DEVICES: TIMELINE_CHANNEL_ID = "1341209850"
        self.server.timelineHeaders = {
            'x-line-application': self.server.Headers['x-line-application'],
            'User-Agent': self.server.Headers['User-Agent'],
            'X-Line-Mid': self.profile[1],
            'X-Line-Access': self.authToken,
            'X-Line-ChannelToken': self.issueChannelToken(TIMELINE_CHANNEL_ID)[5] # or 1
        }
        Poll.__init__(self)
        Object.__init__(self)
        Timeline.__init__(self)
        Helpers.__init__(self)
        if self.APP_TYPE not in NOT_SUPPORT_WEBVIEW_DEVICES:
            LineCube.__init__(self)
        
        self.is_login = True
        self.can_use_square = False
        self.squares = None
        _squares = self.getJoinedSquares()
        if 'error' not in _squares:
            self.can_use_square = True
            self.squares = _squares
        else:
            print('Not support Square')
        
        self.custom_data = {}
        self.getCustomData()