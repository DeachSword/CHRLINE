# -*- coding: utf-8 -*-
import time
import json

class LiffService(object):

    def __init__(self):
        pass
        
    def issueLiffView(self, chatMid, liffId="1562242036-RW04okm", lang='zh_TW', deviceSetting=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/LIFF1"
        }
        a = self.encHeaders(_headers)
        b = self.TCompactProtocol()
        sqrd = [130, 33, 00] + self.getStringBytes('issueLiffView', isCompact=True)
        sqrd += b.getFieldHeader(12, 1)
        c = self.TCompactProtocol()
        sqrd += c.getFieldHeader(8, 1)
        sqrd += self.getStringBytes(liffId, isCompact=True)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadTCompactData(data)['issueLiffView']
        
    def getLiffViewWithoutUserContext(self, liffId="1562242036-RW04okm"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/LIFF1"
        }
        a = self.encHeaders(_headers)
        b = self.TCompactProtocol()
        sqrd = [130, 33, 00] + self.getStringBytes('getLiffViewWithoutUserContext', isCompact=True)
        sqrd += b.getFieldHeader(12, 1)
        c = self.TCompactProtocol()
        sqrd += c.getFieldHeader(8, 1)
        sqrd += self.getStringBytes(liffId, isCompact=True)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadTCompactData(data)['getLiffViewWithoutUserContext']
        
    def issueSubLiffView(self, chatMid, msit, liffId="1562242036-RW04okm", lang='zh_TW', deviceSetting=None):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/LIFF1"
        }
        a = self.encHeaders(_headers)
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent("https://gf.line.naver.jp/enc", data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadTCompactData(data)['issueSubLiffView']