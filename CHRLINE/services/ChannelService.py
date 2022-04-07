# -*- coding: utf-8 -*-

class ChannelService(object):

    def __init__(self):
        pass

    def issueChannelToken(self, channelId="1341209950"):
        METHOD_NAME = "issueChannelToken"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes('issueChannelToken') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(channelId)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT, sqrd, readWith=f"ChannelService.{METHOD_NAME}")

    def approveChannelAndIssueChannelToken(self, channelId="1341209950"):
        METHOD_NAME = "approveChannelAndIssueChannelToken"
        sqrd = [128, 1, 0, 1] + \
            self.getStringBytes(
                'approveChannelAndIssueChannelToken') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(channelId)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT, sqrd, readWith=f"ChannelService.{METHOD_NAME}")

    def getChannelInfo(self, channelId):
        METHOD_NAME = "getChannelInfo"
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 103, 101, 116, 67, 104, 97, 110, 110,
                101, 108, 73, 110, 102, 111, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT, sqrd, readWith=f"ChannelService.{METHOD_NAME}")

    def getCommonDomains(self, lastSynced=0):
        METHOD_NAME = "getCommonDomains"
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 67, 111, 109,
                109, 111, 110, 68, 111, 109, 97, 105, 110, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT, sqrd, readWith=f"ChannelService.{METHOD_NAME}")

    def issueRequestTokenWithAuthScheme(self, channelId, otpId, authScheme, returnUrl):
        METHOD_NAME = "issueRequestTokenWithAuthScheme"
        sqrd = [128, 1, 0, 1, 0, 0, 0, 31, 105, 115, 115, 117, 101, 82, 101, 113, 117, 101, 115, 116, 84,
                111, 107, 101, 110, 87, 105, 116, 104, 65, 117, 116, 104, 83, 99, 104, 101, 109, 101, 0, 0, 0, 0]
        sqrd += [11, 0, 1, 0, 0, 0, len(channelId)]
        for value in channelId:
            sqrd.append(ord(value))
        sqrd += [11, 0, 2, 0, 0, 0, len(otpId)]
        for value in otpId:
            sqrd.append(ord(value))
        sqrd += [15, 0, 3, 11, 0, 0, 0, len(authScheme)]
        for mid in authScheme:
            sqrd += [0, 0, 0, len(mid)]
            for value in mid:
                sqrd.append(ord(value))
        sqrd += [11, 0, 4, 0, 0, 0, len(returnUrl)]
        for value in returnUrl:
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT, sqrd, readWith=f"ChannelService.{METHOD_NAME}")

    def getReturnUrlWithRequestTokenForAutoLogin(self, url, sessionString=None):
        METHOD_NAME = "getReturnUrlWithRequestTokenForAutoLogin"
        params = [
            [12, 2, [
                [11, 1, url],
                [11, 2, sessionString]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getReturnUrlWithRequestTokenForAutoLogin', params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_CHANNEL_ENDPOINT_V4, sqrd, 4, 
            readWith=f"ChannelService.{METHOD_NAME}")

    def getWebLoginDisallowedUrl(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getWebLoginDisallowedUrl is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getWebLoginDisallowedUrl", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def updateChannelNotificationSetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateChannelNotificationSetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateChannelNotificationSetting", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def updateChannelSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateChannelSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateChannelSettings", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def syncChannelData(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("syncChannelData is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "syncChannelData", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getUpdatedChannelIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUpdatedChannelIds is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getUpdatedChannelIds", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getChannels(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannels is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannels", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getDomains(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getDomains is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getDomains", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def revokeAccessToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("revokeAccessToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "revokeAccessToken", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def approveChannelAndIssueRequestToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "approveChannelAndIssueRequestToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "approveChannelAndIssueRequestToken", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getChannelNotificationSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelNotificationSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelNotificationSettings", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def reserveCoinUse(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reserveCoinUse is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reserveCoinUse", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getApprovedChannels(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getApprovedChannels is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getApprovedChannels", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def issueRequestToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueRequestToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueRequestToken", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def issueRequestTokenForAutoLogin(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueRequestTokenForAutoLogin is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueRequestTokenForAutoLogin", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getNotificationBadgeCount(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNotificationBadgeCount is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNotificationBadgeCount", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def revokeChannel(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("revokeChannel is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "revokeChannel", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getChannelSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelSettings", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def issueOTP(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueOTP is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueOTP", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def fetchNotificationItems(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("fetchNotificationItems is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "fetchNotificationItems", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getFriendChannelMatrices(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getFriendChannelMatrices is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getFriendChannelMatrices", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def getChannelNotificationSetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelNotificationSetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelNotificationSetting", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE)

    def issueChannelAppView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("issueChannelAppView is not implemented")
        METHOD_NAME = "issueChannelAppView"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ChannelService_API_PATH, sqrd,  self.ChannelService_RES_TYPE)

    def getWebLoginDisallowedURL(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getWebLoginDisallowedURL is not implemented")
        METHOD_NAME = "getWebLoginDisallowedURL"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.ChannelService_API_PATH, sqrd,  self.ChannelService_RES_TYPE)
