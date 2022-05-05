# -*- coding: utf-8 -*-


class ShopService(object):
    ShopService_REQ_TYPE = 3
    ShopService_RES_TYPE = 3

    def __init__(self):
        pass

    def getProduct(self, shopId, productId, language="zh-TW", country="TW"):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 10, 103, 101, 116,
                80, 114, 111, 100, 117, 99, 116, 0, 0, 0, 0]
        sqrd += [11, 0, 2, 0, 0, 0, len(shopId)]  # e.g. stickershop
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd)

    def getProductsByAuthor(self, authorId, productType=1):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getProductsByAuthor') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [8, 0, 1] + self.getIntBytes(productType)
        sqrd += [11, 0, 2] + self.getStringBytes(authorId)
        sqrd += [8, 0, 3] + self.getIntBytes(0)
        sqrd += [8, 0, 4] + self.getIntBytes(100)
        sqrd += [2, 0, 6, int(True)]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd)

    def getStudentInformation(self):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getStudentInformation') + [0, 0, 0, 0]
        sqrd += [12, 0, 2]
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd)

    def canReceivePresent(self, shopId, productId, recipientMid):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('canReceivePresent') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(shopId)
        sqrd += [11, 0, 3] + self.getStringBytes(productId)
        sqrd += [12, 0, 4]
        sqrd += [11, 0, 1] + self.getStringBytes('zh_TW')  # language
        sqrd += [11, 0, 2] + self.getStringBytes('TW')  # country
        sqrd += [0]
        sqrd += [11, 0, 5] + self.getStringBytes(recipientMid)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd)

    def getOwnedProductSummaries(self, shopId, offset=0, limit=200, language='zh_TW', country='TW'):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getOwnedProductSummaries') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(shopId)
        sqrd += [8, 0, 3] + self.getIntBytes(offset)
        sqrd += [8, 0, 4] + self.getIntBytes(limit)
        sqrd += [12, 0, 5]
        sqrd += [11, 0, 1] + self.getStringBytes(language)
        sqrd += [11, 0, 2] + self.getStringBytes(country)
        sqrd += [0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd)

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
            [12, 1, [  # Shop_ShowcaseRequest
                [8, 1, productType],
                [8, 2, showcaseType],
                [8, 3, subType],
                [11, 4, continuationToken],
                [8, 5, limit],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getShowcaseV3', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getProductV2(self, productType: int, productId: str, carrierCode: str = "", saveBrowsingHistory: bool = True):
        params = [
            [12, 2, [
                [8, 1, productType],
                [11, 2, productId],
                [11, 3, carrierCode],
                [2, 4, saveBrowsingHistory],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getProductV2', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getProductByVersion', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'placePurchaseOrderForFreeProduct', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'placePurchaseOrderWithLineCoin', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'placePurchaseOrderWithIAP', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getOwnedProducts', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getPurchasedProducts', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getReceivedPresents', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getSentPresents', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def notifyProductEvent(self, shopId: str, productId: str, productVersion: int, productEvent: int):
        params = [
            [11, 2, shopId],  # sticonshop
            [11, 3, productId],  # 1
            [10, 4, productVersion],  # 3
            [10, 5, productEvent],  # 16
        ]
        sqrd = self.generateDummyProtocol(
            'notifyProductEvent', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getProductValidationScheme(self, shopId: str, productId: str, productVersion: int):
        params = [
            [11, 2, shopId],
            [11, 3, productId],
            [10, 4, productVersion],
        ]
        sqrd = self.generateDummyProtocol(
            'getProductValidationScheme', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'validateProduct', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getProductsByBillingItemId(self, shopId: str, billingItemIds: list, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [15, 3, [11, billingItemIds]]
            [12, 4, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getProductsByBillingItemId', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getUpdates(self, shopId: str, language: str = 'zh_TW', country: str = 'TW'):
        params = [
            [11, 2, shopId],
            [12, 3, [
                [11, 1, language],
                [11, 2, country],
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getUpdates', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'searchProductsV2', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getAggregatedHomeV2(self, showcaseRequests: list, enableEditorsPickBanner: bool = True, enableAuthorList: bool = True, enableKeywordSticker: bool = True, enableDetailedEditorsPick: bool = True, enableDetailedCategory: bool = True, enableCategoryList: bool = True, enableTagsList: bool = True):
        params = [
            [12, 2, [
                [15, 1, [12, showcaseRequests]],  # Shop_ShowcaseRequest
                [2, 2, enableEditorsPickBanner],
                [2, 3, enableAuthorList],
                [2, 4, enableKeywordSticker],
                [2, 5, enableDetailedEditorsPick],
                [2, 6, enableDetailedCategory],
                [2, 7, enableCategoryList],
                [2, 8, enableTagsList],
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getAggregatedHomeV2', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getAggregatedHomeNative(self, productType: int):
        params = [
            [12, 2, [
                [8, 1, productType],
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getAggregatedHomeNative', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getDynamicHomeNative(self, productType: int = 1):
        params = [
            [12, 2, [
                [8, 1, productType],
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getDynamicHomeNative', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getAggregatedPremiumHome(self, showcaseRequests: list):
        params = [
            [12, 2, [
                [15, 1, [12, showcaseRequests]],  # Shop_ShowcaseRequest
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getAggregatedPremiumHome', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getAggregatedShowcaseV4(self, productType: int, showcaseRequests: list):
        params = [
            [12, 2, [
                [8, 1, productType],
                [15, 2, [12, showcaseRequests]],  # Shop_ShowcaseRequest
            ]],
        ]
        sqrd = self.generateDummyProtocol(
            'getAggregatedShowcaseV4', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getRecommendationForUser', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getRecommendationList', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

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
        sqrd = self.generateDummyProtocol(
            'getCategories', params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def removeProductFromSubscriptionSlot(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeProductFromSubscriptionSlot is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "removeProductFromSubscriptionSlot", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getRecommendOa(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRecommendOa is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRecommendOa", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionCampaigns(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionCampaigns is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionCampaigns", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def buyMustbuyProduct(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("buyMustbuyProduct is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "buyMustbuyProduct", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionPlans(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionPlans is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionPlans", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def previewCustomizedImageText(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("previewCustomizedImageText is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "previewCustomizedImageText", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getBrowsingHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBrowsingHistory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBrowsingHistory", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def deleteAllBrowsingHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("deleteAllBrowsingHistory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "deleteAllBrowsingHistory", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionShowcase(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionShowcase is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionShowcase", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getExperiments(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getExperiments is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getExperiments", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getResourceFile(self):
        params = [
            [12, 2, [
                [12, 1, []], # tagClusterFileRequest
                [2, 2, False], # staging
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "getResourceFile", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getExperimentsV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getExperimentsV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getExperimentsV2", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getAutoSuggestionShowcase(self, productType: int = 1, suggestionType: int = 0):
        """
        - suggestionType:
            NOT_PURCHASED(0),
            SUBSCRIPTION(1);
        """
        params = [
            [12, 2, [
                [8, 1, productType],
                [8, 2, suggestionType]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "getAutoSuggestionShowcase", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def sendReportForShop(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("sendReport is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "sendReport", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getOldSticonMapping(self, lastUpdatedTimeMillis: int = 1567749600000):
        params = [
            [12, 2, [
                [10, 1, lastUpdatedTimeMillis]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "getOldSticonMapping", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getEditorsPickShowcase(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getEditorsPickShowcase is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getEditorsPickShowcase", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getPurchasedSubscriptions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPurchasedSubscriptions is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPurchasedSubscriptions", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getAuthorList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAuthorList is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getAuthorList", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def changeSubscription(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("changeSubscription is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "changeSubscription", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionStatus(self):
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionStatus", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def findRestorablePlan(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findRestorablePlan is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findRestorablePlan", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def purchaseSubscription(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("purchaseSubscription is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "purchaseSubscription", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSimilarImageShowcase(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSimilarImageShowcase is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSimilarImageShowcase", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def setCustomizedImageText(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setCustomizedImageText is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "setCustomizedImageText", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSuggestResources(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestResources is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSuggestResources", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getProductSummariesInSubscriptionSlots(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "getProductSummariesInSubscriptionSlots is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProductSummariesInSubscriptionSlots", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getProductsByCategory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProductsByCategory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProductsByCategory", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getProductsByTags(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProductsByTags is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProductsByTags", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSuggestDictionarySetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestDictionarySetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSuggestDictionarySetting", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSuggestResourcesV2(self, productType: int, productIds: list):
        params = [
            [12, 2, [
                [8, 1, productType],  # 3
                [15, 2, [11, productIds]],  # ['5ac1bfd5040ab15980c9b435']
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            "getSuggestResourcesV2", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.LINE_UNIFIED_SHOP_ENDPOINT, sqrd, self.ShopService_RES_TYPE)

    def getAuthorsLatestProducts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAuthorsLatestProducts is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getAuthorsLatestProducts", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def addProductToSubscriptionSlot(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("addProductToSubscriptionSlot is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "addProductToSubscriptionSlot", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionRecommendations(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionRecommendations is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionRecommendations", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def saveStudentInformation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("saveStudentInformation is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "saveStudentInformation", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getProductsByTagsV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProductsByTagsV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProductsByTagsV2", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getTags(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getTags is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getTags", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def produceInteractionEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("produceInteractionEvent is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "produceInteractionEvent", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def restoreSubscription(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("restoreSubscription is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "restoreSubscription", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def verifyBirthdayGiftAssociationToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "verifyBirthdayGiftAssociationToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "verifyBirthdayGiftAssociationToken", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getShopPopups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopups is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopups", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionSlotStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionSlotStatus is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionSlotStatus", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getSubscriptionSlotHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSubscriptionSlotHistory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSubscriptionSlotHistory", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)

    def getProductKeyboardGlobalSetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProductKeyboardGlobalSetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getProductKeyboardGlobalSetting", params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH, sqrd, self.ShopService_RES_TYPE)


    def getEventPackages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getEventPackages is not implemented")
        METHOD_NAME = "getEventPackages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getFreePackages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getFreePackages is not implemented")
        METHOD_NAME = "getFreePackages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def buyCoinProduct(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("buyCoinProduct is not implemented")
        METHOD_NAME = "buyCoinProduct"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getDefaultProducts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getDefaultProducts is not implemented")
        METHOD_NAME = "getDefaultProducts"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def reserveCoinPurchase(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reserveCoinPurchase is not implemented")
        METHOD_NAME = "reserveCoinPurchase"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def reservePayment(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reservePayment is not implemented")
        METHOD_NAME = "reservePayment"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getActivePurchaseVersions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getActivePurchaseVersions is not implemented")
        METHOD_NAME = "getActivePurchaseVersions"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getDownloads(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getDownloads is not implemented")
        METHOD_NAME = "getDownloads"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getFreePackagesWithoutEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getFreePackagesWithoutEvent is not implemented")
        METHOD_NAME = "getFreePackagesWithoutEvent"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getProductCategories(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getProductCategories is not implemented")
        METHOD_NAME = "getProductCategories"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getProductsForCategory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getProductsForCategory is not implemented")
        METHOD_NAME = "getProductsForCategory"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getPresentsReceived(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPresentsReceived is not implemented")
        METHOD_NAME = "getPresentsReceived"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getPopularPackages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPopularPackages is not implemented")
        METHOD_NAME = "getPopularPackages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getCoinUseAndRefundHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCoinUseAndRefundHistory is not implemented")
        METHOD_NAME = "getCoinUseAndRefundHistory"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getRecommendationsForProduct(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getRecommendationsForProduct is not implemented")
        METHOD_NAME = "getRecommendationsForProduct"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getActivePurchases(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getActivePurchases is not implemented")
        METHOD_NAME = "getActivePurchases"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getProductWithCarrier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getProductWithCarrier is not implemented")
        METHOD_NAME = "getProductWithCarrier"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getShowcase(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getShowcase is not implemented")
        METHOD_NAME = "getShowcase"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def searchProducts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("searchProducts is not implemented")
        METHOD_NAME = "searchProducts"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getCoinProducts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCoinProducts is not implemented")
        METHOD_NAME = "getCoinProducts"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getPurchaseHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPurchaseHistory is not implemented")
        METHOD_NAME = "getPurchaseHistory"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getPresentsSent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPresentsSent is not implemented")
        METHOD_NAME = "getPresentsSent"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getTotalBalance(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getTotalBalance is not implemented")
        METHOD_NAME = "getTotalBalance"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getCoinPurchaseHistory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCoinPurchaseHistory is not implemented")
        METHOD_NAME = "getCoinPurchaseHistory"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getProductList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getProductList is not implemented")
        METHOD_NAME = "getProductList"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def buyFreeProduct(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("buyFreeProduct is not implemented")
        METHOD_NAME = "buyFreeProduct"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def checkCanReceivePresent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("checkCanReceivePresent is not implemented")
        METHOD_NAME = "checkCanReceivePresent"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def notifyDownloaded(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifyDownloaded is not implemented")
        METHOD_NAME = "notifyDownloaded"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getCoinProductsByPgCode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCoinProductsByPgCode is not implemented")
        METHOD_NAME = "getCoinProductsByPgCode"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getProductListWithCarrier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getProductListWithCarrier is not implemented")
        METHOD_NAME = "getProductListWithCarrier"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def getNewlyReleasedPackages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getNewlyReleasedPackages is not implemented")
        METHOD_NAME = "getNewlyReleasedPackages"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd,  self.ShopService_RES_TYPE)

    def purchaseForSelf(self):
        METHOD_NAME = "purchaseForSelf"
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.ShopService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ShopService_API_PATH ,sqrd, self.ShopService_RES_TYPE)