# -*- coding: utf-8 -*-
import json
import time
import os
import qrcode

from .exceptions import LineServiceException

class Helpers(object):

    def __init__(self):
        self.liff_token_cache = {}
    
    def squareMemberIdIsMe(self, squareMemberId):
        if self.can_use_square:
            if squareMemberId in self.squares.get(2, {}).keys():
                return True
            else:
                return False
        else:
            raise Exception('Not support Square')
    
    def sendLiff(self, to, messages, tryConsent=True, forceIssue=False):
        cache_key = f"{to}"
        use_cache = False
        if cache_key not in self.liff_token_cache or forceIssue:
            try:
                liff = self.issueLiffView(to)
            except LineServiceException as e:
                self.log(f'[sendLiff] issueLiffView error: {e}')
                if e.code == 3 and tryConsent:
                    if self.tryConsentLiff(e.metadata[3][1]):
                        return self.sendLiff(to, messages, tryConsent=False)
            except Exception as e:
                return e
            token = liff[3]
            self.log(f'[sendLiff] issue new token for {cache_key}...')
        else:
            token = self.liff_token_cache[cache_key]
            use_cache = True
            self.log(f'[sendLiff] using cache token for {cache_key}', True)
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
        if resp.status_code == 200:
            self.liff_token_cache[cache_key] = token
        elif use_cache:
            return self.sendLiff(to, messages, tryConsent=False, forceIssue=True)
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
        ckStatusCode = lpv != 1
        if lpv == 1:
            if "x-lc" in resp.headers:
                if resp.headers["x-lc"] != status_code:
                    return False
            else:
                ckStatusCode = True
        if ckStatusCode:
            if resp.status_code != status_code:
                return False
        return True
    
    def checkIsVideo(self, filename: str):
        video_suffix = ['.mp4', '.mkv', '.webm']
        for _vs in video_suffix:
            if filename.endswith(_vs):
                return True
        return False

    def getProfileCoverObjIdAndUrl(self, mid: str):
        detail = self.getProfileCoverDetail(mid)['result']
        coverObsInfo = detail['coverObsInfo']
        url = self.LINE_OBS_DOMAIN + f'/r/{coverObsInfo["serviceName"]}/{coverObsInfo["obsNamespace"]}/{coverObsInfo["objectId"]}'
        return url, None, coverObsInfo["objectId"], None

    def genQrcodeImageAndPrint(self, url: str, filename: str=None, output_char: list=['　', '■']):
        if filename is None:
            filename = str(time.time())
        savePath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '.images')
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        savePath = savePath + f"/qr_{filename}.png"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,)
        qr.add_data(url)
        qr.make()
        win_qr_make = lambda x: print(''.join([output_char[1]] + [output_char[0] if y == True else output_char[1] for y in x] + [output_char[1]]))
        fixed_bored = [False for _b in range(len(qr.modules[0]))] # 如果你問我問啥要加這段, 我可以告訴你fk u line >:( 你可以看到qr外面有一圈, 這是讓line讀到的必要條件(啊明明就可以不用 line的判定有夠爛)
        for qr_module in [fixed_bored] + qr.modules + [fixed_bored]:
            win_qr_make(qr_module)
        img = qr.make_image()
        img.save(savePath)
        return savePath
    
    def getMentioneesByMsgData(self, msg: dict):
        a = []
        b = mag[18]
        if b is not None:
            if 'MENTION' in b:
                c = json.loads(b['MENTION'])
                print(c)
                for _m in c['MENTIONEES']:
                    print(_m['M'])
                    a.append(_m['M'])
        return a
    
    def genMentionData(self, mentions: dict):
        """
        - mentions:
            - S: index
            - L: len
            - M: mid
        """
        a = []
        for b in mentions:
            a.append({
                'S': str(b['S']),
                'E': str(b['S'] + b['L']),
                'M': str(b['M']),
            })
        a = {
            'MENTIONEES': a
        }
        return {
            'MENTION': json.dumps(a)
        }