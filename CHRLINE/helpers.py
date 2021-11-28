# -*- coding: utf-8 -*-
import json

class Helpers(object):

    def __init__(self):
        pass
    
    def squareMemberIdIsMe(self, squareMemberId):
        if self.can_use_square:
            if squareMemberId in self.squares.get(2, {}).keys():
                return True
            else:
                return False
        else:
            raise Exception('Not support Square')
    
    def sendLiff(self, to, messages, tryConsent=True):
        liff = self.issueLiffView(to)
        token = liff.get(3)
        if not token:
            error = liff.get('error', {})
            print(f"[sendLiff]{error}")
            if error.get('code') == 3 and tryConsent:
                if self.tryConsentLiff(error['metadata'][3][1]):
                    return self.sendLiff(to, messages, tryConsent=False)
            return error
        liff_headers = {
            'Accept' : 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; G730-U00 Build/JLS36C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Line/9.8.0',
            'Accept-Encoding': 'gzip, deflate',
            'content-Type': 'application/json',
            'X-Requested-With': 'jp.naver.line.android'
        }
        liff_headers["authorization"] = 'Bearer %s'%(token)
        if type(messages) == list:
            messages = {"messages":messages}
        else:
            messages = {"messages":[messages]}
        resp = self.server.postContent("https://api.line.me/message/v3/share", headers=liff_headers, data=json.dumps(messages))
        return resp.text
    
    def tryConsentLiff(self, channelId, on=["P", "CM"], referer=None):
        payload = {
            "on": on,
            "off": []
        }
        data = json.dumps(payload)
        hr = {
            'X-LINE-ChannelId': str(channelId),
            'X-LINE-Access': self.authToken,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36',
            'Content-Type': 'application/json',
            'X-Line-Application': self.APP_NAME,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-TW,en-US;q=0.8'
        }
        if referer is not None:
            hr['referer'] = referer
        r = self.server.postContent("https://access.line.me/dialog/api/permissions", data=data, headers=hr)
        if r.status_code == 200:
            return True
        print(f"tryConsentLiff failed: {r.status_code}")
        return False
    
    def getToType(self, mid):
        """
        USER(0),
        ROOM(1),
        GROUP(2),
        SQUARE(3),
        SQUARE_CHAT(4),
        SQUARE_MEMBER(5),
        BOT(6);
        """
        _u = mid[0]
        if _u == "u":
            return 0
        if _u == "r":
            return 1
        if _u == "c":
            return 2
        if _u == "s":
            return 3
        if _u == "m":
            return 4
        if _u == "p":
            return 5
        if _u == "v":
            return 6

    def getAccessToken(self, client_id, redirect_uri, otp, code):
        data = {
            "client_id": str(client_id), # channel id
            "redirect_uri": redirect_uri, # intent://result#Intent;package=xxx;scheme=lineauth;end",
            "otp": otp, # len 20
            "code": code, # len 20
            "grant_type": "authorization_code"
        }
        hr = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36',
        }
        r = self.server.postContent("https://access.line.me/v2/oauth/accessToken", data=data, headers=hr)
        return r.json['access_token']
    
    def checkRespIsSuccessWithLpv(self, resp, lpv: int = 1, status_code: int = 200):
        if resp.status_code != status_code:
            return False
        if lpv == 1 and resp.headers["x-lc"] != status_code:
            return False
        return True
