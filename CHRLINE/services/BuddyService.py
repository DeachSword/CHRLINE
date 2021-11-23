# -*- coding: utf-8 -*-
import time
import json


class BuddyService(object):

    def __init__(self):
        pass

    def getPromotedBuddyContacts(self, language="zh_TW", country="TW"):
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('getPromotedBuddyContacts') + [0, 0, 0, 0]
        sqrd += [11, 0, 2] + self.getStringBytes(language)
        sqrd += [11, 0, 3] + self.getStringBytes(country)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_BUDDY_ENDPOINT, sqrd)

    def getBuddyCategoryView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyCategoryView is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyCategoryView", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyChatBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBarV2", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyChatBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBar", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getCountriesHavingBuddy(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCountriesHavingBuddy is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesHavingBuddy", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getPopularBuddyBanner(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyBanner is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyBanner", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyStatusBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBarV2", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyDetailWithPersonal(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyDetailWithPersonal is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyDetailWithPersonal", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyLive(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLive is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyLive", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyContacts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyContacts is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyContacts", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyTopView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyTopView is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyTopView", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyCollectionEntries(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyCollectionEntries is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyCollectionEntries", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getPopularBuddyLists(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyLists is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyLists", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getNewlyReleasedBuddyIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNewlyReleasedBuddyIds is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNewlyReleasedBuddyIds", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyOnAir is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyOnAir", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyNewsView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyNewsView is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyNewsView", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getCountriesServingOfficialAccountPromotionV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "getCountriesServingOfficialAccountPromotionV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesServingOfficialAccountPromotionV2", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyStatusBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBar", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getRichMenuContents(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRichMenuContents is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRichMenuContents", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyDetail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyDetail is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyDetail", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def findBuddyContactsByQuery(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findBuddyContactsByQuery is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findBuddyContactsByQuery", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getBuddyProfilePopup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyProfilePopup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyProfilePopup", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)

    def getLatestBuddyNewsTimestamp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getLatestBuddyNewsTimestamp is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getLatestBuddyNewsTimestamp", params, BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(BuddyService_API_PATH, sqrd, BuddyService_RES_TYPE)
