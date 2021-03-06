from .models import Models
from .config import Config
from .api import API
from .thrift import Thrift
from .poll import Poll
from .object import Object
from .timeline import Timeline
from .timelineBiz import TimelineBiz
from .helpers import Helpers
from .cube import LineCube
from os import system

class CHRLINE(Models, Config, API, Thrift, Poll, Object, Timeline, TimelineBiz, Helpers, LineCube):

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
        self.checkNextToken()
        self.profile = self.getProfile()
        if 'error' in self.profile:
            self.log(f"登入失敗... {self.profile['error']}")
            try:
                for b in self.requestSQR(False):
                    print(b)
            except:
                raise Exception(f"登入失敗... {self.profile['error']}")
            self.handleNextToken(b)
            return self.initAll()
        self.log(f"[{self.profile[20]}] 登入成功 ({self.profile[1]})")
        self.mid = self.profile[1]
        system(f"title CHRLINE - {self.profile[20]}")
        self.revision = self.getLastOpRevision()
        self.groups = self.getAllChatMids()[1]

        Timeline.__init__(self)
        TimelineBiz.__init__(self)
        Poll.__init__(self)
        Object.__init__(self)
        LineCube.__init__(self)
        Helpers.__init__(self)

        self.is_login = True

        self.can_use_square = False
        self.squares = None
        _squares = self.getJoinedSquares()
        if 'error' not in _squares:
            self.can_use_square = True
            self.squares = _squares
        else:
            self.log('Not support Square')

        self.custom_data = {}
        self.getCustomData()