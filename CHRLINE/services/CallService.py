# -*- coding: utf-8 -*-

class CallService(object):

    def __init__(self):
        pass
        
    def acquireCallRoute(self, to, callType=1, fromEnvInfo={}):
        METHOD_NAME = "acquireCallRoute"
        params = [
            [11, 2, to],
            [8, 3, callType],
            [13, 4, [11, 11, fromEnvInfo]]
        ]
        sqrd = self.generateDummyProtocol('acquireCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def acquireOACallRoute(self, searchId, fromEnvInfo, otp):
        METHOD_NAME = "acquireOACallRoute"
        params = [
            [12, 2, [
                [11, 1, searchId],
                [13, 2, [11, 11, fromEnvInfo]],
                [11, 3, otp]
            ]]
        ]
        sqrd = self.generateDummyProtocol('acquireOACallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def searchPaidCallUserRate(self, countryCode):
        METHOD_NAME = "searchPaidCallUserRate"
        params = [
            [11, 2, countryCode],
        ]
        sqrd = self.generateDummyProtocol('searchPaidCallUserRate', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def acquirePaidCallCurrencyExchangeRate(self, countryCode):
        METHOD_NAME = "acquirePaidCallCurrencyExchangeRate"
        params = [
            [11, 2, countryCode],
        ]
        sqrd = self.generateDummyProtocol('acquirePaidCallCurrencyExchangeRate', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def lookupPaidCall(self, dialedNumber, language, referer):
        METHOD_NAME = "lookupPaidCall"
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [11, 4, referer],
        ]
        sqrd = self.generateDummyProtocol('lookupPaidCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def acquirePaidCallRoute(self, paidCallType, dialedNumber, language, networkCode, disableCallerId, referer, adSessionId):
        METHOD_NAME = "acquirePaidCallRoute"
        params = [
            [8, 2, paidCallType],
            [11, 3, dialedNumber],
            [11, 4, language],
            [11, 5, networkCode],
            [2, 6, disableCallerId],
            [11, 7, referer],
            [11, 8, adSessionId],
        ]
        sqrd = self.generateDummyProtocol('acquirePaidCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getPaidCallBalanceList(self, language):
        METHOD_NAME = "getPaidCallBalanceList"
        params = [
            [11, 2, language],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallBalanceList', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getPaidCallHistory(self, start, size):
        METHOD_NAME = "getPaidCallHistory"
        params = [
            [10, 2, start],
            [8, 3, size],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallHistory', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getCallCreditProducts(self, appStoreCode, pgCode, country):
        METHOD_NAME = "getCallCreditProducts"
        params = [
            [8, 2, appStoreCode],
            [8, 3, pgCode],
            [11, 4, country],
        ]
        sqrd = self.generateDummyProtocol('getCallCreditProducts', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def reserveCallCreditPurchase(self, productId, country, currency, price, appStoreCode, language, pgCode, redirectUrl):
        METHOD_NAME = "reserveCallCreditPurchase"
        params = [
            [12, 2, [
                [11, 1, productId],
                [11, 2, country],
                [11, 3, currency],
                [11, 4, price],
                [8, 5, appStoreCode],
                [11, 6, language],
                [8, 7, pgCode],
                [11, 8, redirectUrl],
            ]]
        ]
        sqrd = self.generateDummyProtocol('reserveCallCreditPurchase', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getCallCreditPurchaseHistory(self, start, size, language, eddt, appStoreCode):
        METHOD_NAME = "getCallCreditPurchaseHistory"
        params = [
            [12, 2, [
                [10, 1, start],
                [8, 2, size],
                [11, 3, language],
                [11, 4, eddt],
                [8, 5, appStoreCode],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getCallCreditPurchaseHistory', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def redeemPaidCallVoucher(self, serial):
        METHOD_NAME = "redeemPaidCallVoucher"
        params = [
            [11, 2, serial]
        ]
        sqrd = self.generateDummyProtocol('redeemPaidCallVoucher', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getPaidCallMetadata(self, language):
        METHOD_NAME = "getPaidCallMetadata"
        params = [
            [11, 2, language],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallMetadata', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def acquireGroupCallRoute(self, chatMid, mediaType=1, isInitialHost=True, capabilities=[]):
        METHOD_NAME = "acquireGroupCallRoute"
        params = [
            [11, 2, chatMid],
            [8, 3, mediaType],
            [2, 4, isInitialHost],
            [15, 5, [11, capabilities]],
        ]
        sqrd = self.generateDummyProtocol('acquireGroupCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getGroupCall(self, chatMid):
        METHOD_NAME = "getGroupCall"
        params = [
            [11, 2, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getGroupCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def inviteIntoGroupCall(self, chatMid, memberMids, mediaType=1):
        METHOD_NAME = "inviteIntoGroupCall"
        params = [
            [11, 2, chatMid],
            [15, 3, [11, memberMids]],
            [8, 4, mediaType],
        ]
        sqrd = self.generateDummyProtocol('inviteIntoGroupCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def markPaidCallAd(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "markPaidCallAd"
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [2, 4, disableCallerId],
        ]
        sqrd = self.generateDummyProtocol('markPaidCallAd', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getPaidCallAdStatus(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "getPaidCallAdStatus"
        params = []
        sqrd = self.generateDummyProtocol('getPaidCallAdStatus', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def acquireTestCallRoute(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "acquireTestCallRoute"
        params = []
        sqrd = self.generateDummyProtocol('acquireTestCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getGroupCallUrls(self):
        METHOD_NAME = "getGroupCallUrls"
        params = [
            [12, 2, []]
        ]
        sqrd = self.generateDummyProtocol('getGroupCallUrls', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def createGroupCallUrl(self, title):
        METHOD_NAME = "createGroupCallUrl"
        params = [
            [12, 2, [
                [11, 1, title]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def deleteGroupCallUrl(self, urlId):
        METHOD_NAME = "deleteGroupCallUrl"
        params = [
            [12, 2, [
                [11, 1, urlId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('deleteGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def updateGroupCallUrl(self, urlId, title):
        METHOD_NAME = "updateGroupCallUrl"
        params = [
            [12, 2, [
                [11, 1, urlId],
                [12, 2, [
                    [11, 1, title]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('updateGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def getGroupCallUrlInfo(self, urlId):
        METHOD_NAME = "getGroupCallUrlInfo"
        params = [
            [12, 2, [
                [11, 1, urlId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getGroupCallUrlInfo', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def joinChatByCallUrl(self, urlId):
        METHOD_NAME = "joinChatByCallUrl"
        params = [
            [12, 2, [
                [11, 1, urlId],
                [8, 2, self.getCurrReqId()]
            ]]
        ]
        sqrd = self.generateDummyProtocol('joinChatByCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3, readWith=f"CallService.{METHOD_NAME}")

    def kickoutFromGroupCall(self, toMid: str, targetMids: list):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 08/26/2022, 13:18:46
        """
        METHOD_NAME = "kickoutFromGroupCall"
        params = [
            [12, 2, [
                [11, 1, toMid],
                [15, 2, [11, targetMids]]
            ]]
        ]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.CallService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.CallService_API_PATH ,sqrd,  self.CallService_RES_TYPE)