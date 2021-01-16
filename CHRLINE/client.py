from .models import Models
from .config import Config
from .api import API
from .thrift import Thrift

class CHRLINE(Models, API, Thrift, Config):

    def __init__(self, authToken=None, device="CHROMEOS", version=None, os_name=None, os_version=None):
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self)
        Thrift.__init__(self)
        if authToken:
            self.authToken = authToken
            self.profile = self.getProfile()['getProfile']
            if 'error' in self.profile:
                raise Exception(f"登入失敗... {self.profile['error']}")
            print(f"[{self.profile[20]}] 登入成功 ({self.profile[1]})")
        else:
            self.authToken = self.requestSQR()
            print(f"AuthToken: {self.authToken}")
       

    def initAll(self):
        pass