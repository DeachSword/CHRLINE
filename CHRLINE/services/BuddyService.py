# -*- coding: utf-8 -*-
import time
import json

class BuddyService(object):

    def __init__(self):
        pass
        
    def getPromotedBuddyContacts(self, language="zh_TW", country="TW"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/BUDDY3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getPromotedBuddyContacts') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(language)
        sqrd += [11, 0, 3] + self.getStringBytes(country)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getPromotedBuddyContacts']
        