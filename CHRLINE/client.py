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
from .e2ee import E2EE
from .exceptions import LineServiceException

class CHRLINE(Models, Config, API, Thrift, Poll, Object, Timeline, TimelineBiz, Helpers, LineCube, E2EE):

    def __init__(self, authTokenOrEmail=None, password=None, device="CHROMEOS", version=None, os_name=None, os_version=None, noLogin=False, encType=1, debug=False, customDataId=None, phone=None, region=None):
        self.encType = encType
        self.isDebug = debug
        self.customDataId = customDataId
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self)
        Thrift.__init__(self)
        if region is not None:
            self.LINE_SERVICE_REGION = region
            
        if authTokenOrEmail is not None and password is not None:
            self.requestEmailLoginV2(authTokenOrEmail, password)
        elif authTokenOrEmail:
            self.authToken = authTokenOrEmail
        elif phone:
            self.requestPwlessLogin(phone, self.LINE_SERVICE_REGION)
        else:
            if not noLogin:
                sqr_func = self.requestSQR
                if device in self.LOGIN_V2_SUPPORT:
                    sqr_func = self.requestSQR2
                for b in sqr_func():
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
        if self.customDataId is None:
            self.customDataId = self.mid
        system(f"title CHRLINE - {self.profile[20]}")
        self.revision = -1
        self.groups = self.getAllChatMids()[1]

        E2EE.__init__(self)
        Timeline.__init__(self)
        TimelineBiz.__init__(self)
        Poll.__init__(self)
        Object.__init__(self)
        LineCube.__init__(self)
        Helpers.__init__(self)

        self.is_login = True

        self.can_use_square = False
        self.squares = None
        try:
            _squares = self.getJoinedSquares()
            self.can_use_square = True
            self.squares = _squares
        except LineServiceException as e:
            self.log(f'Not support Square: {e.message}')

        self.custom_data = {}
        self.getCustomData()