# -*- coding: utf-8 -*-
import time
import json
import requests

class AuthService(object):
    
    def __init__(self):
        pass
        
    def openAuthSession(self):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('openAuthSession') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['openAuthSession']
        
    def getAuthRSAKey(self, authSessionId: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getAuthRSAKey') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [8, 0, 3] + self.getIntBytes(1) #identityProvider
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getAuthRSAKey']

    def setIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('setIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1) #identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId) #cipherKeyId, eg.10031
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText) #cipherText, rsa enc maybe
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['setIdentifier']

    def updateIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('updateIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1) #identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId) #cipherKeyId, eg.10031
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText) #cipherText, rsa enc maybe
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['updateIdentifier']
        
    def resendIdentifierConfirmation(self, authSessionId: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('resendIdentifierConfirmation') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['resendIdentifierConfirmation']
        
    def confirmIdentifier(self, authSessionId: str, verificationCode: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('confirmIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [12, 0, 5]
        sqrd += [2, 0, 2] + self.getIntBytes(1) #forceRegistration : 1?
        sqrd += [1, 0, 3] + self.getStringBytes(verificationCode) #verificationCode
        sqrd += [0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['confirmIdentifier']
        
    def removeIdentifier(self, authSessionId: str, verificationCode: str):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/RS3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('removeIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['removeIdentifier']
        