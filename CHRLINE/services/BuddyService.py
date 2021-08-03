# -*- coding: utf-8 -*-
import time
import json

class BuddyService(object):

    def __init__(self):
        pass
        
    def getPromotedBuddyContacts(self, language="zh_TW", country="TW"):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getPromotedBuddyContacts') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(language)
        sqrd += [11, 0, 3] + self.getStringBytes(country)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_BUDDY_ENDPOINT ,sqrd)
        