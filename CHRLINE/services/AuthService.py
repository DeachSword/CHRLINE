# -*- coding: utf-8 -*-
import time
import json
import requests


class AuthService(object):

    def __init__(self):
        pass

    def openAuthSession(self):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('openAuthSession') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def getAuthRSAKey(self, authSessionId: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getAuthRSAKey') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [8, 0, 3] + self.getIntBytes(1)  # identityProvider
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def setIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('setIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1)  # identityProvider
        # cipherKeyId, eg.10031
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId)
        # cipherText, rsa enc maybe
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def updateIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('updateIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1)  # identityProvider
        # cipherKeyId, eg.10031
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId)
        # cipherText, rsa enc maybe
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def resendIdentifierConfirmation(self, authSessionId: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('resendIdentifierConfirmation') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def confirmIdentifier(self, authSessionId: str, verificationCode: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('confirmIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [12, 0, 5]
        # sqrd += [2, 0, 2] + self.getIntBytes(1) #forceRegistration : 1?
        # verificationCode
        sqrd += [11, 0, 3] + self.getStringBytes(verificationCode)
        sqrd += [0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def removeIdentifier(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('removeIdentifier') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(authSessionId)
        sqrd += [12, 0, 3]
        sqrd += [8, 0, 2] + self.getIntBytes(1)  # identityProvider
        sqrd += [11, 0, 3] + self.getStringBytes(cipherKeyId)  # cipherKeyId
        sqrd += [11, 0, 4] + self.getStringBytes(cipherText)  # cipherText
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT, sqrd)

    def getClovaAppToken(self, authSessionId, cipherText, metaData={}):
        params = [
            [11, 2, authSessionId],
            [12, 3, [
                [8, 1, 2],
                [13, 2, [11, 11, metaData]],
                [11, 3, cipherText]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getClovaAppToken', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT_V4, sqrd, 4)

    def loginFromClova(self, authSessionId, cipherText, metaData={}):
        params = [
            [11, 2, authSessionId],
            [12, 3, [
                [8, 1, 2],
                [13, 2, [11, 11, metaData]],
                [11, 3, cipherText]
            ]]
        ]
        sqrd = self.generateDummyProtocol('loginFromClova', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT_V4, sqrd, 4)

    def validateClovaRequest(self, authSessionId, cipherText, metaData={}):
        params = [
            [11, 2, authSessionId],
            [12, 3, [
                [8, 1, 2],
                [13, 2, [11, 11, metaData]],
                [11, 3, cipherText]
            ]]
        ]
        sqrd = self.generateDummyProtocol('validateClovaRequest', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT_V4, sqrd, 4)

    def setClovaCredential(self, authSessionId, cipherText, metaData={}):
        params = [
            [11, 2, authSessionId],
            [12, 3, [
                [8, 1, 2],  # authLoginVersion
                [13, 2, [11, 11, metaData]],
                [11, 3, cipherText]
            ]]
        ]
        sqrd = self.generateDummyProtocol('setClovaCredential', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT_V4, sqrd, 4)

    def validateClovaAppToken(self, authSessionId, cipherText, metaData={}):
        params = [
            [11, 2, authSessionId],
            [12, 3, [
                [8, 1, 2],  # authLoginVersion
                [13, 2, [11, 11, metaData]],
                [11, 3, cipherText]
            ]]
        ]
        sqrd = self.generateDummyProtocol('validateClovaAppToken', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_AUTH_ENDPOINT_V4, sqrd, 4)

    def verifyQrcodeWithE2EE(self, verifier, keyId, keyData, createdTime, encryptedKeyChain, hashKeyChain, pinCode=""):
        params = [
            [11, 2, verifier],
            [11, 3, pinCode],
            [8, 4, 95],  # errorCode
            [12, 5, [
                [8, 1, 1],  # version
                [8, 2, keyId],
                [11, 4, keyData],
                [10, 5, createdTime]
            ]],
            [11, 6, encryptedKeyChain],
            [11, 7, hashKeyChain]
        ]
        sqrd = self.generateDummyProtocol('verifyQrcodeWithE2EE', params, 4)
        return self.postPackDataAndGetUnpackRespData("/S4", sqrd, 4)

    def confirmE2EELogin(self, verifier, deviceSecret):
        params = [
            [11, 1, verifier],
            [11, 2, deviceSecret],
        ]
        sqrd = self.generateDummyProtocol('confirmE2EELogin', params, 3)
        return self.postPackDataAndGetUnpackRespData("/api/v3p/rs", sqrd, 3)

    def issueV3TokenForPrimary(self, udid: str, systemDisplayName: str, modelName: str):
        params = [
            [12, 1, [
                [11, 1, udid],
                [11, 2, systemDisplayName],
                [11, 3, modelName]
            ]]
        ]
        sqrd = self.generateDummyProtocol('issueV3TokenForPrimary', params, 3)
        return self.postPackDataAndGetUnpackRespData("/api/v3p/rs", sqrd, 3)

    def logoutZ(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logoutZ is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "logoutZ", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def issueTokenForAccountMigration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueTokenForAccountMigration is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueTokenForAccountMigration", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def updatePassword(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updatePassword is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updatePassword", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def respondE2EELoginRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("respondE2EELoginRequest is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "respondE2EELoginRequest", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def logoutV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logoutV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "logoutV2", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def establishE2EESession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("establishE2EESession is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "establishE2EESession", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def releaseLockScreen(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("releaseLockScreen is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "releaseLockScreen", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def normalizePhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("normalizePhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "normalizePhoneNumber", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def exchangeKey(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("exchangeKey is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "exchangeKey", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def setIdentifierAndPassword(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setIdentifierAndPassword is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "setIdentifierAndPassword", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)

    def issueTokenForAccountMigrationSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "issueTokenForAccountMigrationSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueTokenForAccountMigrationSettings", params, AuthService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(AuthService_API_PATH, sqrd, AuthService_RES_TYPE)
