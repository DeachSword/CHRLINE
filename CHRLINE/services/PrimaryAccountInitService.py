# -*- coding: utf-8 -*-
import time
import json
import uuid

class PrimaryAccountInitService(object):

    def __init__(self):
        self.register_headers  = self.server.Headers
        self.uuid = uuid.uuid4().hex
    
    def setPrimaryUuid(self, uuid):
        self.uuid = uuid
        
    def openPrimarySession(self):
        params = [
            [12, 1, [
                [13, 1, [11, 11, []]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('openSession', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def getCountryInfo(self, authSessionId, simCard=None):
        params = [
            [11, 1, authSessionId],
            # [12, 11, [
                # [11, 1, countryCode],
                # [11, 2, hni],
                # [11, 3, carrierName],
            # ]]
        ]
        sqrd = self.generateDummyProtocol('getCountryInfo', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def getPhoneVerifMethod(self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"):
        _headers = {
            'x-lpqs': "/acct/pais/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getPhoneVerifMethod') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1] + self.getStringBytes(self.uuid)
        sqrd += [11, 0, 2] + self.getStringBytes(deviceModel)
        sqrd += [0]
        sqrd += [12, 0, 3]
        sqrd += [11, 0, 1] + self.getStringBytes(phoneNumber)
        sqrd += [11, 0, 2] + self.getStringBytes(countryCode)
        sqrd += [0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent('https://ga2.line.naver.jp', data=data, headers=self.register_headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def sendPinCodeForPhone(self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"):
        _headers = {
            'x-lpqs': "/acct/pais/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('sendPinCodeForPhone') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1] + self.getStringBytes(self.uuid)
        print(f"UUID: {self.uuid}")
        sqrd += [11, 0, 2] + self.getStringBytes(deviceModel)
        sqrd += [0]
        sqrd += [12, 0, 3]
        sqrd += [11, 0, 1] + self.getStringBytes(phoneNumber)
        sqrd += [11, 0, 2] + self.getStringBytes(countryCode)
        sqrd += [0]
        sqrd += [8, 0, 4] + self.getIntBytes(2)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent('https://ga2.line.naver.jp', data=data, headers=self.register_headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def verifyPhone(self, authSessionId, phoneNumber, countryCode, pinCode, deviceModel="SM-N950F"):
        _headers = {
            'x-lpqs': "/acct/pais/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('verifyPhone') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 2]
        sqrd += [11, 0, 1] + self.getStringBytes(self.uuid)
        sqrd += [11, 0, 2] + self.getStringBytes(deviceModel)
        sqrd += [0]
        sqrd += [12, 0, 3]
        sqrd += [11, 0, 1] + self.getStringBytes(phoneNumber)
        sqrd += [11, 0, 2] + self.getStringBytes(countryCode)
        sqrd += [0]
        sqrd += [11, 0, 4] + self.getStringBytes(pinCode)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent('https://ga2.line.naver.jp', data=data, headers=self.register_headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def validateProfile(self, authSessionId, displayName):
        params = [
            [11, 1, authSessionId],
            [11, 2, displayName]
        ]
        sqrd = self.generateDummyProtocol('validateProfile', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def exchangeEncryptionKey(self, authSessionId, publicKey, nonce, authKeyVersion=1):
        params = [
            [11, 1, authSessionId],
            [12, 2, [
                [8, 1, authKeyVersion],
                [11, 2, publicKey],
                [11, 3, nonce],
            ]]
        ]
        sqrd = self.generateDummyProtocol('exchangeEncryptionKey', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def setPassword(self, authSessionId, cipherText, encryptionKeyVersion=1):
        params = [
            [11, 1, authSessionId],
            [12, 2, [
                [8, 1, encryptionKeyVersion],
                [11, 2, cipherText],
            ]]
        ]
        sqrd = self.generateDummyProtocol('setPassword', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def registerPrimaryUsingPhone(self, authSessionId):
        _headers = {
            'x-lpqs': "/acct/pais/v1"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('registerPrimaryUsingPhone') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent('https://ga2.line.naver.jp', data=data, headers=self.register_headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        
    def getPhoneVerifMethodV2(self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [12, 2, [
                    [11, 1, self.uuid],
                    [11, 2, deviceModel]
                ]],
                [12, 3, [
                    [11, 1, phoneNumber],
                    [11, 2, countryCode]
                ]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getPhoneVerifMethodV2', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def requestToSendPhonePinCode(self, authSessionId, phoneNumber, countryCode, verifMethod=1):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [12, 2, [
                    [11, 1, phoneNumber],
                    [11, 2, countryCode]
                ]],
                [8, 3, verifMethod],
            ]]
        ]
        sqrd = self.generateDummyProtocol('requestToSendPhonePinCode', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def verifyPhonePinCode(self, authSessionId, phoneNumber, countryCode, pinCode):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [12, 2, [
                    [11, 1, phoneNumber],
                    [11, 2, countryCode]
                ]],
                [11, 3, pinCode],
            ]]
        ]
        sqrd = self.generateDummyProtocol('verifyPhonePinCode', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def verifyAccountUsingPwd(self, authSessionId, identifier, countryCode, cipherText):
        params = [
            [12, 1, [
                [11, 1, authSessionId],
                [12, 2, [
                    [8, 1, 1], # type
                    [11, 2, identifier],
                    [11, 3, countryCode]
                ]],
                [12, 3, [
                    [8, 1, 1], # encryptionKeyVersion
                    [11, 2, cipherText]
                ]],
            ]]
        ]
        sqrd = self.generateDummyProtocol('verifyAccountUsingPwd', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def registerPrimaryUsingPhoneWithTokenV3(self, authSessionId):
        params = [
            [11, 2, authSessionId]
        ]
        sqrd = self.generateDummyProtocol('registerPrimaryUsingPhoneWithTokenV3', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def registerPrimaryWithTokenV3(self, authSessionId):
        params = [
            [11, 2, authSessionId]
        ]
        sqrd = self.generateDummyProtocol('registerPrimaryUsingPhoneWithTokenV3', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
        
    def lookupAvailableEap(self, authSessionId):
        params = [
            [11, 1, authSessionId]
        ]
        params = [
            [12, 1, params]
        ]
        sqrd = self.generateDummyProtocol('lookupAvailableEap', params, 4)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 4, headers=self.register_headers)
    
    def getAllowedRegistrationMethod(self, authSessionId: str, countryCode: str):
        """
        Get allowed registration method.
        
        ---
        1: Phone - getPhoneVerifMethodV2
        2: Eap   - verifyEapAccountForRegistration
        """
        params = [
            [11, 1, authSessionId],
            [11, 2, countryCode]
        ]
        sqrd = self.generateDummyProtocol('getAllowedRegistrationMethod', params, 4)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 4, headers=self.register_headers)
    
    def verifyEapAccountForRegistration(self, authSessionId: str, _type: int, accessToken: str, countryCode: str, deviceModel="SM-N950F"):
        """
        Verify eap account for registration.
        
        - type:
            UNKNOWN(0),
            FACEBOOK(1),
            APPLE(2),
            GOOGLE(3);
        """
        params = [
            [11, 1, authSessionId, "authSessionId"],
            [12, 2, [
                [11, 1, self.uuid, "udid"],
                [11, 2, deviceModel, "deviceModel"]
            ], "device", "Device"],
            [12, 3, [
                [8, 1, _type, "type"],
                [11, 2, accessToken, "accessToken"],
                [11, 3, countryCode, "accessToken"]
            ], "socialLogin", "SocialLogin"],
        ]
        sqrd = self.generateDummyProtocol('verifyEapAccountForRegistration', params, 4)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 4, headers=self.register_headers)

    def registerPrimaryUsingEapAccount(self, authSessionId):
        params = [
            [11, 1, authSessionId]
        ]      
        sqrd = self.generateDummyProtocol('registerPrimaryUsingEapAccount', params, 3)
        return self.postPackDataAndGetUnpackRespData("/acct/pais/v1" ,sqrd, 3, headers=self.register_headers)
