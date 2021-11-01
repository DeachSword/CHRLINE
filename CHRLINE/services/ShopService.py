# -*- coding: utf-8 -*-
import time
import json

class ShopService(object):
    SHOPS_REQ_TYPE = 3
    SHOPS_RES_TYPE = 3

    def __init__(self):
        pass
        
    def getProduct(self, shopId, productId, language="zh-TW", country="TW"):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116, 80, 114, 111, 100, 117, 99, 116, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(shopId)] # e.g. stickershop
        for value in shopId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 3, 0, 0, 0, len(productId)]
        for value in productId:
            sqrd.append(ord(value))
        sqrd += [12, 0, 4]
        sqrd += [11, 0, 1, 0, 0, 0, len(language)]
        for value in language:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(country)]
        for value in country:
            sqrd.append(ord(value))
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd)

    def getProductsByAuthor(self, authorId, productType=1):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getProductsByAuthor') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [8, 0, 1] + self.getIntBytes(productType)
        sqrd += [11, 0, 2] + self.getStringBytes(authorId)
        sqrd += [8, 0, 3] + self.getIntBytes(0)
        sqrd += [8, 0, 4] + self.getIntBytes(100)
        sqrd += [2, 0, 6, int(True)]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd)
    
    def getStudentInformation(self):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getStudentInformation') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd)
    
    def canReceivePresent(self, shopId, productId, recipientMid):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('canReceivePresent') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(shopId)
        sqrd += [11, 0, 3] + self.getStringBytes(productId)
        sqrd += [12, 0, 4]
        sqrd += [11, 0, 1] + self.getStringBytes('zh_TW') #language
        sqrd += [11, 0, 2] + self.getStringBytes('TW') #country
        sqrd += [0]
        sqrd += [11, 0, 5] + self.getStringBytes(recipientMid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd)
    
    def getOwnedProductSummaries(self, shopId, offset=0, limit=200, language='zh_TW', country='TW'):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('getOwnedProductSummaries') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(shopId)
        sqrd += [8, 0, 3] + self.getIntBytes(offset)
        sqrd += [8, 0, 4] + self.getIntBytes(limit)
        sqrd += [12, 0, 5]
        sqrd += [11, 0, 1] + self.getStringBytes(language)
        sqrd += [11, 0, 2] + self.getStringBytes(country)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd)
    
    def getShowcaseV3(self, productType: int, showcaseType: int, subType: int, continuationToken: str = None, limit: int = 20):
        """
        - productType
            STICKER(1),
            THEME(2),
            STICON(3);
        - showcaseType
            UNPURCHASED(1),
            SUBSCRIPTION(2);
        - subType
            GENERAL(0),
            CREATORS(1),
            STICON(2);
        """
        params = [
            [12, 1, [ # Shop_ShowcaseRequest
                [8, 1, productType],
                [8, 2, showcaseType],
                [8, 3, subType],
                [11, 4, continuationToken],
                [8, 5, limit],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getShowcaseV3', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getProductV2(self, productType: int, productId: str, carrierCode: str, saveBrowsingHistory: bool = True):
        params = [
            [12, 2, [
                [8, 1, productType],
                [11, 2, productId],
                [11, 3, carrierCode],
                [2, 4, saveBrowsingHistory],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getProductV2', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getProductByVersion(self, shopId: str, productId: str, productVersion: int, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [11, 3, productId],
            [10, 4, productVersion],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getProductByVersion', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def placePurchaseOrderForFreeProduct(self, shopId: str, productId: str, recipientMid: str, price: str, amount: str, priceString: str, enableLinePointAutoExchange: bool = True, language: str = 'zh_TW', country: str = 'TW', presentAttributes: dict = {}):
        params = [
            [12, 2, [
                [11, 1, shopId],
                [11, 2, productId],
                [11, 5, recipientMid],
                [12, 11, [
                    [11, 1, price],
                    [11, 2, amount],
                    [11, 5, priceString],
                ]],
                [2, 12, enableLinePointAutoExchange],
                [12, 21, [
                    [11, 1, language],
                    [11, 2, country],
                ]],
                [13, 31, [11, 11, presentAttributes]],
            ]],
        ]
        sqrd = self.generateDummyProtocol('placePurchaseOrderForFreeProduct', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def placePurchaseOrderWithLineCoin(self, shopId: str, productId: str, recipientMid: str, price: str, amount: str, priceString: str, enableLinePointAutoExchange: bool = True, language: str = 'zh_TW', country: str = 'TW', presentAttributes: dict = {}):
        params = [
            [12, 2, [
                [11, 1, shopId],
                [11, 2, productId],
                [11, 5, recipientMid],
                [12, 11, [
                    [11, 1, price],
                    [11, 2, amount],
                    [11, 5, priceString],
                ]],
                [2, 12, enableLinePointAutoExchange],
                [12, 21, [
                    [11, 1, language],
                    [11, 2, country],
                ]],
                [13, 31, [11, 11, presentAttributes]],
            ]],
        ]
        sqrd = self.generateDummyProtocol('placePurchaseOrderWithLineCoin', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def placePurchaseOrderWithIAP(self, shopId: str, productId: str, recipientMid: str, price: str, amount: str, priceString: str, enableLinePointAutoExchange: bool = True, language: str = 'zh_TW', country: str = 'TW', presentAttributes: dict = {}):
        params = [
            [12, 2, [
                [11, 1, shopId],
                [11, 2, productId],
                [11, 5, recipientMid],
                [12, 11, [
                    [11, 1, price],
                    [11, 2, amount],
                    [11, 5, priceString],
                ]],
                [2, 12, enableLinePointAutoExchange],
                [12, 21, [
                    [11, 1, language],
                    [11, 2, country],
                ]],
                [13, 31, [11, 11, presentAttributes]],
            ]],
        ]
        sqrd = self.generateDummyProtocol('placePurchaseOrderWithIAP', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getOwnedProducts(self, shopId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [8, 3, offset],
            [8, 4, limit],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getOwnedProducts', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getPurchasedProducts(self, shopId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [8, 3, offset],
            [8, 4, limit],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getPurchasedProducts', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getReceivedPresents(self, shopId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [8, 3, offset],
            [8, 4, limit],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getReceivedPresents', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getSentPresents(self, shopId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [8, 3, offset],
            [8, 4, limit],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getSentPresents', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def notifyProductEvent(self, shopId: str, productId: str, productVersion: int, productEvent: int):
        params = [
            [11, 2, shopId],
            [11, 3, productId],
            [10, 4, productVersion],
            [10, 5, productEvent],
        ]
        sqrd = self.generateDummyProtocol('notifyProductEvent', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getProductValidationScheme(self, shopId: str, productId: str, productVersion: int):
        params = [
            [11, 2, shopId],
            [11, 3, productId],
            [10, 4, productVersion],
        ]
        sqrd = self.generateDummyProtocol('getProductValidationScheme', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def validateProduct(self, shopId: str, productId: str, productVersion: int, key: str, offset: int, size: int, authCode: str):
        params = [
            [11, 2, shopId],
            [11, 3, productId],
            [10, 4, productVersion],
            [12, 5, [
                [12, 1, [
                    [11, 10, key],
                    [10, 11, offset],
                    [10, 12, size],
                ]],
                [11, 10, authCode]
            ]],
        ]
        sqrd = self.generateDummyProtocol('validateProduct', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getProductsByBillingItemId(self, shopId: str, billingItemIds: list, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [15, 3, [11, billingItemIds]]
            [12, 4, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getProductsByBillingItemId', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getUpdates(self, shopId: str, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [12, 3, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getUpdates', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def searchProductsV2(self, query: str, productTypes: list, subtypes: list, priceTiers: list, stickerResourceTypes: list, productResourceTypes: list, continuationToken: str, limit: int = 10, deprecatedOffsetForLineSearchServer: int = 0, sortType: int = 0, enableSearchSuggestKeywords: bool = False):
        params = [
            [12, 2, [
                [11, 1, query],
                [14, 2, [8, productTypes]],
                [14, 3, [8, subtypes]],
                [11, 4, continuationToken],
                [8, 5, limit],
                [8, 6, deprecatedOffsetForLineSearchServer],
                [14, 7, [8, priceTiers]],
                [14, 8, [8, stickerResourceTypes]],
                [8, 9, sortType],
                [10, 14, [8, productResourceTypes]],
                [2, 100, enableSearchSuggestKeywords],
                # [12, 101, [
                    # Shop_ShopFilter.h
                # ]],
            ]],
        ]
        sqrd = self.generateDummyProtocol('searchProductsV2', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getAggregatedHomeV2(self, showcaseRequests: list, enableEditorsPickBanner: bool = True, enableAuthorList: bool = True, enableKeywordSticker: bool = True, enableDetailedEditorsPick: bool = True, enableDetailedCategory: bool = True, enableCategoryList: bool = True, enableTagsList: bool = True):
        params = [
            [12, 2, [
                [15, 1, [12, showcaseRequests]], # Shop_ShowcaseRequest
                [2, 2, enableEditorsPickBanner],
                [2, 3, enableAuthorList],
                [2, 4, enableKeywordSticker],
                [2, 5, enableDetailedEditorsPick],
                [2, 6, enableDetailedCategory],
                [2, 7, enableCategoryList],
                [2, 8, enableTagsList],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getAggregatedHomeV2', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getAggregatedHomeNative(self, productType: int):
        params = [
            [12, 2, [
                [8, 1, productType],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getAggregatedHomeNative', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getDynamicHomeNative(self, productType: int = 1):
        params = [
            [12, 2, [
                [8, 1, productType],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getDynamicHomeNative', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getAggregatedPremiumHome(self, showcaseRequests: list):
        params = [
            [12, 2, [
                [15, 1, [12, showcaseRequests]], # Shop_ShowcaseRequest
            ]],
        ]
        sqrd = self.generateDummyProtocol('getAggregatedPremiumHome', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getAggregatedShowcaseV4(self, productType: int, showcaseRequests: list):
        params = [
            [12, 2, [
                [8, 1, productType],
                [15, 2, [12, showcaseRequests]], # Shop_ShowcaseRequest
            ]],
        ]
        sqrd = self.generateDummyProtocol('getAggregatedShowcaseV4', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getRecommendationForUser(self, shopId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [8, 3, offset],
            [8, 4, limit],
            [12, 5, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol('getRecommendationForUser', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)
    
    def getRecommendationList(self, productType: int, recommendationType: int, productId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', continuationToken: str = None, shouldShuffle: bool = False, includeStickerIds: bool = True):
        params = [
            [12, 2, [
                [11, 1, continuationToken],
                [8, 2, limit],
                [8, 3, productType],
                [8, 4, recommendationType],
                [11, 5, productId],
                # [14, 6, [8, subtypes]],
                [2, 7, shouldShuffle],
                [2, 8, includeStickerIds],
                # [12, 9, shopFilter],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getRecommendationList', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)

    def getCategories(self, productType: int, recommendationType: int, productId: str, offset: int = 0, limit: int = 20, language: str = 'zh_TW', continuationToken: str = None, shouldShuffle: bool = False, includeStickerIds: bool = True):
        params = [
            [12, 2, [
                [11, 1, continuationToken],
                [8, 2, limit],
                [8, 3, productType],
                [8, 4, recommendationType],
                [11, 5, productId],
                # [14, 6, [8, subtypes]],
                [2, 7, shouldShuffle],
                [2, 8, includeStickerIds],
                # [12, 9, shopFilter],
            ]]
        ]
        sqrd = self.generateDummyProtocol('getCategories', params, self.SHOPS_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT ,sqrd, self.SHOPS_RES_TYPE)