# -*- coding: utf-8 -*-
import time
import json
import requests

class AuthService(object):
    
    def __init__(self):
        pass
        
    def openAuthSession(self):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('openAuthSession') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['openAuthSession']
        
    def getAuthRSAKey(self, authSessionId: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getAuthRSAKey') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [8, 0, 3] + self.getIntBytes(1) #identityProvider
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['getAuthRSAKey']

    def setIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('setIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1) #identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId) #cipherKeyId, eg.10031
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText) #cipherText, rsa enc maybe
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['setIdentifier']

    def updateIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('updateIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1) #identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId) #cipherKeyId, eg.10031
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText) #cipherText, rsa enc maybe
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['updateIdentifier']
        
    def resendIdentifierConfirmation(self, authSessionId: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('resendIdentifierConfirmation') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['resendIdentifierConfirmation']
        
    def confirmIdentifier(self, authSessionId: str, verificationCode: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('confirmIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [12, 0, 5]
        # sqrd += [2, 0, 2] + self.getIntBytes(1) #forceRegistration : 1?
        sqrd += [11, 0, 3] + self.getStringBytes(verificationCode) #verificationCode
        sqrd += [0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['confirmIdentifier']
        
    def removeIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('removeIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1) #identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId) #cipherKeyId
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText) #cipherText
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT ,sqrd)['removeIdentifier']
        