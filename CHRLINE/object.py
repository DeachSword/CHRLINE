# -*- coding: utf-8 -*-
import json
import time
import hashlib
from base64 import b64encode
import uuid
import urllib
import requests
import httpx


class Object(object):

    def __init__(self):
        self.Hraders4Obs = {
            'User-Agent': self.server.Headers['User-Agent'],
            'X-Line-Access': self.acquireEncryptedAccessToken().split('\x1e')[1],
            'X-Line-Application': self.server.Headers['x-line-application'],
            'X-Line-Mid': self.mid,
            'x-lal': self.LINE_LANGUAGE,
        }
        self.obsConn = httpx.Client(http2=True, timeout=None)
    """ 
    
    TimelineObs 
    Source: https://github.com/DeachSword/LINE-DemoS-Bot/blob/master/api/obs/obs.py
    
    """

    def updateProfileImage(self, path, storyShare=False, type='p'):
        obsPath = f'talk/p/{self.mid}'
        oType = 'IMAGE'
        params = {}
        is_video = self.checkIsVideo(path)
        hstr = 'DearSakura_%s' % int(time.time() * 1000)
        hstr = hashlib.md5(hstr.encode()).hexdigest()
        filename = "profile.jpg"
        metaData = {
            "profileContext": {
                "storyShare": storyShare
            }
        }
        if type == 'vp':
            params["cat"] = "vp.mp4"  # let server know u have vp.mp4
        is_video = self.checkIsVideo(path)
        if is_video:
            obsPath = f'talk/vp/{self.mid}'
            oType = "VIDEO"
            filename = f"{hstr}.mp4"
            params = {
                "cat": "vp.mp4",
            }
        talkMeta = b64encode(json.dumps(
            metaData).encode('utf-8')).decode('utf-8')
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, talkMeta, filename)
        except Exception as e:
            raise Exception(
                f"updateProfileImage failure: {e}")
        return True

    def updateProfileCover(self, path, storyShare=False):
        hstr = 'DearSakura_%s' % int(time.time() * 1000)
        objId = hashlib.md5(hstr.encode()).hexdigest()
        obsPath = f'myhome/c/{objId}'
        oType = 'IMAGE'
        filename = f"{objId}.jpg"
        params = None
        is_video = self.checkIsVideo(path)
        if is_video:
            obsPath = f'myhome/vc/{objId}'
            oType = 'VIDEO'
            filename = f"{objId}.mp4"
            params = {
                "cat": 'vp.mp4'
            }
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, filename=filename)
        except Exception as e:
            raise Exception(e)
        if is_video:
            _url, _vc_url, _objId, _vc_objId = self.getProfileCoverObjIdAndUrl(
                self.mid)
            home = self.updateProfileCoverById(
                _objId, objId, storyShare=storyShare)
        else:
            home = self.updateProfileCoverById(objId, storyShare=storyShare)
        return home

    def updateChatProfileImage(self, groupId: str, path: str, oType: str = 'IMAGE'):
        obsPath = f'talk/g/{groupId}'
        params = {
            'cat': 'original'
        }
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, filename='profile.jpg')
        except Exception as e:
            raise Exception(
                f"updateChatProfileImage failure: {e}")
        return True

    def updateImageToAlbum(self, mid, albumId, path):
        file = open(path, 'rb').read()
        f_name = hashlib.md5(str(time.time()).encode('utf8')).hexdigest()
        params = {
            'name': f_name + '.20' + time.strftime('%m%d', time.localtime(int(round(time.time())))) + '08' + '.jpg',
            'quality': '100',
            'ver': '2.0',
            'type': 'image'
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': 'image/jpeg',
            'X-Line-Mid': mid,
            'X-Line-Album': albumId,
            'X-Line-Access': self.acquireEncryptedAccessToken()[7:],
            'x-obs-params': self.genOBSParams(params, 'b64')
        })
        r = self.server.postContent(self.LINE_OBS_DOMAIN + '/r/album/a/' + f_name + '.20' + time.strftime(
            '%m%d', time.localtime(int(round(time.time())))) + '08', data=file, headers=hr)

        if r.status_code != 201:
            raise Exception('Add image to album failure.')
        return f_name + '.20' + time.strftime('%m%d', time.localtime(int(round(time.time())))) + '08'

    def uploadObjHome(self, path, type='image', objId=None):
        if type not in ['image', 'video', 'audio']:
            raise Exception('Invalid type value')
        if type == 'image':
            contentType = 'image/jpeg'
        elif type == 'video':
            contentType = 'video/mp4'
        elif type == 'audio':
            contentType = 'audio/mp3'
        if not objId:
            hstr = 'DearSakura_%s' % int(time.time()*1000)
            objId = hashlib.md5(hstr.encode()).hexdigest()
        file = open(path, 'rb').read()
        params = {
            'name': f"{objId}.mp4",
            'oid': '%s' % str(objId),
            'type': type,
            'ver': '2.0'  # 2.0 :p
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': contentType,
            'Content-Length': str(len(file)),
            'x-obs-params': self.genOBSParams(params, 'b64')  # base64 encode
        })
        r = self.server.postContent(
            self.LINE_OBS_DOMAIN + '/myhome/h/upload.nhn', headers=hr, data=file)
        if r.status_code != 201:
            raise Exception(
                f"Upload object home failure. Receive statue code: {r.status_code}")
        return objId

    def uploadMultipleImageToTalk(self, paths, to):
        if type(paths) != list:
            raise Exception('paths must be list')
        sqrd_base = [13, 0, 18, 11, 11]
        hashmap = {
            "GID": "0",
            "GSEQ": "1",
            "GTOTAL": str(len(paths))
        }
        sqrd = sqrd_base + self.getIntBytes(len(hashmap.keys()))
        for hm in hashmap.keys():
            sqrd += self.getStringBytes(hm)
            sqrd += self.getStringBytes(hashmap[hm])
        sqrd += [0]
        data = bytes(sqrd)
        msg = json.dumps({
            "message": b64encode(data).decode('utf-8')
        })
        talkMeta = b64encode(msg.encode('utf-8')).decode('utf-8')
        res = self.uploadObjTalk(
            paths[0], to=to, talkMeta=talkMeta, returnHeaders=True)
        gid = res['x-line-message-gid']
        msgIds = [res['x-obs-oid']]
        if len(paths) > 1:
            hashmap["GID"] = gid
            nc = 2
            for img in paths[1:]:
                self.log(f"Upload image-{nc} with GID-{gid}...", True)
                hashmap["GSEQ"] = str(nc)
                sqrd = sqrd_base + self.getIntBytes(len(hashmap.keys()))
                for hm in hashmap.keys():
                    sqrd += self.getStringBytes(hm)
                    sqrd += self.getStringBytes(hashmap[hm])
                sqrd += [0]
                data = bytes(sqrd)
                msg = json.dumps({
                    "message": b64encode(data).decode('utf-8')
                })
                talkMeta = b64encode(msg.encode('utf-8')).decode('utf-8')
                res = self.uploadObjTalk(
                    img, to=to, talkMeta=talkMeta, returnHeaders=True)
                msgIds.append(res['x-obs-oid'])
                nc += 1
        return gid

    def uploadObjTalk(self, pathOrBytes, oType='image', objId=None, to=None, talkMeta=None, returnHeaders=False, filename: str = None):
        if oType.lower() not in ['image', 'gif', 'video', 'audio', 'file']:
            raise Exception('Invalid type value')
        # url = self.LINE_OBS_DOMAIN + '/talk/m/upload.nhn' #if reqseq not working
        # url = self.LINE_OBS_DOMAIN + '/r/talk/m/reqseq'
        params = {
            "oid": "reqseq",
            "reqseq": str(self.getCurrReqId()),
            'cat': 'original'
        }
        if to != None:
            params['tomid'] = to
        else:
            if objId != None:
                params['oid'] = objId
        obsObjId, obsHash, respHeaders = self.uploadObjectForService(
            pathOrBytes, oType, 'talk/m/reqseq', params=params, talkMeta=talkMeta, filename=filename)
        if returnHeaders:
            return respHeaders
        if objId is None:
            # the message seq, if u oid using reqseq
            objId = obsObjId
        objHash = obsHash  # for view on cdn
        return objId

    def forwardObjectMsg(self, to: str, msgId: str, contentType: str = 'image', copyFromService: str = 'talk', copyFromSid: str = 'm', copyFrom: str = None, copy2Service: str = 'talk', copy2Sid: str = 'm', copy2: str = None, contentId: str = None, original: bool = False, duration: int = None, issueToken4ChannelId: str = None):
        if contentType.lower() not in ['image', 'video', 'audio', 'file']:
            raise Exception('Type not valid.')
        if copyFrom is None:
            copyFrom = f"/{copyFromService}/{copyFromSid}/{msgId}"
        if copy2 is None:
            copy2 = f"/{copy2Service}/{copy2Sid}"
        data = {
            'copyFrom': copyFrom,
            'contentId': contentId,
            'oid': 'reqseq',
            'tomid': to,
            'reqseq': self.getCurrReqId(),
            'type': contentType,
            'ver': '1.0',
        }
        if original:
            data['cat'] = 'original'
        if duration is not None:
            data['duration'] = duration
        hr = self.Hraders4Obs
        if issueToken4ChannelId is not None:
            hr = self.server.additionalHeaders(hr, {
                "X-Line-ChannelToken": self.checkAndGetValue(self.approveChannelAndIssueChannelToken(issueToken4ChannelId), 'channelAccessToken', 5),
            })
        data = list(urllib.parse.urlencode(data).encode())
        r = self.postPackDataAndGetUnpackRespData(f'/oa/{copy2}/copy.nhn', data, 0, 0,
                                                  headers=hr,
                                                  conn=self.obsConn)
        return r.headers['X-Obs-Oid']

    def forwardKeepObjectMsg(self, to, oid, contentId, contentType='image'):
        # SHARE KEEP CONTENTS V1
        data = {
            'copyFrom': f'/keep/p/{oid}',
            'tomid': to,
            'reqseq': self.getCurrReqId(),
            'type': contentType,
            'contentId': contentId,
            'size': '-1',
        }
        if contentType == 'image':
            data['cat'] = 'original'
        elif contentType in ['audio', 'video']:
            data['duration'] = '3000'
        print(self.server.timelineHeaders)
        r = self.server.postContent(
            self.LINE_HOST_DOMAIN + '/oa/r/talk/m/reqseq/copy.nhn', data=data, headers=self.server.timelineHeaders)
        if not self.checkRespIsSuccessWithLpv(r):
            raise Exception(f'Forward object failure: {r.status_code}')
        return r.headers['X-Obs-Oid']

    def forwardKeepContent2Mid(self, to: str, oid: str, contentId: str, contentType='image', original: bool = False, duration: int = None):
        # SHARE KEEP CONTENTS V2
        return self.forwardObjectMsg(to, oid, contentType, 'keep', 'p', None, contentId=contentId, original=original, duration=duration, issueToken4ChannelId='1433572998')

    def trainingImage(self, msgId):
        data = {
            "useAsTrainingData": False,
            "input": 'obs://talk/m/%s' % msgId,
            "filters": {
                "OCR": {
                    "params": {
                        "useColorPicker": "true"
                    }
                }
            }
        }

        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            "x-client-channel": "chat_viewer",
            "x-lal": "zh-Hant_TW",
            "x-recognition-input-type": "obs",
            "Content-Type": "application/json",
        })
        r = self.server.postContent(
            self.LINE_OBS_DOMAIN + '/px/talk/m/%s/recognition.obs' % msgId, data=json.dumps(data), headers=hr)
        if not self.checkRespIsSuccessWithLpv(r):
            raise Exception(f'Training image failure: {r.status_code}')
        return r.json()

    def downloadObjectMsg(self, objId: str, path: str = None, objFrom: str = 'c'):
        obs_path = f'{"g2" if self.getToType(objFrom) == 4 else "talk"}/m'
        return self.downloadObjectForService(objId, path, obs_path)

    def downloadAlbumImage(self, oid: str, path: str):
        obs_path = f'/album/a/download.nhn?ver=1.0&oid={oid}'
        r = self.server.getContent(
            self.LINE_OBS_DOMAIN + obs_path, headers=self.server.timelineHeaders)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content

    def downloadProfileImage(self, mid: str, base_path: str, video: bool = False):
        url = self.LINE_OBS_DOMAIN + f'/r/talk/p/{mid}'
        savePath = f"{base_path}/{mid}.jpg"
        if video:
            url += '/vp'
            savePath = f"{base_path}/{mid}.mp4"
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        with open(savePath, 'wb') as f:
            f.write(r.content)
        return savePath

    def downloadProfileCover(self, mid: str, base_path: str, video: bool = False):
        url, vc_url, objId, vc_objId = self.getProfileCoverObjIdAndUrl(mid)
        savePath = f"{base_path}/{mid}.jpg"
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        with open(savePath, 'wb') as f:
            f.write(r.content)
        return savePath

    def downloadObjectMyhome(self, objId, path, objFrom='h'):
        return self.downloadObjectForService(objId, path, obsPathPrefix=f'myhome/{objFrom}')

    def downloadObjectForService(self, objId, savePath, obsPathPrefix='myhome/h', size=None, suffix=None, issueToken4ChannelId: str = None, params: dict = {}):
        obs_path = f'/r/{obsPathPrefix}/{objId}'
        if size is not None:
            # eg. size = "m800x1200" or "L800x1200"or "w800"
            # must be an existing size :p
            obs_path += f'/{size}'
        if suffix is not None:
            # eg. suffix = "mp4"
            obs_path += f'/{suffix}'
        hr = self.Hraders4Obs
        hr = self.server.additionalHeaders(hr, {
            "X-LHM": "GET",
            "X-LPV": "1",
        })
        if issueToken4ChannelId is not None:
            hr = self.server.additionalHeaders(hr, {
                "X-Line-ChannelToken": self.checkAndGetValue(self.approveChannelAndIssueChannelToken(issueToken4ChannelId), 'channelAccessToken', 5),
            })
        isDebugOnly = True
        self.log(f'Starting downloadObjectForService...', isDebugOnly)
        self.log(f'obsPath: {obs_path}', isDebugOnly)
        self.log(f'params: {params}', isDebugOnly)
        self.log(f'hr: {hr}', isDebugOnly)
        try:
            r = self.postPackDataAndGetUnpackRespData(
                f'/oa{obs_path}', b'', 0, 0, headers=hr, conn=self.obsConn)
        except Exception as e:
            print("downloadObjectForService: ", e)
            raise Exception(e)
        if r.status_code != 200:
            raise Exception(
                f'[downloadObjectForService] Download failed! Resp status expected `200`, got `{r.status_code}`.')
        if savePath is not None:
            with open(savePath, 'wb') as f:
                f.write(r.content)
        self.log(f'Ended downloadObjectForService!', isDebugOnly)
        return r.content

    def uploadObjectForService(self, pathOrBytes: any, oType: str = 'image', obsPath: str = 'myhome/h', issueToken4ChannelId: str = None, params: dict = None, talkMeta: str = None, filename: str = None):
        obs_path = f'/r/{obsPath}'
        hr = self.Hraders4Obs
        data = None
        files = None
        oType = oType.lower()
        isDebugOnly = True
        if isinstance(pathOrBytes, str):
            files = {'file': open(pathOrBytes, 'rb')}
            filename = files['file'].name if filename is None else filename
            filename = filename.split('\\')[-1]
            data = open(pathOrBytes, 'rb').read()
        else:
            data = pathOrBytes
        filename = str(uuid.uuid1()) if filename is None else filename
        base_params = {
            "type": oType,
            "ver": "2.0",
            "name": filename,
        }
        if params:
            base_params.update(params)
        params = base_params
        if files is not None:
            # FORM DATA
            data = {'params': json.dumps(params)}
            params = None
        else:
            # POST DATA
            files = None
            if len(data) == 0:
                raise ValueError('No data to send: %s' % data)
            hr = self.server.additionalHeaders(hr, {
                'Content-Type': 'image/gif',  # but...
                'Content-Length': str(len(data)),
                'X-Obs-Params': self.genOBSParams(params, 'b64'),
            })
        if issueToken4ChannelId is not None:
            hr = self.server.additionalHeaders(hr, {
                "X-Line-ChannelToken": self.checkAndGetValue(self.approveChannelAndIssueChannelToken(issueToken4ChannelId), 'channelAccessToken', 5),
            })
        if params is not None:
            hr = self.server.additionalHeaders(hr, {
                'X-Obs-Params': self.genOBSParams(params, 'b64').decode(),
            })
        if talkMeta is not None:
            hr = self.server.additionalHeaders(hr, {
                'X-Talk-Meta': talkMeta
            })
        self.log(f'Starting uploadObjectForService...', isDebugOnly)
        self.log(f'data: {str(data)[:200]}', isDebugOnly)
        self.log(f'files: {files}', isDebugOnly)
        self.log(f'obsPath: {obs_path}', isDebugOnly)
        self.log(f'params: {params}', isDebugOnly)
        self.log(f'files: {files}', isDebugOnly)
        self.log(f'hr: {hr}', isDebugOnly)
        try:
            r = self.postPackDataAndGetUnpackRespData(
                f'/oa{obs_path}', data, 0, 0, headers=hr, expectedRespCode=[200, 201], conn=self.obsConn, files=files)
            #r = self.obsConn.post(self.LINE_GW_HOST_DOMAIN + f'/oa{obs_path}', data=data, headers=hr, files=files)
            # expectedRespCode:
            # - 200: image cache on obs server
            # - 201: image created success
        except Exception as e:
            print("uploadObjectForService: ", e)
            raise Exception(e)
        objId = r.headers['x-obs-oid']
        objHash = r.headers['x-obs-hash']  # for view on cdn
        self.log(f'Ended uploadObjectForService!', isDebugOnly)
        return objId, objHash, r.headers

    def getObjPlayback(self, oid: int, type: str = "VIDEO"):
        url = self.LINE_HOST_DOMAIN + "/oa/talk/m/playback.obs?p=sg-1"
        data = {
            "networkType": "Cell",
            "oid": oid,
            "type": type,
            "ver": "1.0",
            "modelName": "ios",
            "lang": "zh"
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            "x-obs-channeltype": "legy",
        })
        r = self.server.postContent(url, data=data, headers=hr)
        if not self.checkRespIsSuccessWithLpv(r):
            raise Exception(f'GetObjPlayback failure: {r.status_code}')
        return r.json()

    def uploadStoryObject(self, mid, albumId, name):
        raise Exception("uploadStoryObject is not implemented")
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-obs-params': 'eyJuYW1lIjoidGltZWxpbmVfMjAyMTAyMjZfMDQzODExLmpwZyIsIm9pZCI6IjgzNTY2YWVmM2ZhNWRhMjllMGNkNGJkMzFiM2QzM2IxdGZmZmZmZmZmIiwicmFuZ2UiOiJieXRlcyAwLTIxNzEwXC8yMTcxMSIsInF1YWxpdHkiOiI3MCIsInR5cGUiOiJpbWFnZSIsInZlciI6IjEuMCJ9'
        })
        url = self.server.urlEncode(
            self.LINE_OBS_DOMAIN, '/story/st/upload.nhn')
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    def downloadKeepContentByOidAndContentId(self, oid: str, contentId: str, save_path: str = None, sid: str = 'p'):
        return self.downloadObjectForService(
            oid, save_path,
            obsPathPrefix=f'keep/{sid}',
            issueToken4ChannelId='1433572998',
            params={
                'contentId': contentId
            })

    def copyTalkObject4Keep(self, messageId: str, service="talk"):
        url = self.LINE_HOST_DOMAIN + f"/oa/keep/p/copy.nhn"
        hstr = 'DearSakura_%s_%s' % int(time.time() * 1000, messageId)
        file_name = hashlib.md5(hstr.encode()).hexdigest()
        keep_oid = f"linekeep_{file_name}_tffffffff"
        data = {
            'oid': keep_oid,
            'copyFrom': f"/{service}/m/{messageId}"
        }
        hr = self.server.additionalHeaders(self.Hraders4Obs, {
            "x-obs-channeltype": "legy",
        })
        r = self.server.postContent(url, data=data, headers=hr)
        if not self.checkRespIsSuccessWithLpv(r):
            raise Exception(f'saveTalkObject2Keep failure: {r.status_code}')
        return r.json()