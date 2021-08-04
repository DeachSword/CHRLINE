# -*- coding: utf-8 -*-

class CallService(object):

    def __init__(self):
        pass
        
    def acquireCallRoute(self, to, callType=1, fromEnvInfo={}):
        params = [
            [11, 2, to],
            [8, 3, callType],
            [13, 4, [11, 11, fromEnvInfo]]
        ]
        sqrd = self.generateDummyProtocol('acquireCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def acquireOACallRoute(self, searchId, fromEnvInfo, otp):
        params = [
            [12, 2, [
                [11, 1, searchId],
                [13, 2, [11, 11, fromEnvInfo]],
                [11, 3, otp]
            ]]
        ]
        sqrd = self.generateDummyProtocol('acquireOACallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def searchPaidCallUserRate(self, countryCode):
        params = [
            [11, 2, countryCode],
        ]
        sqrd = self.generateDummyProtocol('searchPaidCallUserRate', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def acquirePaidCallCurrencyExchangeRate(self, countryCode):
        params = [
            [11, 2, countryCode],
        ]
        sqrd = self.generateDummyProtocol('acquirePaidCallCurrencyExchangeRate', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def lookupPaidCall(self, dialedNumber, language, referer):
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [11, 4, referer],
        ]
        sqrd = self.generateDummyProtocol('lookupPaidCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def acquirePaidCallRoute(self, paidCallType, dialedNumber, language, networkCode, disableCallerId, referer, adSessionId):
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getPaidCallBalanceList(self, language):
        params = [
            [11, 2, language],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallBalanceList', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getPaidCallHistory(self, start, size):
        params = [
            [10, 2, start],
            [8, 3, size],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallHistory', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getCallCreditProducts(self, appStoreCode, pgCode, country):
        params = [
            [8, 2, appStoreCode],
            [8, 3, pgCode],
            [11, 4, country],
        ]
        sqrd = self.generateDummyProtocol('getCallCreditProducts', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def reserveCallCreditPurchase(self, productId, country, currency, price, appStoreCode, language, pgCode, redirectUrl):
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getCallCreditPurchaseHistory(self, start, size, language, eddt, appStoreCode):
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def redeemPaidCallVoucher(self, serial):
        params = [
            [11, 2, serial]
        ]
        sqrd = self.generateDummyProtocol('redeemPaidCallVoucher', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getPaidCallMetadata(self, language):
        params = [
            [11, 2, language],
        ]
        sqrd = self.generateDummyProtocol('getPaidCallMetadata', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def acquireGroupCallRoute(self, chatMid, mediaType=1, isInitialHost=True, capabilities=[]):
        params = [
            [11, 2, chatMid],
            [8, 3, mediaType],
            [2, 4, isInitialHost],
            [15, 5, [11, capabilities]],
        ]
        sqrd = self.generateDummyProtocol('acquireGroupCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getGroupCall(self, chatMid):
        params = [
            [11, 2, chatMid],
        ]
        sqrd = self.generateDummyProtocol('getGroupCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def inviteIntoGroupCall(self, chatMid, memberMids, mediaType=1):
        params = [
            [11, 2, chatMid],
            [15, 3, [11, memberMids]],
            [8, 4, mediaType],
        ]
        sqrd = self.generateDummyProtocol('inviteIntoGroupCall', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def markPaidCallAd(self, dialedNumber, language, disableCallerId):
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [2, 4, disableCallerId],
        ]
        sqrd = self.generateDummyProtocol('markPaidCallAd', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getPaidCallAdStatus(self, dialedNumber, language, disableCallerId):
        params = []
        sqrd = self.generateDummyProtocol('getPaidCallAdStatus', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def acquireTestCallRoute(self, dialedNumber, language, disableCallerId):
        params = []
        sqrd = self.generateDummyProtocol('acquireTestCallRoute', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getGroupCallUrls(self):
        params = [
            [12, 2, []]
        ]
        sqrd = self.generateDummyProtocol('getGroupCallUrls', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def createGroupCallUrl(self, title):
        params = [
            [12, 2, [
                [11, 1, title]
            ]]
        ]
        sqrd = self.generateDummyProtocol('createGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def deleteGroupCallUrl(self, urlId):
        params = [
            [12, 2, [
                [11, 1, urlId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('deleteGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def updateGroupCallUrl(self, urlId, title):
        params = [
            [12, 2, [
                [11, 1, urlId],
                [12, 2, [
                    [11, 1, title]
                ]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('updateGroupCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def getGroupCallUrlInfo(self, urlId):
        params = [
            [12, 2, [
                [11, 1, urlId]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getGroupCallUrlInfo', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)

    def joinChatByCallUrl(self, urlId):
        params = [
            [12, 2, [
                [11, 1, urlId],
                [8, 2, self.getCurrReqId()]
            ]]
        ]
        sqrd = self.generateDummyProtocol('joinChatByCallUrl', params, 3)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CALL_ENDPOINT ,sqrd, 3)