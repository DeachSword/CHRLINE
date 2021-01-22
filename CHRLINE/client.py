from .models import Models
from .config import Config
from .api import API
from .thrift import Thrift
from .poll import Poll
from os import system

class CHRLINE(Models, API, Thrift, Config, Poll):

    def __init__(self, authToken=None, device="CHROMEOS", version=None, os_name=None, os_version=None):
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self)
        Thrift.__init__(self)
        if not authToken:
            authToken = self.requestSQR()
        if authToken:
            self.authToken = authToken
            self.initAll()
       

    def initAll(self):
        self.profile = self.getProfile()['getProfile']
        if 'error' in self.profile:
            raise Exception(f"登入失敗... {self.profile['error']}")
        print(f"[{self.profile[20]}] 登入成功 ({self.profile[1]})")
        system(f"title CHRLINE - {self.profile[20]}")
        self.revision = self.getLastOpRevision()
        Poll.__init__(self)