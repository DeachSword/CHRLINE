# -*- coding: utf-8 -*-
import time
import json


class BuddyService(object):
    BuddyService_REQ_TYPE = 3
    BuddyService_RES_TYPE = 3
    BuddyService_API_PATH = None

    def __init__(self):
        self.BuddyService_API_PATH = self.LINE_BUDDY_ENDPOINT

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
            "getBuddyCategoryView", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyChatBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBarV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyChatBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBar", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getCountriesHavingBuddy(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCountriesHavingBuddy is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesHavingBuddy", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getPopularBuddyBanner(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyBanner is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyBanner", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyStatusBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBarV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyDetailWithPersonal(self, buddyMid: str, attributeSet: list):
        params = [
            [11, 1, buddyMid],
            [14, 2, [11, attributeSet]]
        ]
        sqrd = self.generateDummyProtocol(
            "getBuddyDetailWithPersonal", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyLive(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLive is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyLive", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyContacts(self, language: str, country: str, classification: str, fromIndex: int, count: int):
        params = [
            [11, 2, language],
            [11, 3, country],
            [11, 4, classification],
            [10, 5, fromIndex],
            [8, 6, count],
        ]
        sqrd = self.generateDummyProtocol(
            "getBuddyContacts", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyTopView(self, language: str, country: str):
        """REMOVED"""
        params = [
            [11, 2, language],
            [11, 3, country],
        ]
        sqrd = self.generateDummyProtocol(
            "getBuddyTopView", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyCollectionEntries(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyCollectionEntries is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyCollectionEntries", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getPopularBuddyLists(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyLists is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyLists", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getNewlyReleasedBuddyIds(self):
        params = []
        sqrd = self.generateDummyProtocol(
            "getNewlyReleasedBuddyIds", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyOnAir is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyOnAir", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyNewsView(self, language: str, country: str, fromIndex: int, count: int):
        """REMOVED"""
        params = [
            [11, 2, language],
            [11, 3, country],
            [10, 4, fromIndex],
            [8, 5, count],
        ]
        sqrd = self.generateDummyProtocol(
            "getBuddyNewsView", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getCountriesServingOfficialAccountPromotionV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "getCountriesServingOfficialAccountPromotionV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesServingOfficialAccountPromotionV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyStatusBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBar", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getRichMenuContents(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRichMenuContents is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRichMenuContents", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyDetail(self, buddyMid: str):
        params = [
            [11, 4, buddyMid]
        ]
        sqrd = self.generateDummyProtocol(
            "getBuddyDetail", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def findBuddyContactsByQuery(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findBuddyContactsByQuery is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findBuddyContactsByQuery", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getBuddyProfilePopup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyProfilePopup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyProfilePopup", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)

    def getLatestBuddyNewsTimestamp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getLatestBuddyNewsTimestamp is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getLatestBuddyNewsTimestamp", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE)
