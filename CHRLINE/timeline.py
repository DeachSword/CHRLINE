# -*- coding: utf-8 -*-

import json, time, base64

class Timeline():


    """ TIMELINE """
    
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

    def sendContactV2(self, homeId, targetMids):
        url = 'https://ga2.line.naver.jp/hm/api/v1/home/profile/share'
        data = {"homeId":homeId,"shareType":"FLEX_OA_HOME_PROFILE_SHARING","targetMids":targetMids}
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data=json.dumps(data))
        result =  r.json()
        if result['message'] == 'success':
            return  result['result']
        else:
            return False


    """ POST """

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
        url = self.server.urlEncode('https://gwz.line.naver.jp', '/mh/api/v52/post/get.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

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

    """ ALBUM """

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
        

    def getAlbumImages(self, mid, albumId):
        params = {'homeId': mid}
        
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'GET',
            'content-type': "application/json",
        })

        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/photos/%s' % albumId, params)
        r = self.server.postContent(url, headers=hr)
        
        return r.json()    
        
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