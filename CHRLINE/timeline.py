# -*- coding: utf-8 -*-
import json
import uuid

from .BIZ.TL.ST import Story, StoryMedia


def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].can_use_timeline:
            return func(*args, **kwargs)
        else:
            raise Exception("can't use Timeline func")

    return checkLogin


class Timeline:
    def __init__(self):
        TIMELINE_CHANNEL_ID = "1341209950"
        self.can_use_timeline = False
        try:
            if self.APP_TYPE in ["CHROMEOS"]:
                TIMELINE_CHANNEL_ID = "1341209850"
            self.server.timelineHeaders = {
                "x-line-application": self.server.Headers["x-line-application"],
                "User-Agent": self.server.Headers["User-Agent"],
                "X-Line-Mid": self.mid,
                "X-Line-Access": self.authToken,
                "X-Line-ChannelToken": self.checkAndGetValue(
                    self.approveChannelAndIssueChannelToken(TIMELINE_CHANNEL_ID),
                    "channelAccessToken",
                    5,
                ),
                "x-lal": self.LINE_LANGUAGE,
                "X-LAP": "5",
                "X-LPV": "1",
                "X-LSR": self.LINE_SERVICE_REGION,
                "x-line-bdbtemplateversion": "v1",
                "x-line-global-config": "discover.enable=true; follow.enable=true"
                # "X-Line-PostShare": "true"
                # "X-Line-StoryShare": "true"
            }
            self.can_use_timeline = True
            if self.APP_TYPE in ["CHROMEOS"]:
                self.server.timelineHeaders[
                    "origin"
                ] = "chrome-extension://CHRLINE-v2.5.0-rc-will-not-be-released"

            # BIZ
            self.story = Story(8)

            # OTO
            self.otoMids = {}
            self.syncOtoAccount()
        except Exception as e:
            self.log(f"can't use Timeline: {e}")

    """ TIMELINE """

    @loggedIn
    def getSocialProfileDetail(
        self,
        mid,
        withSocialHomeInfo=True,
        postLimit=10,
        likeLimit=6,
        commentLimit=10,
        storyVersion="v7",
        timelineVersion="v57",
        postId=None,
        updatedTime=None,
    ):
        params = {
            "homeId": mid,
            "withSocialHomeInfo": withSocialHomeInfo,
            "postLimit": postLimit,
            "likeLimit": likeLimit,
            "commentLimit": commentLimit,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
        }
        if postId is not None:
            # post offset
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lhm": "GET"}
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/hm/api/v1/home/socialprofile/post.json", params
        )
        r = self.server.postContent(url, headers=hr, data="")
        return r.json()

    @loggedIn
    def getSocialProfileMediaDetail(
        self,
        mid: str,
        withSocialHomeInfo: bool = True,
        postLimit: int = 10,
        withStory: bool = True,
        storyVersion: str = "v7",
        timelineVersion: str = "v57",
        postId: str = None,
        updatedTime: int = None,
    ):
        params = {
            "homeId": mid,
            "withSocialHomeInfo": withSocialHomeInfo,
            "withStory": withStory,
            "postLimit": postLimit,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
        }
        if postId is not None:
            # post offset
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lhm": "GET"}
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN,
            "/hm/api/v1/home/socialprofile/mediapost.json",
            params,
        )
        r = self.server.postContent(url, headers=hr, data="")
        return r.json()

    @loggedIn
    def getProfileDetail(
        self, mid, styleMediaVersion="v2", storyVersion="v7", timelineVersion="v57"
    ):
        params = {
            "homeId": mid,
            "styleMediaVersion": styleMediaVersion,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
            "profileBannerRevision": 0,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                # why get follow count with this?
                "x-line-global-config": "discover.enable=true; follow.enable=true",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/hm/api/v1/home/profile.json", params
        )
        r = self.server.postContent(url, headers=hr, data="")
        return r.json()

    @loggedIn
    def updateProfileDetail(self, mid):
        params = {}
        data = {
            "homeId": self.mid,
            "styleMediaVersion": "v2",
            "userStyleMedia": {
                "profile": {"displayName": "鴻"},
            },
            "storyShare": "false",
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lhm": "POST"}
        )
        url = self.LINE_HOST_DOMAIN + "/hm/api/v1/home/profile"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getProfileCoverDetail(self, mid):
        params = {"homeId": mid}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/hm/api/v1/home/cover.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def updateProfileCoverById(
        self, objid: str = None, vObjid: str = None, storyShare: bool = False
    ):
        data = {"homeId": self.mid, "storyShare": storyShare, "meta": {}}  # heh
        if objid is None and vObjid is None:
            raise ValueError("objid is None")
        if objid:
            data["coverObjectId"] = objid
        if vObjid:
            data["videoCoverObjectId"] = vObjid
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        r = self.server.postContent(
            self.LINE_HOST_DOMAIN + "/hm/api/v1/home/cover.json",
            headers=hr,
            data=json.dumps(data),
        )
        return r.json()

    @loggedIn
    def updateProfileCoverById2(self, objId: str):
        params = {
            "coverImageId": objId,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v41/home/updateCover.json", params
        )
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getOACarousel(self):
        params = {"homeId": "ud9b11771afc46b1d9b6faa646ab3c475"}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v42/feed/carousel/oa.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getPartlyBlockContacts(self):
        params = {"id": self.mid, "limit": 30}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/mapi/v57/contacts/block/partly.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getClosedContacts(self):
        params = {"id": self.mid}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/mapi/v41/contacts/block", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getHideContacts(self, MID):
        params = {"id": self.mid}
        data = {"mid": "u67c43239c865dfce6addb41c6b3c0edd"}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/mapi/v41/contacts/hide", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getAutoOpenOption(self):
        params = {}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/mapi/v41/contact/autoopen", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getHideGrouphomeList(self):
        params = {}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ma/api/v24/grouphome/hide/list.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getNewpostStatus(self):
        params = {}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/mapi/v41/status/newpost", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getGroupProfileimageList(self):
        params = {}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v24/group/profileimage/list.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getUserProfile(self, mid: str):
        params = {"userMid": mid}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ma/api/v1/profile/get.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def getUserDetail(self, mid: str):
        params = {"userMid": mid}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ma/api/v1/userpopup/getDetail.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def syncBuddygroup(self, mid: str):
        params = {"userMid": mid, "lastUpdated": 0}
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/mapi/v41/home/buddygroup/sync", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def sendContactV2(self, homeId, targetMids):
        url = self.LINE_HOST_DOMAIN + "/hm/api/v1/home/profile/share"
        data = {
            "homeId": homeId,
            "shareType": "FLEX_OA_HOME_PROFILE_SHARING",
            "targetMids": targetMids,
        }
        r = self.server.postContent(
            url, headers=self.server.timelineHeaders, data=json.dumps(data)
        )
        result = r.json()
        if result["message"] == "success":
            return result["result"]
        else:
            return False

    @loggedIn
    def getTimelintTab(self, postLimit=20, likeLimit=6, commentLimit=10, requestTime=0):
        url = self.LINE_HOST_DOMAIN + "/tl/api/v57/timeline/tab.json"
        data = {
            "feedRequests": {
                "FEED_LIST": {
                    "version": "v57",
                    "queryParams": {
                        "postLimit": postLimit,
                        "likeLimit": likeLimit,
                        "commentLimit": commentLimit,
                        "requestTime": 0,
                        "userAction": "TAP-REFRESH_UEN",
                        "order": "RANKING",
                    },
                    "requestBody": {
                        "discover": {"contents": ["CP", "PI", "PV", "PL", "LL"]}
                    },
                },
                "STORY": {"version": "v6"},
            }
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "Content-type": "application/json", "x-lsr": "TW"},
        )
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        result = r.json()
        if result["message"] == "success":
            return result["result"]
        else:
            return False

    @loggedIn
    def updateCmtLike(self, homeId: str, noti: bool = True):
        """update note notify"""
        params = {
            "homeId": homeId,
        }
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN,
            "/mh/api/v21/grouphome/notisetting/updateCmtLike.json",
            params,
        )
        data = {"notiSet": [{"notiType": "NOTE_CMTLIKE", "noti": noti}]}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getTalkroomStatus(self, userMid: str):
        """check talkroom has updated"""
        params = {
            "userMid": userMid,
        }
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ma/api/v1/talkroom/get.json", params
        )
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getHomeProfileBridge(self, homeId: str):
        """update note notify"""
        params = {
            "homeId": homeId,
        }
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v1/home/profileBridge.json", params
        )
        data = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ POST """

    @loggedIn
    def createPost(
        self,
        homeId: str,
        text: str = None,
        sharedPostId: str = None,
        textSizeMode: str = "NORMAL",
        backgroundColor: str = "#FFFFFF",
        textAnimation: str = "NONE",
        readPermissionType: str = "ALL",
        readPermissionGids: list = None,
        holdingTime: int = None,
        stickerIds: list = None,
        stickerPackageIds: list = None,
        locationLatitudes: list = None,
        locationLongitudes: list = None,
        locationNames: list = None,
        mediaObjectIds: list = None,
        mediaObjectTypes: list = None,
        sourceType: str = "TIMELINE",
        textMeta: list = []
    ):
        """
        - readPermissionType:
            ALL,
            FRIEND,
            GROUP,
            EVENT,
            NONE;
        - textSizeMode:
            AUTO,
            NORMAL;
        - textAnimation:
            NONE,
            SLIDE,
            ZOOM,
            BUZZ,
            BOUNCE,
            BLINK;
        """
        if readPermissionGids is None:
            readPermissionGids = []
        if stickerIds is None:
            stickerIds = []
        if stickerPackageIds is None:
            stickerPackageIds = []
        if locationLatitudes is None:
            locationLatitudes = []
        if locationLongitudes is None:
            locationLongitudes = []
        if locationNames is None:
            locationNames = []
        if mediaObjectIds is None:
            mediaObjectIds = []
        if mediaObjectTypes is None:
            mediaObjectTypes = []
        if self.getToType(homeId) == 0:
            self.log(f"Can't use mid {homeId} to create post, will be get oto mid...")
            if homeId in self.otoMids:
                homeId = self.otoMids[homeId]
                self.log(f"Use oto mid {homeId} to create post...")
            else:
                self.log(f"Can't find oto mid: {homeId}, ready to create oto mid...")
                otoRes = self.createOtoAccount(self.mid, homeId)
                otoMid = otoRes.get("result", {}).get("groupId")
                if otoMid is None:
                    raise ValueError(f"Oto Mid is None: {otoRes}")
                self.log(f"Created oto mid {otoMid} to create post...")
                self.otoMids[homeId] = otoMid
                homeId = otoMid
        params = {"homeId": homeId, "sourceType": sourceType}
        postInfo = {
            "readPermission": {"type": readPermissionType, "gids": readPermissionGids},
        }
        stickers = []
        locations = []
        medias = []
        for stickerIndex, stickerId in enumerate(stickerIds):
            stickers.append(
                {
                    "id": stickerId,
                    "packageId": stickerPackageIds[stickerIndex],
                    "packageVersion": 1,
                    "hasAnimation": True,  # TODO: check it
                    "hasSound": True,  # TODO: check it
                    "stickerResourceType": "ANIMATION",  # TODO: check it
                }
            )
        for locatioIndex, locationLatitude in enumerate(locationLatitudes):
            locations.append(
                {
                    "latitude": locationLatitude,
                    "longitude": locationLongitudes[locatioIndex],
                    "name": locationNames[locatioIndex],
                }
            )
        for mediaIndex, mediaObjectId in enumerate(mediaObjectIds):
            medias.append(
                {
                    "objectId": mediaObjectId,
                    "type": mediaObjectTypes[mediaIndex],
                    # "width": 1016,
                    # "height": 453,
                    # "size": 16022,
                    "obsFace": "[]",
                }
            )
        contents = {
            "contentsStyle": {
                "textStyle": {
                    "textSizeMode": textSizeMode,
                    "backgroundColor": backgroundColor,
                    "textAnimation": textAnimation,
                },
                "mediaStyle": {"displayType": "GRID_1_A"},
            },
            "stickers": stickers,
            "locations": locations,
            "media": medias,
        }
        if holdingTime is not None:
            postInfo["holdingTime"] = holdingTime
        if text is not None:
            contents["text"] = text
        if sharedPostId is not None:
            contents["sharedPostId"] = sharedPostId
        if textMeta is not None:
            contents["textMeta"] = textMeta
        data = {"postInfo": postInfo, "contents": contents}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/create.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def updatePost(self, homeId: str, postData: dict, sourceType: str = "TIMELINE"):
        params = {"homeId": homeId, "sourceType": sourceType}
        data = postData.copy()
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/update.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def deletePost(self, homeId: str, postId: str):
        params = {"homeId": homeId, "postId": postId}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/delete.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getPost(self, mid: str, postId: str, sourceType: str = "MYHOME"):
        params = {"homeId": mid, "postId": postId, "sourceType": sourceType}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/get.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listPost(
        self,
        mid: str,
        postId: str = None,
        updatedTime: int = None,
        sourceType: str = "TALKROOM",
    ):
        """list posts for chat room.
        use postId and updatedTime to fetch next posts"""
        params = {"homeId": mid, "sourceType": sourceType}
        if postId is not None:
            params["postId"] = postId
        if updatedTime is not None:
            params["updatedTime"] = updatedTime
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/list.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def createComment(
        self,
        mid: str,
        contentId: str,
        text: str = "",
        stickerId: int = None,
        stickerPackageId: int = None,
        mediaObjectId: str = None,
        mediaObjectType: str = "PHOTO",
        mediaObjectFrom: str = "cmt",
        sourceType: str = "TIMELINE",
    ):
        params = {"homeId": mid, "sourceType": sourceType}
        contentsList = []
        if stickerId is not None:
            contentsList.append(
                {
                    "categoryId": "sticker",
                    "extData": {
                        "id": stickerId,
                        "packageId": stickerPackageId,
                        "packageVersion": 1,
                        "hasAnimation": True,  # TODO: check it
                        "hasSound": True,  # TODO: check it
                        "stickerResourceType": "ANIMATION",  # TODO: check it
                    },
                }
            )
        if mediaObjectId is not None:
            contentsList.append(
                {
                    "categoryId": "media",
                    "extData": {
                        "objectId": mediaObjectId,
                        "type": mediaObjectType,
                        "width": 999999999999999,
                        "height": 999999999999999,
                        "size": -1,
                        "obsNamespace": mediaObjectFrom,
                        "serviceName": "myhome",
                    },
                }
            )
        data = {
            "contentId": contentId,
            "commentText": text,
            # "secret": False,  # WTF THIS?
            "contentsList": contentsList,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/comment/create.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def deleteComment(self, mid: str, commentId: str):
        params = {"homeId": mid, "commentId": commentId}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/comment/delete.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listComment(self, mid: str, contentId: str, scrollId: str = None):
        params = {
            "homeId": mid,
            # 'actorId': actorId,
            "contentId": contentId,
            # 'limit': 10
        }
        if scrollId is not None:
            params["scrollId"] = scrollId
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
                "x-lpv": "1",
                "x-lsr": "TW",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/comment/getList.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def createLike(
        self,
        mid: str,
        contentId: str,
        likeType: str = "1003",
        sharable: bool = False,
        sourceType: str = "TIMELINE",
    ):
        params = {"sourceType": sourceType}
        data = {
            "contentId": contentId,
            "actorId": mid,
            "likeType": likeType,
            "sharable": sharable,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/like/create.json", params
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def cancelLike(self, contentId: str, sourceType: str = "TIMELINE"):
        params = {"contentId": contentId, "sourceType": sourceType}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v41/like/cancel.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listLike(
        self,
        mid: str,
        contentId: str,
        scrollId: str = None,
        includes: list = None,
        filterType: str = None,
    ):
        if includes is None:
            includes = ["ALL", "GROUPED", "STATS"]
        params = {"homeId": mid, "contentId": contentId, "includes": ",".join(includes)}
        if scrollId is not None:
            params["scrollId"] = scrollId
        if filterType is not None:
            params["filterType"] = filterType  # eg. 1003 for GROUPED
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "Content-type": "application/json",
                "x-lpv": "1",
                "x-lsr": "TW",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v41/like/getList.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def searchNote(self, mid, text):
        data = {
            "query": text,
            "queryType": "TEXT",
            "homeId": mid,
            "postLimit": 20,
            "commandId": 16,
            "channelId": "1341209850",
            "commandType": 188259,
        }
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v46/search/note.json", {}
        )
        r = self.server.postContent(
            url, headers=self.server.timelineHeaders, data=json.dumps(data)
        )
        res = r.json()
        return res["result"]["feeds"]

    @loggedIn
    def sendPostToTalk(self, postId: str, receiveMids: list):
        data = {"postId": postId, "receiveMids": receiveMids}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/post/sendPostToTalk.json", {}
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagPosts(self, query, homeId=None, scrollId=None, range=None):
        if range is None:
            range = ["GROUP"]
        # range: GROUP or unset
        data = {"query": query, "homeId": homeId, "scrollId": scrollId, "range": range}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v52/hashtag/posts.json", {}
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
                "x-lal": self.LINE_LANGUAGE,
            },
        )
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagSuggest(self, query):
        data = {"query": query}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v52/hashtag/suggest.json", {}
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
                "x-lal": self.LINE_LANGUAGE,
            },
        )
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagPopular(self, homeId, limit=20):
        data = {"homeId": homeId, "limit": limit}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v52/hashtag/popular.json", {}
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
                "x-lal": self.LINE_LANGUAGE,
            },
        )
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getTimelineUrl(self, homeId):
        data = {"homeId": homeId}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/mh/api/v55/web/getUrl.json", data
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lal": self.LINE_LANGUAGE}
        )
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getPostShareLink(self, postId):
        data = {"postId": postId}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/api/v57/post/getShareLink.json", data
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lal": self.LINE_LANGUAGE}
        )
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getDiscoverRecommendFeeds(self, sourcePostId, contents=None):
        if contents is None:
            contents = ["CP", "PI", "PV", "PL", "AD"]
        data = {"sourcePostId": sourcePostId, "contents": contents}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/tl/discover/api/v1/recommendFeeds", {}
        )
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders, {"x-lal": self.LINE_LANGUAGE}
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ ALBUM """

    @loggedIn
    def changeGroupAlbumName(self, mid, albumId, name):
        data = json.dumps({"title": name})
        params = {"homeId": mid}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "PUT",
                "Content-type": "application/json",
                "x-lpv": "1",  # needless
                "x-lsr": "TW",  # needless
                "x-u": "",  # needless
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/album/%s" % albumId, params
        )
        r = self.server.postContent(url, data=data, headers=hr)
        # r.json()['code'] == 0: success
        return r.json()

    @loggedIn
    def deleteGroupAlbum(self, mid, albumId):
        params = {"homeId": mid}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "DELETE",
                "Content-type": "application/json",
                "x-lpv": "1",  # needless
                "x-lsr": "TW",  # needless
                "x-u": "",  # needless
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v4/album/%s" % albumId, params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def addImageToAlbum(self, mid: str, albumId: str, oid: any):
        """
        Add an image to the album

        oid is a string, you can use list for multiple oids
        """
        oids = []
        if type(oid) is str:
            oid = [oid]
        if type(oid) is list:
            for _oid in oid:
                oids.append({"oid": _oid})
        else:
            raise ValueError(f"Not support oid: {oid}")
        params = {"homeId": mid}
        data = json.dumps({"photos": oids})

        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "PUT",
                "content-type": "application/json",
                # change it if you want update many images
                "x-album-stats": "e2FsYnVtUGhvdG9BZGRDb3VudD0xfQ==",
            },
        )

        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/photos/%s" % albumId, params
        )
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    @loggedIn
    def getAlbumImages(self, mid, albumId):
        params = {"homeId": mid}

        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "content-type": "application/json",
            },
        )

        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/photos/%s" % albumId, params
        )
        r = self.server.postContent(url, headers=hr)

        return r.json()

    @loggedIn
    def deleteAlbumImages(self, mid: str, albumId: str, id: any):
        """
        Delete an image on the album

        id is a string, you can use list for multiple ids
        * id is photo id, not objId
        """
        ids = []
        if type(id) is str:
            id = [id]
        if type(id) is list:
            for _id in id:
                ids.append({"id": _id})
        else:
            raise ValueError(f"Not support id: {id}")
        params = {"homeId": mid}
        data = json.dumps({"photos": ids})

        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )

        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "ext/album/api/v3/photos/delete/%s" % albumId, params
        )
        r = self.server.postContent(url, data=data, headers=hr)
        # {"code":0,"message":"success","result":true}
        return r.json()

    @loggedIn
    def getAlbums(self, homeId):
        params = {"homeId": homeId}
        data = {}

        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )

        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/albums", params
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getAlbumUsers(self, mid, albumId):
        params = {"homeId": mid}
        data = {}

        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )

        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/users/%s" % albumId, params
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def createGroupAlbum(self, mid, name):
        data = json.dumps({"title": name, "type": "image"})
        params = {"homeId": mid, "count": "1", "auto": "1"}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/album/api/v3/album", params
        )
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        if r.status_code != 201:
            print(r.text)
        return r.json()

    """ STORY """

    @loggedIn
    def createStoryContent(
        self, oid: str, ohash: str, oType: str = "IMAGE", shareType: str = "PUBLIC"
    ):
        """
        Create story content.

        - shareType:
            PUBLIC,
            FRIEND,
            GROUP,
            FOLLOW_GROUP;

        """
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        medias = [StoryMedia(oid, ohash, oType)]
        data = self.story.CreateStoryContent(
            **{
                "sourceType": "USER",
                "contentType": "USER",
                "medias": medias,
                "shareType": shareType,
            }
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content/create")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def deleteStoryContent(self, contentId: str):
        """Delete story content."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.DeleteStoryContent(**{"contentId": contentId})
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content/delete")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getStoryList(self, userMids: list):
        """Get story list by mids."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.GetStoryList(**{"userMid": self.mid, "userMids": userMids})
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/list")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getStory(self, userMid: str):
        """Get story by mid."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.GetStory(**{"userMid": userMid})
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getStoryContent(self, contentId: str):
        """Get story content."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.GetStoryContent(**{"contentId": contentId})
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def readStoryContent(self, contentId: str):
        """Read story content."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.ReadStoryContent(**{"contentId": contentId, "tsId": ""})
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content/read")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def likeStoryContent(
        self, contentId: str, tsId: str, like: bool, likeType: str = "1001"
    ):
        """Like story content."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.LikeStoryContent(
            **{"contentId": contentId, "tsId": tsId, "like": like, "likeType": likeType}
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content/like")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getStoryContentLikeList(
        self,
        contentId: str,
        include: str = "MERGED",
        likeType: str = "1001",
        size: int = 20,
        scrollId: str = None,
    ):
        """Get story content like list."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        req = {
            "contentId": contentId,
            "include": include,
            "likeType": likeType,  # opt
            "size": size,
        }
        if scrollId is not None:
            req["scrollId"] = scrollId
        data = self.story.StoryContentLikeList(**req)
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/content/like/list")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def sendMessageByStory(
        self, toMid: str, contentId: str, message: str, tsId: str = ""
    ):
        """Send message by story."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        req = {
            "to": {"userMid": toMid, "tsId": tsId},
            "contentId": contentId,
            "message": message,
        }
        data = self.story.SendStoryMessage(**req)
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/message/send")
        )
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    @loggedIn
    def getRecentStoryList(self, lastRequestTime: int, lastTimelineVisitTime: int = 0):
        """Get recent story list."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.GetRecentStoryList(
            **{
                "lastRequestTime": lastRequestTime,
                "lastTimelineVisitTime": lastTimelineVisitTime,
            }
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/recentstory/list")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def getNewStory(self, lastTimelineVisitTime: int = 0):
        """Get new story."""
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        data = self.story.GetNewStory(
            **{"lastTimelineVisitTime": lastTimelineVisitTime}
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, self.story.GetApiPath("story/newstory")
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    @loggedIn
    def fetchNewNotification(self, revision: int = 0):
        params = {"serviceCode": "TL", "revision": revision}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "X-Line-TL-Upstream-ID": "1583881852"},
        )
        data = {}
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/eg/lin/api/v1/notification/fetch/new", params
        )
        r = self.server.postContent(url, json=data, headers=hr)
        return r.json()

    """ Search """

    @loggedIn
    def lnexearch(self, q):
        params = {"q": q}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                # x-line-channeltoken: 1557852768
            },
        )
        url = self.server.urlEncode(self.LINE_SEARCH_DOMAIN, "/lnexearch", params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ Sc """

    def getPageInfo(self, url):
        params = {"url": url, "caller": "TALK", "lang": self.LINE_LANGUAGE}
        hr = self.server.additionalHeaders(
            # self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/sc/api/v2/pageinfo/get.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ One to one """

    @loggedIn
    def syncOtoAccount(self, userMid: str = None):
        """Sync oto accounts."""
        if userMid is None:
            userMid = self.mid
        params = {"userMid": userMid}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/otoaccount/sync.json", params
        )
        r = self.server.postContent(url, headers=hr)
        resp = r.json()
        if userMid == self.mid:
            # update oto accounts cache.
            result = resp.get("result")
            if result is None:
                self.log(f"Can't update oto accounts: {resp}")
            else:
                updated = result.get("updated", [])
                for i in updated:
                    groupId = i.get("groupId")
                    userMid = i.get("userMid")
                    self.otoMids[userMid] = groupId
                self.log(f"Oto accounts updated.", True)
        return resp

    @loggedIn
    def createOtoAccount(self, userMid: str, friendMid: str):
        """Create oto account."""
        params = {"userMid": userMid, "friendMid": friendMid}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "POST", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/ext/note/nt/api/v57/otoaccount/create.json", params
        )
        r = self.server.postContent(url, json=params, headers=hr)
        return r.json()

    """ Keep """

    @loggedIn
    def syncKeep(self, revision=0, limit=30):
        params = {"revision": revision, "limit": limit}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/sync.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def fetchKeep(self, startRevision: int = 0, endRevision: int = 0, limit: int = 30):
        params = {
            "startRevision": startRevision,
            "endRevision": endRevision,
            "limit": limit,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "GET",
                "content-type": "application/json",
                "x-source": "KEEP-PICKER",  # or KEEP-DEFAULT
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/fetch.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def createKeepContent(self):
        raise NotImplementedError("createKeepContent is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/create.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def updateKeepContent(self):
        raise NotImplementedError("updateKeepContent is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/update.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def deleteKeepContent(self):
        raise NotImplementedError("deleteKeepContent is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/delete.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getKeepSize(self, revision: int = 0, limit: int = 30):
        params = {"revision": revision, "limit": limit}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/size.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def initKeepStatus(self):
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/init.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def deleteKeepObs(self):
        raise NotImplementedError("deleteKeepObs is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/obs/delete.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getKeep(self):
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/get.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def deleteKeepMessage(self):
        raise NotImplementedError("deleteKeepMessage is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/message/delete.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def pinKeepContents(self):
        raise NotImplementedError("pinKeepContents is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/contents/pin.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def unpinKeepContents(self):
        raise NotImplementedError("UnpinKeepContents is not implemented")
        params = {}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {"x-lhm": "GET", "content-type": "application/json"},
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN, "/kp/api/v27/keep/contents/unpin.json", params
        )
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ GroupCall YotTube """

    @loggedIn
    def getYouTubeVideos(self, videoIds: list):
        params = {}
        data = {
            "id": ",".join(videoIds),
            "part": "snippet,contentDetails,id,liveStreamingDetails,status,statistics",
            "fields": "items(snippet(publishedAt,title,thumbnails(default,high,medium),channelTitle,"
            "liveBroadcastContent),contentDetails(duration,contentRating),id,liveStreamingDetails("
            "concurrentViewers,scheduledStartTime),status(embeddable),statistics(viewCount, commentCount)) ",
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "content-type": "application/json",
                "x-voip-service-id": "gc",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN + self.LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT,
            "/api/videos",
            params,
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getYouTubeVideosWithQuery(self, query="bao", pageToken=None):
        params = {}
        data = {
            "q": query,
            "part": "id",
            "fields": "nextPageToken,items(id/videoId)",
            "safeSearch": "strict",
            "order": "relevance",
            "maxResults": 50,
            "type": "video",
        }
        if pageToken is not None:
            data["pageToken"] = pageToken
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "content-type": "application/json",
                "x-voip-service-id": "gc",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN + self.LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT,
            "/api/search",
            params,
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getYouTubeVideosWithPopular(self, pageToken=None):
        params = {}
        data = {
            "chart": "mostPopular",
            "part": "snippet,contentDetails,id,liveStreamingDetails,status,statistics",
            "fields": "items(snippet(publishedAt,title,thumbnails(default,high,medium),channelTitle,liveBroadcastContent),contentDetails(duration,contentRating),id,liveStreamingDetails(concurrentViewers,scheduledStartTime),status(embeddable),statistics(viewCount))",
            "regionCode": "TW",
            "maxResults": 50,
        }
        if pageToken is not None:
            data["pageToken"] = pageToken
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "content-type": "application/json",
                "x-voip-service-id": "gc",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN + self.LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT,
            "/api/videos",
            params,
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getYouTubeVideosWithPlaylists(self, ids, pageToken=None):
        params = {}
        data = {
            "id": ",".join(ids),
            "part": "id,contentDetails, snippet",
            "fields": "items(contentDetails,id,snippet)",
            "regionCode": "TW",
            "maxResults": 50,
        }
        if pageToken is not None:
            data["pageToken"] = pageToken
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "content-type": "application/json",
                "x-voip-service-id": "gc",
            },
        )
        url = self.server.urlEncode(
            self.LINE_HOST_DOMAIN + self.LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT,
            "/api/playlists",
            params,
        )
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ Share List Service """

    @loggedIn
    def createShareList(self, ownerMid: str, members: list):
        data = {
            "ownerMid": ownerMid,
            "name": "????",
            "members": members,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/ext/timeline/tlgw/sl/api/v2/sharelist/create"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ BDB """

    @loggedIn
    def incrBDBCelebrate(self, boardId: str, incrCnt: int = 1):
        data = {
            "boardId": boardId,
            "from": "POST",
            "incrCnt": incrCnt,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/celebrate/incr"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def cancelBDBCelebrate(self, boardId: str):
        data = {
            "boardId": boardId,
            "from": "POST",
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/celebrate/cancel"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getBDBBoard(self, boardId: str):
        data = {
            "boardId": boardId,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/board/get"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def likeBDBCard(self, boardId: str, cardId: str):
        data = {
            "boardId": boardId,
            "cardId": cardId,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/card/like/create"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def unlikeBDBCard(self, boardId: str, cardId: str):
        data = {
            "boardId": boardId,
            "cardId": cardId,
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/card/like/cancel"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def createBDBCard(
        self, boardId: str, celebratorMid: str, text: str, cardStatus: str = "NORMAL"
    ):
        data = {
            "boardId": boardId,
            "cardStatus": cardStatus,  # NORMAL or HIDDEN
            "celebratorMid": celebratorMid,  # self mid, but why? 🤔
            "text": text,
            "from": "BOARD",
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/tl/api/v1/bdb/card/create"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ Avatar Service """

    @loggedIn
    def shareAvatarToTalkById(self, avatar_id: str, toMids: list):
        data = {"avatar_id": avatar_id, "to": toMids}
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
                # 'X-Line-Clientid': ''
            },
        )
        url = self.LINE_HOST_DOMAIN + "/ex/ya/am/v1/share"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ Translate Service """

    @loggedIn
    def translate(self, originalText: str, sLang: str = "auto", tLang: str = "tw"):
        data = {
            "originalText": originalText,
            "sLang": sLang,
            "tLang": tLang,
            "xMode": 0,
            "id": str(uuid.uuid1()),
            "service": "talk",
        }
        hr = self.server.additionalHeaders(
            self.server.timelineHeaders,
            {
                "x-lhm": "POST",
                "Content-type": "application/json",
                "x-client-channel": "chat_context",
                "X-Line-Translate-From": "line_android",
            },
        )
        url = self.LINE_HOST_DOMAIN + "/ds/translate/legyTransAPI.nhn"
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()
