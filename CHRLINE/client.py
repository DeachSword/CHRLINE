from .models import Models
from .config import Config
from .api import API
from .thrift import Thrift
from .poll import Poll
from .object import Object
from os import system

class CHRLINE(Models, Config, API, Thrift, Poll, Object):

    def __init__(self, authToken=None, device="CHROMEOS", version=None, os_name=None, os_version=None, noLogin=False):
        Models.__init__(self)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version)
        API.__init__(self)
        Thrift.__init__(self)
        if authToken:
            self.authToken = authToken
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
            raise Exception(f"登入失敗... {self.profile['error']}")
        print(f"[{self.profile[20]}] 登入成功 ({self.profile[1]})")
        system(f"title CHRLINE - {self.profile[20]}")
        self.revision = self.getLastOpRevision()
        self.groups = self.getAllChatMids()[1]
        self.server.timelineHeaders = {
            'x-line-application': self.server.Headers['x-line-application'],
            'User-Agent': self.server.Headers['User-Agent'],
            'X-Line-Mid': self.profile[1],
            'X-Line-Access': self.authToken,
            'X-Line-ChannelToken': self.issueChannelToken()[5] # or 1
        }
        Poll.__init__(self)
        
        self.custom_data = {}
        self.getCustomData()