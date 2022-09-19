# -*- coding: utf-8 -*-
"""
CHRLINE Timeline Story.

Created by DeachSword/YinMo
Created Time: 2022-09-19
"""

import time


class Story(object):
    def __init__(self, a: int):
        self.a = a

    @staticmethod
    def CreateStoryContent(**kwargs):
        contentBody = {
            "sourceType": kwargs["sourceType"],
            "contentType": kwargs["contentType"],
        }
        medias = []
        for media in kwargs["medias"]:
            medias.append(media.get())
        contentBody["media"] = medias
        if "referrerType" in kwargs is not None:
            contentBody["referrerType"] = kwargs["referrerType"]
        if "meta" in kwargs is not None:
            contentBody["meta"] = kwargs["meta"]
        shareInfoBody = {"shareType": kwargs["shareType"]}
        if "shareGroupIds" in kwargs is not None:
            shareInfoBody["shareGroupIds"] = kwargs["shareGroupIds"]
        return {"content": contentBody, "shareInfo": shareInfoBody}

    @staticmethod
    def DeleteStoryContent(**kwargs):
        return {"contentId": kwargs["contentId"]}

    @staticmethod
    def GetStoryList(**kwargs):
        userInfosBody = []
        clickedUserInfo = {"userMid": kwargs["userMid"], "tsId": ""}
        for mid in kwargs["userMids"]:
            info = {
                "userMid": mid,
                # guideId": guideId,
                "tsId": "",
            }
            userInfosBody.append(info)
        return {"userInfos": userInfosBody, "clickedUserInfo": clickedUserInfo}

    @staticmethod
    def GetStory(**kwargs):
        return {"userMid": kwargs["userMid"]}

    @staticmethod
    def GetStoryContent(**kwargs):
        return {"contentId": kwargs["contentId"]}

    @staticmethod
    def ReadStoryContent(**kwargs):
        return {
            # "userMid": kwargs['userMid'],
            "contentId": kwargs["contentId"],
            "createdTime": int(time.time() * 1000),
            "tsId": kwargs["tsId"],
        }

    @staticmethod
    def LikeStoryContent(**kwargs):
        return {
            "contentId": kwargs["contentId"],
            "tsId": kwargs["tsId"],
            "like": kwargs["like"],
            "likeType": kwargs["likeType"],
        }

    @staticmethod
    def StoryContentLikeList(**kwargs):
        baseBody = {
            # "userMid": kwargs['userMid'],
            "contentId": kwargs["contentId"],
            "include": kwargs["include"],
            "likeType": kwargs["likeType"],
            "size": kwargs["size"],
        }
        if "scrollId" in kwargs:
            baseBody["scrollId"] = kwargs["scrollId"]
        return baseBody

    @staticmethod
    def ReportStoryContent(**kwargs):
        return {
            "contentId": kwargs["contentId"],
            "type": kwargs["type"],
        }

    @staticmethod
    def SendStoryMessage(**kwargs):
        return {
            "contentId": kwargs["contentId"],
            "to": kwargs["to"],
            "message": kwargs["message"],
        }

    @staticmethod
    def GetStoryGuild(**kwargs):
        return {
            "guideId": kwargs["guideId"],
        }

    @staticmethod
    def NotifyStoryGuild(**kwargs):
        return {
            # "userMid": kwargs['userMid'],
            "guideId": kwargs["guideId"],
            "guideContentId": kwargs["guideContentId"],
            "notifyType": kwargs["notifyType"],
            "value": kwargs["value"],
            "tsId": kwargs["tsId"],
        }

    @staticmethod
    def GetOwnerStoryContentList(**kwargs):
        baseBody = {
            "order": kwargs["order"],
            "size": kwargs["size"],
        }
        if "lastContentId" in kwargs:
            baseBody["lastContentId"] = kwargs["lastContentId"]
        return baseBody

    @staticmethod
    def GetOwnerStoryContentViewList(**kwargs):
        return {
            "contentId": kwargs["contentId"],
            "order": kwargs["order"],
            "size": kwargs["size"],
        }

    @staticmethod
    def GetOwnerStoryContentViewMoreList(**kwargs):
        return {
            "lastContentId": kwargs["lastContentId"],
            "direction": kwargs["direction"],
            "order": kwargs["order"],
            "size": kwargs["size"],
        }

    @staticmethod
    def GetRecentStoryList(**kwargs):
        baseBody = {
            "lastRequestTime": kwargs["lastRequestTime"],
        }
        if "lastTimelineVisitTime" in kwargs:
            baseBody["lastTimelineVisitTime"] = kwargs["lastTimelineVisitTime"]
        return baseBody

    @staticmethod
    def GetStoryContentViewerList(**kwargs):
        baseBody = {
            "contentId": kwargs["contentId"],
            "size": kwargs["size"],
        }
        if "scrollId" in kwargs:
            baseBody["scrollId"] = kwargs["scrollId"]
        return baseBody

    @staticmethod
    def GetStoryChallengeeContentList(**kwargs):
        baseBody = {
            "guideId": kwargs["guideId"],
            "direction": kwargs["direction"],
            "size": kwargs["size"],
        }
        if "lastContentSeq" in kwargs:
            baseBody["lastContentSeq"] = kwargs["lastContentSeq"]
        if "popularContentIds" in kwargs:
            baseBody["popularContentIds"] = kwargs["popularContentIds"]
        return baseBody

    @staticmethod
    def GetNewStory(**kwargs):
        baseBody = {
            "newStoryTypes": [
                "WRITE",
                "MY",
                "GUIDE",
                "CHALLENGE",
                "USER",
                "ARCHIVE",
                "LIVE",
                "INVALID",
            ],
        }
        if "lastTimelineVisitTime" in kwargs:
            baseBody["lastTimelineVisitTime"] = kwargs["lastTimelineVisitTime"]
        return baseBody

    def GetApiPath(self, path):
        return f"/st/api/v{self.a}/{path}"


class StoryMedia(object):
    def __init__(self, oid: str, ohash: str, oType: str):
        self.oid = oid
        self.ohash = ohash
        self.oType = oType

    def get(self):
        return {
            "oid": self.oid,
            "service": "story",
            "sid": "st",
            "hash": self.ohash,
            "extra": {"playtime": 99999999999999999999999999},
            "mediaType": self.oType,
        }
