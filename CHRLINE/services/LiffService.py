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
    
    def sendLiff(self, to, messages):
        token = self.issueLiffView(to)[3]
        liff_headers = {
            'Accept' : 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; G730-U00 Build/JLS36C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Line/9.8.0',
            'Accept-Encoding': 'gzip, deflate',
            'content-Type': 'application/json',
            'X-Requested-With': 'jp.naver.line.android'
        }
        liff_headers["authorization"] = 'Bearer %s'%(token)
        if type(messages) == "list":
            messages = {"messages":messages}
        else:
            messages = {"messages":[messages]}
        resp = self.server.postContent("https://api.line.me/message/v3/share", headers=liff_headers, data=json.dumps(messages))
        return resp.text
        