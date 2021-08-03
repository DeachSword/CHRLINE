# -*- coding: utf-8 -*-

import json, time, base64

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].can_use_timeline:
            return func(*args, **kwargs)
        else:
            raise Exception("can't use Timeline func")
    return checkLogin

class Timeline():

    def __init__(self):
        TIMELINE_CHANNEL_ID = "1341209950"
        self.can_use_timeline = False
        try:
            if self.APP_TYPE in ["CHROMEOS"]:
                TIMELINE_CHANNEL_ID = "1341209850"
            self.server.timelineHeaders = {
                'x-line-application': self.server.Headers['x-line-application'],
                'User-Agent': self.server.Headers['User-Agent'],
                'X-Line-Mid': self.profile[1],
                'X-Line-Access': self.authToken,
                'X-Line-ChannelToken': self.approveChannelAndIssueChannelToken(TIMELINE_CHANNEL_ID)[5],
                'x-lal': self.LINE_LANGUAGE,
                "X-LAP": "5",
                "X-LPV": "1",
                "X-LSR": self.LINE_SERVICE_REGION,
            }
            self.can_use_timeline = True
        except:
            self.log("can't use Timeline")

    """ TIMELINE """

    @loggedIn
    def getProfileDetail(self, mid, styleMediaVersion='v2', storyVersion='v6'):
        params = {
            'homeId': mid,
            'styleMediaVersion': styleMediaVersion,
            'storyVersion': storyVersion
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'x-line-global-config': "discover.enable=true; follow.enable=true", #why get follow count with this?
        })
        url = self.server.urlEncode('https://ga2.line.naver.jp/hm', '/api/v1/home/profile.json', params)
        r = self.server.postContent(url, headers=hr, data='')
        return r.json()

    @loggedIn
    def getProfileCoverDetail(self, mid):
        params = {
            'homeId': mid
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
        })
        print(hr)
        url = self.server.urlEncode('https://ga2.line.naver.jp/hm', '/api/v1/home/cover.json', params)
        r = self.server.postContent(url, headers=hr, data='')
        return r.json()

    @loggedIn
    def updateProfileCoverById(self, objid, vObjid=None):
        data = {
            "homeId": self.profile[1],
            "coverObjectId": objid,
            "storyShare": True,
            "meta":{} # heh
        }
        if vObjid:
            data['videoCoverObjectId'] = vObjid
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
        })
        r = self.server.postContent('https://ga2.line.naver.jp/hm/api/v1/home/cover.json', headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def updateProfileCoverById2(self, objId: str):
        params = {
            "coverImageId": objId,
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/api/v41/home/updateCover.json', params)
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getOACarousel(self):
        params = {
            "homeId": "ud9b11771afc46b1d9b6faa646ab3c475"
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/api/v42/feed/carousel/oa.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getPartlyBlockContacts(self):
        params = {
            "id": self.mid,
            "limit": 30
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/mapi/v53/contacts/block/partly.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getClosedContacts(self):
        params = {
            "id": self.mid
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/tl/mapi/v41/contacts/block', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getHideContacts(self, MID):
        params = {
            "id": self.mid
        }
        data = {
            "mid": "u67c43239c865dfce6addb41c6b3c0edd"
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/tl/mapi/v41/contacts/hide', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getAutoOpenOption(self):
        params = {
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/tl/mapi/v41/contact/autoopen', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getHideGrouphomeList(self):
        params = {
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/ma/api/v24/grouphome/hide/list.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getNewpostStatus(self):
        params = {
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/mapi/v41/status/newpost', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getGroupProfileimageList(self):
        params = {
        }
        data = {
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/api/v24/group/profileimage/list.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def getUserProfile(self, mid: str):
        params = {
            "userMid": mid
        }
        data = {}
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/ma/api/v1/profile/get.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def getUserPopupDetail(self, mid: str):
        params = {
            "userMid": mid
        }
        data = {}
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/ma/api/v1/userpopup/getDetail.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def syncBuddygroup(self, mid: str):
        params = {
            "userMid": mid,
            "lastUpdated": 0
        }
        data = {}
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/tl/mapi/v41/home/buddygroup/sync', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.text

    @loggedIn
    def sendContactV2(self, homeId, targetMids):
        url = 'https://ga2.line.naver.jp/hm/api/v1/home/profile/share'
        data = {"homeId":homeId,"shareType":"FLEX_OA_HOME_PROFILE_SHARING","targetMids":targetMids}
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data=json.dumps(data))
        result =  r.json()
        if result['message'] == 'success':
            return  result['result']
        else:
            return False

    @loggedIn
    def getTimelintTab(self, postLimit=20, likeLimit=6, commentLimit=10, requestTime=0):
        url = 'https://ga2.line.naver.jp/tl/api/v57/timeline/tab.json'
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
                        "order": "RANKING"
                    },
                    "requestBody": {
                        "discover": {
                            "contents": ["CP", "PI", "PV", "PL", "LL"]
                        }
                    }
                },
                "STORY": {
                    "version": "v6"
                }
            }
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            'x-lsr': 'TW'
        })
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        result =  r.json()
        if result['message'] == 'success':
            return  result['result']
        else:
            return False


    """ POST """

    @loggedIn
    def getPost(self, mid, postId):
        params = {
            'homeId': mid,
            'postId': postId,
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/api/v52/post/list.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listPost(self, mid, postId=None, updatedTime=None):
        params = {
            'homeId': mid
        }
        if postId is not None:
            params['postId'] = postId
        if updatedTime is not None:
            params['updatedTime'] = updatedTime
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v52/post/get.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def createComment(self, mid, contentId, text):
        params = {
            'homeId': mid
        }
        data = {
           "contentId" : contentId,
           "commentText" : text,
           "secret" : False,
           "contentsList" : [
              {
                 "categoryId" : "sticker",
                 "extData" : {
                    "id" : 1,
                    "packageId" : 1,
                    "packageVersion" : 1
                 }
              }
           ],
           "commandId" : 16777257,
           "channelId" : "1341209850",
           "commandType" : 188208
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v52/comment/create.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def deleteComment(self, mid, contentId, commentId):
        params = {
            'homeId': mid,
            'commentId': commentId
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v52/comment/delete.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listComment(self, mid, contentId):
        params = {
            'homeId': mid,
            #'actorId': actorId,
            'contentId': contentId,
            #'limit': 10
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v52/comment/getList.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def createLike(self, mid, contentId, likeType=1003):
        params = {
            'homeId': mid
        }
        data = {
           "contentId" : contentId,
           "likeType" : str(likeType),
           "sharable" : False,
           "commandId" : 16777265,
           "channelId" : "1341209850",
           "commandType" : 188210
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v41/like/create.json', params)
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    @loggedIn
    def cancelLike(self, contentId):
        params = {
            'contentId': contentId,
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v41/like/cancel.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def listLike(self, mid, contentId):
        params = {
            'homeId': mid,
            'contentId': contentId
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'Content-type': "application/json",
            'x-lpv': '1',
            'x-lsr':'TW'
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v41/like/getList.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def searchNote(self, mid, text):
        data = {
           "query" : text,
           "queryType" : "TEXT",
           "homeId" : mid,
           "postLimit" : 20,
           "commandId" : 16,
           "channelId" : "1341209850",
           "commandType" : 188259
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp/mh',
            '/api/v46/search/note.json',
            {}
        )
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data=json.dumps(data))
        res = r.json()
        return res["result"]["feeds"]

    @loggedIn
    def sendPostToTalk(self, postId, receiveMids):
        data = {
            "postId": postId,
            "receiveMids": receiveMids
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/mh/api/v56/post/sendPostToTalk.json',
            {}
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
        })
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagPosts(self, query, homeId=None, scrollId=None, range=["GROUP"]):
        # range: GROUP or unset
        data = {
           "query" : query,
           "homeId" : homeId,
           "scrollId" : scrollId,
           "range" : range
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/mh/api/v52/hashtag/posts.json',
            {}
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagSuggest(self, query):
        data = {
           "query" : query
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/mh/api/v52/hashtag/suggest.json',
            {}
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getHashtagPopular(self, homeId, limit=20):
        data = {
           "homeId" : homeId,
           "limit" : limit
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/mh/api/v52/hashtag/popular.json',
            {}
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            'Content-type': "application/json",
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.postContent(url, headers=hr, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getTimelineUrl(self, homeId):
        data = {
           "homeId" : homeId
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/mh/api/v55/web/getUrl.json',
            data
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getPostShareLink(self, postId):
        data = {
           "postId" : postId
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/api/v55/post/getShareLink.json',
            data
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.getContent(url, headers=hr)
        return r.json()

    @loggedIn
    def getDiscoverRecommendFeeds(self, sourcePostId, contents=["CP", "PI", "PV", "PL", "AD"]):
        data = {
            "sourcePostId": sourcePostId, 
            "contents" : contents
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp',
            '/tl/discover/api/v1/recommendFeeds',
            {}
        )
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            "x-lal": self.LINE_LANGUAGE
        })
        r = self.server.postContent(url, headers=hr, json=data)
        return r.json()

    """ ALBUM """

    @loggedIn
    def changeGroupAlbumName(self, mid, albumId, name):
        data = json.dumps({'title': name})
        params = {'homeId': mid}
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "PUT",
            'Content-type': "application/json",
            'x-lpv': '1', #needless
            'x-lsr':'TW', #needless
            'x-u': '' #needless
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/album/%s' % albumId, params)
        r = self.server.postContent(url, data=data, headers=hr)
        #r.json()['code'] == 0: success
        return r.json()

    @loggedIn
    def deleteGroupAlbum(self, mid, albumId):
        params = {'homeId': mid}
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "DELETE",
            'Content-type': "application/json",
            'x-lpv': '1', #needless
            'x-lsr':'TW', #needless
            'x-u': '' #needless
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v4/album/%s' % albumId, params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def addImageToAlbum(self, mid, albumId, oid):
        #oid like 6cbff2e4100006b58db80f87ad8666bc.20121408
        params = {'homeId': mid}
        data = json.dumps({"photos":[{"oid": oid}]})
        
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'PUT',
            'content-type': "application/json",
            'x-album-stats': "e2FsYnVtUGhvdG9BZGRDb3VudD0xfQ==" #change it if you want update many images
        })

        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/photos/%s' % albumId, params)
        r = self.server.postContent(url, data=data, headers=hr)
        
        #{"code":0,"message":"success","result":true}
        return r.json()    

    @loggedIn
    def getAlbumImages(self, mid, albumId):
        params = {'homeId': mid}
        
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'GET',
            'content-type': "application/json",
        })

        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/photos/%s' % albumId, params)
        r = self.server.postContent(url, headers=hr)
        
        return r.json()    

    @loggedIn
    def deleteAlbumImages(self, mid, albumId, id):
        #id 4620693219800810323, not oid
        params = {'homeId': mid}
        data = json.dumps({"photos":[{"id": id}]})
            
        
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'POST',
            'content-type': "application/json"
        })

        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/photos/delete/%s' % albumId, params)
        r = self.server.postContent(url, data=data, headers=hr)
        #{"code":0,"message":"success","result":true}
        return r.json()
        
        
        return res["result"]["feeds"]


    """ STORY """

    @loggedIn
    def uploadStoryObject(self, mid, albumId, name):
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-obs-params': 'eyJuYW1lIjoidGltZWxpbmVfMjAyMTAyMjZfMDQzODExLmpwZyIsIm9pZCI6IjgzNTY2YWVmM2ZhNWRhMjllMGNkNGJkMzFiM2QzM2IxdGZmZmZmZmZmIiwicmFuZ2UiOiJieXRlcyAwLTIxNzEwXC8yMTcxMSIsInF1YWxpdHkiOiI3MCIsInR5cGUiOiJpbWFnZSIsInZlciI6IjEuMCJ9'
        })
        url = self.server.urlEncode('https://obs-tw.line-apps.com', '/story/st/upload.nhn')
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    @loggedIn
    def createStoryContent(self, mid, albumId, name):
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'POST',
            'content-type': "application/json"
        })
        data = {"content":{"sourceType":"USER","contentType":"USER","media":[{"oid":"83566aef3fa5da29e0cd4bd31b3d33b122d46025t0d7431a3","service":"story","sid":"st","hash":"0hK6iOniFhFBlUNgJGU9JrTnp0D3c6Tk0NLU5SfXUxTXktUVEYOFQOL3I-HigrU1YcPVJbLHNjSCsqBlBMPVVcfnIyDygsAFZNaABZ","mediaType":"IMAGE"}]},"shareInfo":{"shareType":"FRIEND"}}
        url = self.server.urlEncode('https://ga2.line.naver.jp', '/st/api/v6/story/content/create')
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    @loggedIn
    def getRecentstoryStory(self, lastRequestTime=None):
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'POST',
            'content-type': "application/json"
        })
        url = self.server.urlEncode('https://ga2.line.naver.jp', '/st/api/v6/story/recentstory/list')
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    @loggedIn
    def sendMessageForStoryAuthor(self, userMid, contentId, message):
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'POST',
            'content-type': "application/json"
        })
        data = {
            "to": {
                "userMid": userMid,
                "friendType": "",
                "tsId":""
            },
            "contentId": contentId,
            "message": message}
        url = self.server.urlEncode('https://ga2.line.naver.jp', '/st/api/v6/story/message/send')
        r = self.server.postContent(url, data=data, headers=hr)
        return r.json()

    """ Search """

    @loggedIn
    def lnexearch(self, q):
        params = {
            'q': q
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
            #x-line-channeltoken: 1557852768
        })
        url = self.server.urlEncode('https://search.line.me', '/lnexearch', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ Sc """

    @loggedIn
    def getPageInfo(self, url):
        params = {
            'url': url,
            'caller': 'TALK',
            'lang': self.LINE_LANGUAGE
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'content-type': "application/json"
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/sc/api/v2/pageinfo/get.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ One to one """

    @loggedIn
    def syncOtoAccount(self, userMid):
        params = {
            'userMid': userMid
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'content-type': "application/json"
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/mh/api/v24/otoaccount/sync.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    """ Keep """

    @loggedIn
    def syncKeep(self, revision=0, limit=30):
        params = {
            'revision': revision,
            'limit': limit
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'content-type': "application/json"
        })
        url = self.server.urlEncode(self.LINE_HOST_DOMAIN, '/kp/api/v27/keep/sync.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()