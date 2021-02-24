# -*- coding: utf-8 -*-
import time
import json

class ChannelService(object):

    def __init__(self):
        pass
        
    def issueChannelToken(self, channelId="1341209950"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 17, 105, 115, 115, 117, 101, 67, 104, 97, 110, 110, 101, 108, 84, 111, 107, 101, 110, 0, 0, 0, 0, 11, 0, 1, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['issueChannelToken']
        
    def approveChannelAndIssueChannelToken(self, channelId="1341209950"):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1] + self.getStringBytes('approveChannelAndIssueChannelToken') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(channelId)
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['approveChannelAndIssueChannelToken']
        
    def getChannelInfo(self, channelId):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 103, 101, 116, 67, 104, 97, 110, 110, 101, 108, 73, 110, 102, 111, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getChannelInfo']
        
    def getCommonDomains(self, lastSynced=0):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 67, 111, 109, 109, 111, 110, 68, 111, 109, 97, 105, 110, 115, 0, 0, 0, 0, 0]
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)['getCommonDomains']
        
    def issueRequestTokenWithAuthScheme(self, channelId, otpId, authScheme, returnUrl):
        _headers = {
            'X-Line-Access': self.authToken, 
            'x-lpqs': "/CH3"
        }
        a = self.encHeaders(_headers)
        sqrd = [128, 1, 0, 1, 0, 0, 0, 31, 105, 115, 115, 117, 101, 82, 101, 113, 117, 101, 115, 116, 84, 111, 107, 101, 110, 87, 105, 116, 104, 65, 117, 116, 104, 83, 99, 104, 101, 109, 101, 0, 0, 0, 0]
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
        sqr_rd = a + sqrd
        _data = bytes(sqr_rd)
        data = self.encData(_data)
        res = self.server.postContent(self.url, data=data, headers=self.server.Headers)
        data = self.decData(res.content)
        return self.tryReadData(data)
        