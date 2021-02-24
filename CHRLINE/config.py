# -*- coding: utf-8 -*-
import re

class Config(object):
    LINE_ENC_HOST_DOMAIN        = 'https://gf.line.naver.jp/enc'
    LINE_OBS_DOMAIN             = 'https://obs.line-apps.com'
    
    LINE_LANGUAGE = 'zh-Hant_TW'

    APP_TYPE    = "CHROMEOS"
    APP_VER     = '8.7.0'
    SYSTEM_NAME = 'DeachSword'
    SYSTEM_VER  = '12.1.4'
    IP_ADDR     = '8.8.8.8'
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def __init__(self, type="CHROME"):
        if type == "DESKTOPWIN":
            self.APP_VER = "6.5.2.2431"
            self.SYSTEM_NAME = "WINDOWS"
            self.SYSTEM_VER  = '10.0.0-NT-x64'
        elif type == "DESKTOPMAC":
            self.APP_VER = "5.13.0"
            self.SYSTEM_NAME = "DESKTOPMAC"
        elif type == "CHROMEOS":
            self.APP_VER = "2.4.1"
            self.SYSTEM_NAME = "Chrome_OS"
            self.SYSTEM_VER  = '1'
        elif type == "ANDROIDLITE":
            self.APP_VER = "2.15.0"
            self.SYSTEM_NAME = "Android_OS"
        elif type == "IOSIPAD":
            self.APP_VER = "10.16.2"
            self.SYSTEM_NAME = "iOS"
        elif type == "ANDROID":
            self.APP_VER = "10.16.2"
            self.SYSTEM_NAME = "Android_OS"
        elif type == "IOS":
            self.APP_VER = "12.1.2"
            self.SYSTEM_NAME = "iOS"
        elif type == "WATCHOS":
            self.APP_VER = "10.16.2"
            self.SYSTEM_NAME = "watchOS"
        else:
            raise Exception(f"未知的Device , 請至 config.py 新增")
        self.USER_AGENT = 'Line/%s' % self.APP_VER
    
    def initAppConfig(self, app_type, app_version, os_name, os_version):
        self.APP_TYPE = "CHROMEOS"
        if app_type is not None:
            self.APP_TYPE = app_type
        if app_version is not None:
            self.APP_VER = app_version
        if os_name is not None:
            self.SYSTEM_NAME = os_name
        if os_version is not None:
            self.SYSTEM_VER = os_version
        self.APP_NAME = "%s\t%s\t%s\t%s"%(self.APP_TYPE, self.APP_VER, self.SYSTEM_NAME, self.SYSTEM_VER)
