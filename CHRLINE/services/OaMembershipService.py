# -*- coding: utf-8 -*-

class OaMembershipService(object):
    OaMembershipService_REQ_TYPE = 4
    OaMembershipService_RES_TYPE = 4
    OaMembershipService_API_PATH = "/EXT/bot/oafan"

    def __init__(self):
        pass

    def activateSubscription(self, uniqueKey: str, activeStatus: str = 1):
        """
        - activeStatus:
            INACTIVE(0),
            ACTIVE(1);
        """
        params = [
            [12, 1, [
                [11, 1, uniqueKey],
                [8, 2, activeStatus]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'activateSubscription', params, self.OaMembershipService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.OaMembershipService_API_PATH, sqrd, self.OaMembershipService_RES_TYPE)

    def activateMembership(self, uniqueKey: str, activeStatus: str = 1):
        """
        - activeStatus:
            INACTIVE(0),
            ACTIVE(1);
        """
        params = [
            [12, 1, [
                [11, 1, uniqueKey],
                [8, 2, activeStatus]
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'activateMembership', params, self.OaMembershipService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.OaMembershipService_API_PATH, sqrd, self.OaMembershipService_RES_TYPE)

    def getJoinedMembership(self, uniqueKey: str):
        params = [
            [12, 1, [
                [11, 1, uniqueKey],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getJoinedMembership', params, self.OaMembershipService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.OaMembershipService_API_PATH, sqrd, self.OaMembershipService_RES_TYPE)

    def getJoinedMemberships(self):
        params = []
        sqrd = self.generateDummyProtocol(
            'getJoinedMemberships', params, self.OaMembershipService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.OaMembershipService_API_PATH, sqrd, self.OaMembershipService_RES_TYPE)

    def getOrderInfo(self, uniqueKey: str):
        params = [
            [12, 1, [
                [11, 1, uniqueKey],
            ]]
        ]
        sqrd = self.generateDummyProtocol(
            'getOrderInfo', params, self.OaMembershipService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.OaMembershipService_API_PATH, sqrd, self.OaMembershipService_RES_TYPE)
