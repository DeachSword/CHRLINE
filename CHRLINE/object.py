# -*- coding: utf-8 -*-
from datetime import datetime
import copy
import json, time, ntpath, re, hashlib

class Object(object):

    def __init__(self):
        pass

    def forwardObjectMsg(self, to, msgId, contentType='image'):
        if contentType not in ['image','video','audio','file']:
            raise Exception('Type not valid.')
        data = {
            'name': f'CHRLINE-{int(time.time())}', 'tomid': to,'oid': 'reqseq','reqseq': self.revision,'type': contentType,'copyFrom': '/talk/m/%s' % msgId
        }
        r = self.server.postContent('https://obs-jp.line-apps.com/talk/m/copy.nhn', data=data, headers=self.server.timelineHeaders)
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
        r = self.server.postContent('https://obs.line-apps.com/px/talk/m/%s/recognition.obs' % msgId, data=json.dumps(data), headers=hr)
        if r.status_code != 200:
            raise Exception(f'Training image failure: {r.status_code}')
        return r.json()

