# -*- coding: utf-8 -*-

class ChannelService(object):

    def __init__(self):
        pass
        
    def issueChannelToken(self, channelId="1341209950"):
        #sqrd = self.DummyProtocol("issueChannelToken", 3, {
        #    1: (11, channelId)
        #}).read()
        sqrd = [128, 1, 0, 1] + self.getStringBytes('issueChannelToken') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(channelId)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT ,sqrd)
        
    def approveChannelAndIssueChannelToken(self, channelId="1341209950"):
        sqrd = [128, 1, 0, 1] + self.getStringBytes('approveChannelAndIssueChannelToken') + [0, 0, 0, 0]
        sqrd += [11, 0, 1] + self.getStringBytes(channelId)
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT ,sqrd)
        
    def getChannelInfo(self, channelId):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 14, 103, 101, 116, 67, 104, 97, 110, 110, 101, 108, 73, 110, 102, 111, 0, 0, 0, 0, 11, 0, 2, 0, 0, 0, len(channelId)]
        for value in str(channelId):
            sqrd.append(ord(value))
        sqrd += [0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT ,sqrd)
        
    def getCommonDomains(self, lastSynced=0):
        sqrd = [128, 1, 0, 1, 0, 0, 0, 16, 103, 101, 116, 67, 111, 109, 109, 111, 110, 68, 111, 109, 97, 105, 110, 115, 0, 0, 0, 0, 0]
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT ,sqrd)
        
    def issueRequestTokenWithAuthScheme(self, channelId, otpId, authScheme, returnUrl):
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
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT ,sqrd)
    
    def getReturnUrlWithRequestTokenForAutoLogin(self, url, sessionString=None):
        params = [
            [12, 2, [
                [11, 1, url],
                [11, 2, sessionString]
            ]]
        ]
        sqrd = self.generateDummyProtocol('getReturnUrlWithRequestTokenForAutoLogin', params, 4)
        return self.postPackDataAndGetUnpackRespData(self.LINE_CHANNEL_ENDPOINT_V4 ,sqrd, 4)