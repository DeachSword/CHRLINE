# -*- coding: utf-8 -*-

class SettingsService(object):
    
    def __init__(self):
        pass
    
    def getSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('getSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def contextAgnosticGetSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('contextAgnosticGetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def setSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('setSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def setSettingWithScope(self):
        params = []
        sqrd = self.generateDummyProtocol('setSettingWithScope', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def resetSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('resetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def resetSettingWithScope(self):
        params = []
        sqrd = self.generateDummyProtocol('resetSettingWithScope', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def searchSettings(self):
        params = []
        sqrd = self.generateDummyProtocol('searchSettings', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)

    def contextAgnosticSearchSettings(self):
        params = []
        sqrd = self.generateDummyProtocol('contextAgnosticSearchSettings', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4" ,sqrd, 4)