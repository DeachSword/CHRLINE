# -*- coding: utf-8 -*-
from datetime import datetime
import copy
import json, time, ntpath, re, hashlib

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
        return objId
    
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
        
    def uploadObjTalk(self, path=None, type='image', objId=None, to=None):
        if type not in ['image','gif','video','audio','file']:
            raise Exception('Invalid type value')
        headers=None
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
        r = self.server.postContent(url, data=data, headers=headers, files=files)
        if r.status_code != 201:
            console.log("uploadObjTalk: ", r.text)
            raise Exception('Upload %s failure.' % type)
        else:
            if objId is None:
                objId = r.headers['x-obs-oid'] #the message seq, if u oid using reqseq
            objHash = r.headers['x-obs-hash']  #for view on cdn
        return objId
    
    def forwardObjectMsg(self, to, msgId, contentType='image'):
        if contentType not in ['image','video','audio','file']:
            raise Exception('Type not valid.')
        data = {
            'name': f'CHRLINE-{int(time.time())}', 'tomid': to,'oid': 'reqseq','reqseq': self.revision,'type': contentType,'copyFrom': '/talk/m/%s' % msgId
        }
        r = self.server.postContent(self.LINE_OBS_DOMAIN + '/talk/m/copy.nhn', data=data, headers=self.server.timelineHeaders)
        if r.status_code != 200:
            raise Exception(f'Forward object failure: {r.status_code}')
        return True

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

