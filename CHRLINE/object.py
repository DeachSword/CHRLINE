# -*- coding: utf-8 -*-
from datetime import datetime
import copy
import json, time, ntpath, re, hashlib
from base64 import b64encode

class Object(object):

    def __init__(self):
        pass
    
    """ 
    
    TimelineObs 
    Source: https://github.com/DeachSword/LINE-DemoS-Bot/blob/master/api/obs/obs.py
    
    """
    
    def updateProfileImage(self, path):
        url = self.LINE_OBS_DOMAIN + f'/r/talk/p/{self.profile[1]}'
        file = open(path, 'rb')
        hstr = 'DearSakura_%s' % int(time.time() * 1000)
        file_name = hashlib.md5(hstr.encode()).hexdigest()
        params = {
            'name': file_name,
            'quality': '100',
            "type": "image",
            "ver": "2.0"
        }
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data={'params': json.dumps(params)}, files={'file':file})
        if r.status_code != 201:
            raise Exception(f"updateProfileImage failure. Receive statue code: {r.status_code}")
        return True
    
    def updateProfileCover(self, path):
        hstr = 'DearSakura_%s' % int(time.time() * 1000)
        objid = hashlib.md5(hstr.encode()).hexdigest()
        if not objid:
            hstr = 'DearSakura_%s' % int(time.time()*1000)
            objid = hashlib.md5(hstr.encode()).hexdigest()
        url = self.LINE_OBS_DOMAIN + f'/r/myhome/c/{objid}'
        file = {'file': open(path, 'rb')}
        params = {
            'name': objid,
            'quality': '100',
            'type': 'image',
            'ver': '2.0'
        }
        data = {'params': json.dumps(params)}
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data=data, files=file)
        if r.status_code != 201:
            raise Exception(f"Upload object home failure. Receive statue code: {r.status_code}")
        objId = r.headers['x-obs-oid']
        home = self.updateProfileCoverById(objId)
        return home
    
    def updateImageToAlbum(self, mid, albumId, path):
        pass
        #privie
    
    def uploadObjHome(self, path, type='image', objId=None):
        if type not in ['image','video','audio']:
            raise Exception('Invalid type value')
        if type == 'image':
            contentType = 'image/jpeg'
        elif type == 'video':
            contentType = 'video/mp4'
        elif type == 'audio':
            contentType = 'audio/mp3'
        if not objId:
            hstr = 'DearSakura_%s' % int(time.time()*1000)
            objid = hashlib.md5(hstr.encode()).hexdigest()
        file = open(path, 'rb').read()
        params = {
            'name': '%s' % str(time.time()*1000),
            'userid': '%s' % self.profile[1],
            'oid': '%s' % str(objId),
            'type': type,
            'ver': '1.0' #2.0 :p
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': contentType,
            'Content-Length': str(len(file)),
            'x-obs-params': self.genOBSParams(params,'b64') #base64 encode
        })
        r = self.server.postContent(self.LINE_OBS_DOMAIN + '/myhome/c/upload.nhn', headers=hr, data=file)
        if r.status_code != 201:
            raise Exception(f"Upload object home failure. Receive statue code: {r.status_code}")
        return objId
    
    def uploadMultipleImageToTalk(self, paths, to):
        if type(paths) != list:
            raise Exception('paths must be list')
        sqrd_base = [13, 0, 18, 11, 11]
        hashmap = {
            "GID" : "0",
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
        res = self.uploadObjTalk(paths[0], to=to, talkMeta=talkMeta, returnHeaders=True)
        gid = res['x-line-message-gid']
        msgIds = [res['x-obs-oid']]
        if len(paths) > 1:
            hashmap["GID"] = gid
            nc = 2
            for img in paths[1:]:
                print(f"Upload image-{nc} with GID-{gid}...")
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
                res = self.uploadObjTalk(img, to=to, talkMeta=talkMeta, returnHeaders=True)
                msgIds.append(res['x-obs-oid'])
                nc += 1
        return gid
        
    def uploadObjTalk(self, path=None, type='image', objId=None, to=None, talkMeta=None, returnHeaders=False):
        if type not in ['image','gif','video','audio','file']:
            raise Exception('Invalid type value')
        headers=self.server.timelineHeaders
        files = {'file': open(path, 'rb')}
        #url = self.LINE_OBS_DOMAIN + '/talk/m/upload.nhn' #if reqseq not working
        url = self.LINE_OBS_DOMAIN + '/r/talk/m/reqseq'
        params = {
            "type": "image",
            "ver": "2.0",
            "name": files['file'].name,
            "oid": "reqseq",
            "reqseq": str(self.revision),
            "cat": "original"
        }
        if objId != None:
            params['oid'] = objId
        if to != None:
            params['tomid'] = to
        if type != 'gif':
            params['type'] = type
            data = {'params': self.genOBSParams(params)}
        elif type == 'gif':
            params = {
                'type': 'image',
                'ver': '2.0',
                'name': files['file'].name,
                'oid': 'reqseq',
                'reqseq': '%s' % str(self.revision),
                'tomid': '%s' % str(to),
                'cat': 'original'
            }
            files = None
            data = open(path, 'rb').read()
            headers = self.server.additionalHeaders(self.server.Headers, {
                'content-type': 'image/gif',
                'Content-Length': str(len(data)),
                'x-obs-params': self.genOBSParams(params,'b64'), #base64 encode
                'X-Line-Access': self.acquireEncryptedAccessToken()[7:]
            })
        if talkMeta != None:
            headers = self.server.additionalHeaders(headers, {
                'X-Talk-Meta': talkMeta
            })
        r = self.server.postContent(url, data=data, headers=headers, files=files)
        if r.status_code != 201:
            print("uploadObjTalk: ", r.status_code)
            raise Exception('Upload %s failure.' % type)
        else:
            if returnHeaders:
                return r.headers
            if objId is None:
                objId = r.headers['x-obs-oid'] #the message seq, if u oid using reqseq
            objHash = r.headers['x-obs-hash']  #for view on cdn
        return objId
    
    def forwardObjectMsg(self, to, msgId, contentType='image', objFrom='c'):
        if contentType not in ['image','video','audio','file']:
            raise Exception('Type not valid.')
        data = {
            'name': f'CHRLINE-{int(time.time())}', 'tomid': to,'oid': 'reqseq','reqseq': self.revision,'type': contentType,'copyFrom': f'/{"g2" if self.getToType(to) == 4 else "talk"}'
        }
        r = self.server.postContent(self.LINE_OBS_DOMAIN + '/g2/m/copy.nhn' if self.getToType(to) == 4 else '/talk/m/copy.nhn', data=data, headers=self.server.timelineHeaders)
        # self.LINE_HOST_DOMAIN + '/oa/r/talk/m/reqseq/copy.nhn'
        if r.status_code != 200:
            raise Exception(f'Forward object failure: {r.status_code}')
        return True
    
    def forwardKeepObjectMsg(self, to, oid, contentId, contentType='image'):
        if contentType not in ['image','video','audio','file']:
            raise Exception('Type not valid.')
        #data = copyFrom=/keep/p/linekeep_1317462115813022667381t0d0d34a0&tomid=c7bb0199d949fee69dd445eaad321cd2b&reqseq=14884&type=video&duration=3320&contentId=WQDnZP2&size=1606120
        data = {
            'copyFrom': f'/keep/p/{oid}', 
            'tomid': to,
            'reqseq': self.revision,
            'type': contentType,
            'contentId': contentId,
            'size': '-1',
        }
        if contentType == 'image':
            data['cat'] = 'original'
        elif contentType in ['audio', 'video']:
            data['duration'] = '3000'
        r = self.server.postContent(self.LINE_HOST_DOMAIN + '/oa/r/talk/m/reqseq/copy.nhn', data=data, headers=self.server.timelineHeaders)
        if r.status_code != 200:
            raise Exception(f'Forward object failure: {r.status_code}')
        return r.text

    def trainingImage(self, msgId):
        data = {
           "useAsTrainingData" : False,
           "input" : 'obs://talk/m/%s' % msgId,
           "filters" : {
              "OCR" : {
                 "params" : {
                    "useColorPicker" : "true"
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
        r = self.server.postContent(self.LINE_OBS_DOMAIN + '/px/talk/m/%s/recognition.obs' % msgId, data=json.dumps(data), headers=hr)
        if r.status_code != 200:
            raise Exception(f'Training image failure: {r.status_code}')
        return r.json()
        
    def downloadObjectMsg(self, objId, path, objFrom='c'):
        obs_path = f'/r/{"g2" if self.getToType(objFrom) == 4 else "talk"}/m/{objId}'
        r = self.server.getContent(self.LINE_OBS_DOMAIN + obs_path, headers=self.server.timelineHeaders)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content

