import gevent.monkey

gevent.monkey.patch_all()

from .exceptions import LineServiceException
from .e2ee import E2EE
from .cube import LineCube
from .helpers import Helpers
from .timelineBiz import TimelineBiz
from .timeline import Timeline
from .object import Object
from .poll import Poll
from .thrift import Thrift
from .api import API
from .config import Config
from .models import Models
from os import system


class CHRLINE(
    Models,
    Config,
    API,
    Thrift,
    Poll,
    Object,
    Timeline,
    TimelineBiz,
    Helpers,
    LineCube,
    E2EE,
):
    def __init__(
        self,
        authTokenOrEmail: str = None,
        password: str = None,
        device: str = "CHROMEOS",
        version: str = None,
        os_name: str = None,
        os_version: str = None,
        noLogin: bool = False,
        encType: int = 1,
        debug: bool = False,
        customDataId: str = None,
        phone: str = None,
        region: str = None,
        forwardedIp: str = None,
        useThrift: bool = False,
    ):
        """Use authToken or Email & Password to Login.
        phone + region to Login secondary devices (and Android).

        ------------------------
        device: `str`
            Line special device name, you can view and add in config.py.
        version: `str`
            The device's version. it may affect some functions.
        os_name: `str`
            Customized system OS name.
        os_version: `str`
            Customized system OS version.
        noLogin: `bool`
            Set whether not to login
        encType: `int`
            Encryption for requests.

            - 0:
                no encryption.
            - 1:
                legy encryption.
        debug: `bool`
            * Developer options *
            For view some params and logs
        customDataId: `str`
            Special the customData id
        forwardedIp: `str`
            Fake ip used to spoof the server.
            ** not necessarily work **
        useThrift: `bool`
            Set whether to use line thrift.
            If true, you must place line thrifts in `services\thrift`.
        """
        self.encType = encType
        self.isDebug = debug
        self.customDataId = customDataId
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self, forwardedIp)
        Thrift.__init__(self)
        self.is_login = False
        self.use_thrift = useThrift
        if region is not None:
            self.LINE_SERVICE_REGION = region

        if authTokenOrEmail is not None and password is not None:
            email_func = self.requestEmailLogin
            if device in self.LOGIN_V2_SUPPORT:
                email_func = self.requestEmailLoginV2
            email_func(authTokenOrEmail, password)
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
        self.checkNextToken(False)
        self.profile = self.getProfile()
        __profile_err = self.checkAndGetValue(self.profile, "error")
        if __profile_err is not None:
            self.log(f"登入失敗... {__profile_err}")
            try:
                for b in self.requestSQR(False):
                    print(b)
            except:
                raise Exception(f"登入失敗... {__profile_err}")
            self.handleNextToken(b)
            return self.initAll()
        self.mid = self.checkAndGetValue(self.profile, "mid", 1)
        __displayName = self.checkAndGetValue(self.profile, "displayName", 20)
        self.log(f"[{__displayName}] 登入成功 ({self.mid})")
        if self.customDataId is None:
            self.customDataId = self.mid
        try:
            system(f"title CHRLINE - {__displayName}")
        except:
            pass
        self.revision = -1
        try:
            self.groups = self.checkAndGetValue(
                self.getAllChatMids(), "memberChatMids", 1
            )
        except Exception as e:
            self.log(f"[getAllChatMids] {e}")
            self.groups = []

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
            self.log(f"Not support Square: {e.message}")

        self.custom_data = {}
        self.getCustomData()
