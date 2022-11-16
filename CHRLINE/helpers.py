# -*- coding: utf-8 -*-
import json
import time
import os
import qrcode
import re
import requests

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
            raise Exception("Not support Square")

    def sendLiff(
        self,
        to,
        messages,
        tryConsent=True,
        forceIssue=False,
        liffId="1562242036-RW04okm",
    ):
        cache_key = f"{to}"
        use_cache = False
        if cache_key not in self.liff_token_cache or forceIssue:
            try:
                liff = self.issueLiffView(to, liffId)
            except LineServiceException as e:
                self.log(f"[sendLiff] issueLiffView error: {e}")
                if e.code == 3 and tryConsent:
                    payload = e.metadata
                    consentRequired = self.checkAndGetValue(
                        payload, "consentRequired", 3
                    )
                    channelId = self.checkAndGetValue(consentRequired, "channelId", 1)
                    consentUrl = self.checkAndGetValue(consentRequired, "consentUrl", 2)
                    toType = self.getToType(to)
                    hasConsent = False
                    if toType == 4:
                        hasConsent = self.tryConsentAuthorize(consentUrl)
                    else:
                        hasConsent = self.tryConsentLiff(channelId)
                    if hasConsent:
                        return self.sendLiff(
                            to, messages, tryConsent=False, liffId=liffId
                        )
                raise Exception(f"Failed to send Liff: {to}")
            except Exception as e:
                return e
            token = self.checkAndGetValue(liff, "accessToken", 3)
            self.log(f"[sendLiff] issue new token for {cache_key}...")
        else:
            token = self.liff_token_cache[cache_key]
            use_cache = True
            self.log(f"[sendLiff] using cache token for {cache_key}", True)
        liff_headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 4.4.2; G730-U00 Build/JLS36C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Line/9.8.0",
            "Accept-Encoding": "gzip, deflate",
            "content-Type": "application/json",
            "X-Requested-With": "jp.naver.line.android",
        }
        liff_headers["authorization"] = "Bearer %s" % (token)
        if type(messages) == list:
            messages = {"messages": messages}
        else:
            messages = {"messages": [messages]}
        resp = self.server.postContent(
            "https://api.line.me/message/v3/share",
            headers=liff_headers,
            data=json.dumps(messages),
        )
        if resp.status_code == 200:
            self.liff_token_cache[cache_key] = token
        elif use_cache:
            return self.sendLiff(to, messages, False, True, liffId)
        return resp.text

    def tryConsentLiff(self, channelId, on=None, referer=None):
        if on is None:
            on = ["P", "CM"]
        payload = {"on": on, "off": []}
        data = json.dumps(payload)
        hr = {
            "X-LINE-ChannelId": str(channelId),
            "X-LINE-Access": self.authToken,
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
            "Content-Type": "application/json",
            "X-Line-Application": self.APP_NAME,
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "zh-TW,en-US;q=0.8",
        }
        if referer is not None:
            hr["referer"] = referer
        r = self.server.postContent(
            "https://access.line.me/dialog/api/permissions", data=data, headers=hr
        )
        if r.status_code == 200:
            return True
        print(f"tryConsentLiff failed: {r.status_code}")
        return False

    def tryConsentAuthorize(
        self, consentUrl, allPermission=None, approvedPermission=None
    ):
        if allPermission is None:
            allPermission = ["P", "CM"]
        if approvedPermission is None:
            approvedPermission = ["P", "CM"]
        CHANNEL_ID = None
        CSRF_TOKEN = None
        session = requests.Session()
        hr = {
            "X-LINE-Access": self.authToken,
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
            "X-Line-Application": self.APP_NAME,
        }
        r = session.get(consentUrl, headers=hr)
        if r.status_code == 200:
            resp = r.text
            # GET CSRF TOKEN
            CHANNEL_ID = re.findall(self.CONSENT_CHANNEL_ID_REGEX, resp)[0]
            CSRF_TOKEN = re.findall(self.CONSENT_CSRF_TOKEN_REGEX, resp)[0]
            self.log(f"CHANNEL_ID: {CHANNEL_ID}")
            self.log(f"CSRF_TOKEN: {CSRF_TOKEN}")
        if CHANNEL_ID and CSRF_TOKEN:
            url = "https://access.line.me/oauth2/v2.1/authorize/consent"
            payload = {
                "allPermission": allPermission,
                "approvedPermission": allPermission,
                "channelId": CHANNEL_ID,
                "__csrf": CSRF_TOKEN,
                "__WLS": "",
                "allow": True,
            }
            r = session.post(url, data=payload, headers=hr)
            if r.status_code == 200:
                return True
            print(f"tryConsentAuthorize failed: {r.status_code}")
        else:
            raise Exception(
                f"tryConsentAuthorize failed: STATUS_CODE: {r.status_code}, CHANNEL_ID: {CHANNEL_ID}, CSRF_TOKEN: {CSRF_TOKEN}"
            )
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
            "client_id": str(client_id),  # channel id
            # intent://result#Intent;package=xxx;scheme=lineauth;end",
            "redirect_uri": redirect_uri,
            "otp": otp,  # len 20
            "code": code,  # len 20
            "grant_type": "authorization_code",
        }
        hr = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
        }
        r = self.server.postContent(
            "https://access.line.me/v2/oauth/accessToken", data=data, headers=hr
        )
        return r.json["access_token"]

    def checkRespIsSuccessWithLpv(self, resp, lpv: int = 1, status_code: int = 200):
        ckStatusCode = lpv != 1
        if lpv == 1:
            if "x-lc" in resp.headers:
                if resp.headers["x-lc"] != str(status_code):
                    return False
            else:
                ckStatusCode = True
        if ckStatusCode:
            if resp.status_code != status_code:
                return False
        return True

    def checkIsVideo(self, filename: str):
        video_suffix = [".mp4", ".mkv", ".webm"]
        for _vs in video_suffix:
            if filename.endswith(_vs):
                return True
        return False

    def getProfileCoverObjIdAndUrl(self, mid: str):
        video_obj = None
        video_url = None
        detail = self.getProfileCoverDetail(mid)["result"]
        coverObsInfo = self.checkAndGetValue(
            detail, "coverObsInfo"
        )  # detail['coverObsInfo']
        videoCoverObsInfo = self.checkAndGetValue(
            detail, "videoCoverObsInfo"
        )  # detail['videoCoverObsInfo']
        url = (
            self.LINE_OBS_DOMAIN
            + f'/r/{coverObsInfo["serviceName"]}/{coverObsInfo["obsNamespace"]}/{coverObsInfo["objectId"]}'
        )
        if videoCoverObsInfo is not None:
            video_obj = videoCoverObsInfo["objectId"]
            video_url = (
                self.LINE_OBS_DOMAIN
                + f'/r/{videoCoverObsInfo["serviceName"]}/{videoCoverObsInfo["obsNamespace"]}/{videoCoverObsInfo["objectId"]}'
            )
        return url, video_url, coverObsInfo["objectId"], videoCoverObsInfo["objectId"]

    def getProfilePictureObjIdAndUrl(self, mid: str):
        url = None
        url_video = None
        objectId = mid
        objectId_video = None
        serviceName = "talk"
        obsNamespace = None
        midType = self.getToType(mid)
        if midType == 0:
            obsNamespace = "p"
            objectId_video = f"{mid}/vp"
            # vp.sjpg, vp.small
        elif midType in [1, 2]:
            obsNamespace = "g"
        elif midType in [3, 4, 5]:
            serviceName = "g2"
            obsNamespace = "group"
            if midType == 5:
                obsNamespace = "member"
        else:
            raise ValueError(f"Not support midType: {midType}")
        url = self.LINE_OBS_DOMAIN + f"/r/{serviceName}/{obsNamespace}/{objectId}"
        if objectId_video is not None:
            url_video = (
                self.LINE_OBS_DOMAIN
                + f"/r/{serviceName}/{obsNamespace}/{objectId_video}"
            )
        return url, url_video, objectId, objectId_video

    def checkAndGetValue(self, value, *args):
        for arg in args:
            if type(value) == dict:
                if arg in value:
                    return value[arg]
            else:
                data = getattr(value, str(arg), None)
                if data is not None:
                    return data
                if isinstance(arg, int):
                    data = getattr(value, f"val_{arg}", None)
                    if data is not None:
                        return data
        return None

    def checkAndSetValue(self, value, *args):
        set = args[-1]
        args = args[:-1]
        if not args:
            raise ValueError(f"Invalid arguments: {args}")
        for arg in args:
            if type(value) == dict:
                value[arg] = set
            else:
                setattr(value, str(arg), set)
        return value

    def genQrcodeImageAndPrint(
        self, url: str, filename: str = None, output_char: list = None
    ):
        if output_char is None:
            output_char = ["　", "■"]
        if filename is None:
            filename = str(time.time())
        savePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".images")
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        savePath = savePath + f"/qr_{filename}.png"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        qr.add_data(url)
        qr.make()

        def win_qr_make(x):
            return print(
                "".join(
                    [output_char[1]]
                    + [output_char[0] if y is True else output_char[1] for y in x]
                    + [output_char[1]]
                )
            )

        # 如果你問我問啥要加這段, 我可以告訴你fk u line >:( 你可以看到qr外面有一圈, 這是讓line讀到的必要條件(啊明明就可以不用 line的判定有夠爛)
        fixed_bored = [False for _b in range(len(qr.modules[0]))]
        for qr_module in [fixed_bored] + qr.modules + [fixed_bored]:
            win_qr_make(qr_module)
        img = qr.make_image()
        img.save(savePath)
        return savePath

    def sendMention(self, to, text="", mids=[], prefix=True):
        if type(mids) != list:
            mids = [mids]
        tag = "@chrline"
        str_tag = "@!"
        arr_data = []
        if mids == []:
            raise ValueError(f"Invalid mids: {mids}")
        if str_tag not in text:
            message = text if prefix else ""
            for mid in mids:
                slen = len(message)
                elen = len(message) + len(tag)
                arr = {"S": str(slen), "E": str(elen), "M": mid}
                arr_data.append(arr)
                message += tag
            if not prefix:
                message += text
        else:
            if text.count(str_tag) != len(mids):
                raise ValueError(
                    f"Invalid tag length: {text.count(str_tag)}/{len(mids)}"
                )
            text_data = text.split(str_tag)
            message = ""
            for mid in mids:
                message += str(text_data[mids.index(mid)])
                slen = len(message)
                elen = len(message) + len(tag)
                arr = {"S": str(slen), "E": str(elen), "M": mid}
                arr_data.append(arr)
                message += tag
            message += text_data[-1]
        return self.sendMessage(
            to,
            message,
            contentMetadata={
                "MENTION": str('{"MENTIONEES":' + json.dumps(arr_data) + "}")
            },
        )

    def getMentioneesByMsgData(self, msg: dict):
        a = []
        b = self.checkAndGetValue(msg, "contentMetadata", 18)
        if b is not None:
            if "MENTION" in b:
                c = json.loads(b["MENTION"])
                print(c)
                for _m in c["MENTIONEES"]:
                    print(_m["M"])
                    a.append(_m["M"])
        return a

    def genMentionData(self, mentions: dict):
        """
        - mentions:
            - S: index
            - L: len
            - M: mid
            - A: ALL
        """
        if mentions is None or len(mentions) == 0:
            return None
        a = []
        for b in mentions:
            c = {}
            d = False
            if "A" in b:
                d = True
            c["S"] = str(b["S"])
            c["E"] = str(b["S"] + b["L"])
            if d:
                c["A"] = str(1)
            else:
                c["M"] = str(b["M"])
            a.append(c)
        a = {"MENTIONEES": a}
        return {"MENTION": json.dumps(a)}
