# -*- coding: utf-8 -*-

class SettingsService(object):

    def __init__(self):
        pass

    def getSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('getSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def contextAgnosticGetSetting(self):
        params = []
        sqrd = self.generateDummyProtocol(
            'contextAgnosticGetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def setSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('setSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def setSettingWithScope(self):
        params = []
        sqrd = self.generateDummyProtocol('setSettingWithScope', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def resetSetting(self):
        params = []
        sqrd = self.generateDummyProtocol('resetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def resetSettingWithScope(self):
        params = []
        sqrd = self.generateDummyProtocol('resetSettingWithScope', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def searchSettings(self):
        params = []
        sqrd = self.generateDummyProtocol('searchSettings', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def contextAgnosticSearchSettings(self):
        params = []
        sqrd = self.generateDummyProtocol(
            'contextAgnosticSearchSettings', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def bulkGetSetting(self, settingItems: list = ["sticker.preview"]):
        settings = []
        for i in settingItems:
            settings.append([
                [11, 1, i]
            ])
        params = [
            [12, 2, [
                [14, 1, [12, settings]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('bulkGetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)

    def bulkSetSetting(self, settingItems: list = ["sticker.preview"], TypedValueItems: list = []):
        """
        - TypedValue:
            ("booleanValue", 2, 1);
            ("i64Value", 10, 2);
            ("stringValue", 11, 3);
            ("stringListValue", 15, 4);
            ("i64ListValue", 15, 5);
            ("rawJsonStringValue", 11, 6);
            ("i8Value", 3, 7);
            ("i16Value", 6, 8);
            ("i32Value", 8, 9);
            ("doubleValue", 4, 10);
            ("i8ListValue", 15, 11);
            ("i16ListValue", 15, 12);
            ("i32ListValue", 15, 13);

        example:
            self.bulkSetSetting(
                ['hometab.service.pinned'], 
                [
                    [15, 13, [8, [1419, 1072, 10]]] 
                ]
            )

            what is [15, 13, [8, [1419, 1072, 10]]]?
            that is "i32ListValue", so it using 15 and 13
            then u can see "i32List", so values is a list (type: 15)
            so the data should be [15, 13, [8, values]]
        """
        settings = []
        c = 0
        for i in settingItems:
            settings.append([
                [11, 1, i],
                [12, 2, [TypedValueItems[c]]],
                [10, 3, 0],  # clientTimestampMillis
                # [8, 4, 0],  # ns
                # [11, 5, 0],  # transactionId
            ])
            c += 1
        params = [
            [12, 2, [
                [14, 1, [12, settings]]
            ]]
        ]
        sqrd = self.generateDummyProtocol('bulkGetSetting', params, 4)
        return self.postPackDataAndGetUnpackRespData("/US4", sqrd, 4)
