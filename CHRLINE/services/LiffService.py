# -*- coding: utf-8 -*-
import time
import json

class LiffService(object):
    LIFF_REQ_TYPE = 4
    LIFF_RES_TYPE = 4

    def __init__(self):
        pass
        
    def issueLiffView(self, chatMid, liffId="1562242036-RW04okm", lang='zh_TW', deviceSetting=None):
        context = [12, 1, []]
        if chatMid is not None:
            chat = [11, 1, chatMid]
            if chatMid[0] in ['u', 'c', 'r']:
                chatType = 2
            else:
                chatType = 3
            context = [12, chatType, [chat]]
        params = [
            [12, 1, [
                [11, 1, liffId],
                [12, 2, [
                    context
                ]],
                [11, 3, lang],
                # [12, 4, []], # deviceSetting
                # [11, 5, None] # msit
            ]]
        ]
        sqrd = self.generateDummyProtocol('issueLiffView', params, self.LIFF_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_LIFF_ENDPOINT, sqrd, self.LIFF_RES_TYPE)
        
    def getLiffViewWithoutUserContext(self, liffId="1562242036-RW04okm"):
        b = self.TCompactProtocol()
        sqrd = [130, 33, 00] + self.getStringBytes('getLiffViewWithoutUserContext', isCompact=True)
        sqrd += b.getFieldHeader(12, 1)
        c = self.TCompactProtocol()
        sqrd += c.getFieldHeader(8, 1)
        sqrd += self.getStringBytes(liffId, isCompact=True)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_LIFF_ENDPOINT ,sqrd, ttype=4)
        
    def issueSubLiffView(self, chatMid, msit, liffId="1562242036-RW04okm", lang='zh_TW', deviceSetting=None):
        b = self.TCompactProtocol()
        sqrd = [130, 33, 00] + self.getStringBytes('issueSubLiffView', isCompact=True)
        sqrd += b.getFieldHeader(12, 1)
        c = self.TCompactProtocol()
        sqrd += c.getFieldHeader(8, 1)
        sqrd += self.getStringBytes(liffId, isCompact=True)
        sqrd += c.getFieldHeader(8, 3) + self.getStringBytes(lang, isCompact=True)
        sqrd += c.getFieldHeader(8, 5) + self.getStringBytes(msit, isCompact=True)
        sqrd += c.getFieldHeader(12, 2)
        d = self.TCompactProtocol()
        if chatMid[0] not in ['u', 'c', 'r']:
            sqrd += d.getFieldHeader(12, 3)
        else:
            sqrd += d.getFieldHeader(12, 2)
        e = self.TCompactProtocol()
        sqrd += e.getFieldHeader(8, 1)
        sqrd += self.getStringBytes(chatMid, isCompact=True)
        sqrd += [0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_LIFF_ENDPOINT ,sqrd, ttype=4)