# -*- coding: utf-8 -*-
import re

class Config(object):
    LINE_HOST_DOMAIN                     = 'https://ga2.line.naver.jp'
    LINE_LEGY_HOST_DOMAIN                = 'https://legy-jp.line.naver.jp'
    LINE_GW_HOST_DOMAIN                  = 'https://gwz.line.naver.jp'
    LINE_GF_HOST_DOMAIN                  = 'https://gf.line.naver.jp'
    LINE_GD2_HOST_DOMAIN                 = 'https://gd2.line.naver.jp'
    LINE_GD2K_HOST_DOMAIN                = 'https://gd2k.line.naver.jp'
    LINE_GD2S_HOST_DOMAIN                = 'https://gd2s.line.naver.jp'
    LINE_GD2G_HOST_DOMAIN                = 'https://gd2g.line.naver.jp'
    LINE_GD2U_HOST_DOMAIN                = 'https://gd2u.line.naver.jp'
    LINE_GD2V_HOST_DOMAIN                = 'https://gd2v.line.naver.jp'
    LINE_GD2I_HOST_DOMAIN                = 'https://gd2i.line.naver.jp'
    LINE_GD2W_HOST_DOMAIN                = 'https://gd2w.line.naver.jp'

    LINE_OBS_DOMAIN                      = 'https://obs.line-apps.com'

    LINE_OBS_CDN_DOMAIN                  = 'https://obs.line-scdn.net'
    LINE_PROFILE_CDN_DOMAIN              = 'https://profile.line-scdn.net'
    LINE_SHOP_CDN_DOMAIN                 = 'https://shop.line-scdn.net'
    LINE_STICKERSHOP_CDN_DOMAIN          = 'https://stickershop.line-scdn.net'

    LINE_LAN_DOMAIN                      = 'https://lan.line.me'

    LINE_LEGY_BETA_DOMAIN                = 'https://legy-beta.line-apps-beta.com'
    LINE_OBS_BETA_DOMAIN                 = 'https://obs-beta.line-apps.com'
    LINE_OBS_CDN_BETA_DOMAIN             = 'https://cdn-obs-beta.line-apps.com/line'
    LINE_SHOP_DL_BETA_DOMAIN             = 'https://dl.shop.line.beta.naver.jp'
    LINE_STICKERSHOP_DL_BETA_DOMAIN      = 'https://dl.stickershop.line.beta.naver.jp'
    LINE_LAN_BETA_DOMAIN                 = 'https://lan.line-beta.me'
    LINE_NOTICE_CDN_DOMAIN               = 'https://notice.line-beta.me'

    LINE_LEGY_RC_DOMAIN                  = 'https://legy-rc.line-apps-rc.com'
    LINE_OBS_RC_DOMAIN                   = 'https://obs-rc.line-apps.com'
    LINE_OBS_CDN_RC_DOMAIN               = 'https://dl.common.line.naver.jp'

    LINE_NOTICE_DOMAIN                   = 'https://notice.line.me'
    LINE_TV_DOMAIN                       = 'https://tv.line.me'
    LINE_TV2_DOMAIN                      = 'https://www.linetv.tw'
    LINE_STORE_DOMAIN                    = 'https://store.line.me'
    LINE_MELODY_DOMAIN                   = 'https://melody.line.me'
    LINE_POD_GAME_DOMAIN                 = 'https://pod.game.line.me'
    LINE_WEBTOONS_DOMAIN                 = 'https://www.webtoons.com'
    LINE_LINEFRIENDS_STORE_DOMAIN        = 'https://store.linefriends.com'
    LINE_LINEFRIENDS_TW_DOMAIN           = 'https://www.linefriends.com.tw'
    LINE_LINEFRIENDS_JP_DOMAIN           = 'https://www.linefriends.jp'
    LINE_SHOP_DOMAIN                     = 'https://shop.line.me'
    LINE_BUY_DOMAIN                      = 'https://buy.line.me'
    LINE_TODAY_DOMAIN                    = 'https://today.line.me'
    LINE_TRAVEL_DOMAIN                   = 'https://travel.line.me'
    LINE_FACTCHECKER_DOMAIN              = 'https://fact-checker.line.me'
    LINE_MUSIC_DOMAIN                    = 'https://music.line.me'
    LINE_LIVE_DOMAIN                     = 'https://live.line.me'
    LINE_MANGA_DOMAIN                    = 'https://manga.line.me'

    LINE_ENCRYPTION_ENDPOINT             = '/enc'
    LINE_AGE_CHECK_ENDPOINT              = '/ACS4'
    LINE_AUTH_ENDPOINT                   = '/RS3'
    LINE_AUTH_ENDPOINT_V4                = '/RS4'
    LINE_AUTH_EAP_ENDPOINT               = '/ACCT/authfactor/eap/v1'
    LINE_BEACON_ENDPOINT                 = '/BEACON4'
    LINE_BUDDY_ENDPOINT                  = '/BUDDY3'
    LINE_CALL_ENDPOINT                   = '/V3'
    LINE_CANCEL_LONGPOLLING_ENDPOINT     = '/CP4'
    LINE_CHANNEL_ENDPOINT                = '/CH3'
    LINE_CHANNEL_ENDPOINT_V4             = '/CH4'
    LINE_PERSONAL_ENDPOINT_V4             = '/PS4'
    LINE_CHAT_APP_ENDPOINT               = '/CAPP1'
    LINE_COIN_ENDPOINT                   = '/COIN4'
    LINE_COMPACT_E2EE_MESSAGE_ENDPOINT   = '/ECA5'
    LINE_COMPACT_MESSAGE_ENDPOINT        = '/C5'
    LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT  = '/CA5'
    LINE_CONN_INFO_ENDPOINT              = '/R2'
    LINE_EXTERNAL_INTERLOCK_ENDPOINT     = '/EIS4'
    LINE_IOT_ENDPOINT                    = '/IOT1'
    LINE_LIFF_ENDPOINT                   = '/LIFF1'
    LINE_NORMAL_ENDPOINT                 = '/S3'
    LINE_SECONDARY_QR_LOGIN_ENDPOINT     = '/acct/lgn/sq/v1'
    LINE_SHOP_ENDPOINT                   = '/SHOP3'
    LINE_SHOP_AUTH_ENDPOINT              = '/SHOPA'
    LINE_SNS_ADAPTER_ENDPOINT            = '/SA4'
    LINE_SNS_ADAPTER_REGISTRATION_ENDPOINT  = '/api/v4p/sa'
    LINE_SQUARE_ENDPOINT                 = '/SQ1'
    LINE_SQUARE_BOT_ENDPOINT             = '/BP1'
    LINE_UNIFIED_SHOP_ENDPOINT           = '/TSHOP4'
    LINE_WALLET_ENDPOINT                 = '/WALLET4'
    LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT = "/acct/lgn/secpwless/v1"
    LINE_SECONDARY_PWLESS_LOGIN_PERMIT_ENDPOINT = "/acct/lp/lgn/secpwless/v1"
    LINE_SECONDARY_AUTH_FACTOR_PIN_CODE_ENDPOINT = "/acct/authfactor/second/pincode/v1"
    LINE_PWLESS_CREDENTIAL_MANAGEMENT_ENDPOINT = "/acct/authfactor/pwless/manage/v1"
    LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT = "/ACCT/authfactor/pwless/v1"
    LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT = "/EXT/groupcall/youtube-api"
    LINE_E2EE_KEY_BACKUP_ENDPOINT = "/EKBS4"
    SECONDARY_DEVICE_LOGIN_VERIFY_PIN_WITH_E2EE = "/LF1"
    SECONDARY_DEVICE_LOGIN_VERIFY_PIN = "/Q"
    LINE_NOTIFY_SLEEP_ENDPOINT  = "/F4"

    LINE_LAN_ANDROID_URL                 = 'https://lan.line.me/v1/line/android/notification'
    LINE_LAN_IOS_URL                     = 'https://lan.line.me/v1/line/ios/notification'
    LINE_MUSIC_WEBAPP_URL                = 'https://music.line.me/webapp'
    LINE_AMP_LOG_URL                     = 'https://log1-amp.line-apps.com/log'
    LINE_SECONDYARY_REGISTER_API_URL     = 'https://w.line.me/lrs/r'

    LINE_LANGUAGE = 'zh-Hant_TW'
    LINE_SERVICE_REGION = 'TW'

    APP_TYPE    = "CHROMEOS"
    APP_VER     = '11.19.2'
    SYSTEM_NAME = 'DeachSword'
    SYSTEM_VER  = '12.1.4'
    IP_ADDR     = '8.8.8.8'
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    CONSENT_CHANNEL_ID_REGEX = re.compile(r"<input type=\"hidden\" name=\"channelId\" value=\"([^\"]+)\"")
    CONSENT_CSRF_TOKEN_REGEX = re.compile(r"<input type=\"hidden\" name=\"__csrf\" id=\"__csrf\" value=\"([^\"]+)\"")
    
    LOGIN_V2_SUPPORT = ["DESKTOPWIN"] # only desktop_win?
    SYNC_SUPPORT = ["IOS", "IOSIPAD"]

    def __init__(self, type="CHROME"):
        self.DEVICE_TYPE = type
        self.isSecondary = False
        if type == "DESKTOPWIN":
            self.APP_VER = "7.7.0.2698"
            self.SYSTEM_NAME = "WINDOWS"
            self.SYSTEM_VER  = '10.0.0-NT-x64'
        elif type == "DESKTOPMAC":
            self.APP_VER = "7.7.0.2698"
            self.SYSTEM_NAME = "MAC"
        elif type == "CHROMEOS":
            self.APP_VER = "2.5.1"
            self.SYSTEM_NAME = "Chrome OS"
            self.SYSTEM_VER  = '1'
        # elif type == "ANDROIDLITE":
            # self.APP_VER = "2.17.1"
            # self.SYSTEM_NAME = "Android OS"
            # self.isSecondary = True
        elif type in ["ANDROID", "ANDROIDSECONDARY"]:
            self.APP_VER = "12.6.1"
            self.SYSTEM_NAME = "Android OS"
        elif type == "IOS":
            self.APP_VER = "12.4.0"
            self.SYSTEM_NAME = "iOS"
        elif type == "IOSIPAD":
            self.APP_VER = "11.19.2"
            self.SYSTEM_NAME = "iOS"
        elif type == "WATCHOS":
            self.APP_VER = "11.19.2"
            self.SYSTEM_NAME = "Watch OS"
        elif type == "WEAROS":
            self.APP_VER = "11.19.2"
            self.SYSTEM_NAME = "Wear OS"
        elif type == "OPENCHAT_PLUS":
            pass
        elif type == "CHANNELGW":
            pass
        elif type == "CHANNELCP":
            pass
        elif type == "CLOVAFRIENDS":
            pass
        elif type == "BOT":
            pass
        elif type == "WAP":
            pass
        elif type == "WEB":
            pass
        elif type == "BIZWEB":
            pass
        elif type == "DUMMYPRIMARY":
            pass
        elif type == "SQUARE":
            pass
        elif type == "FIREFOXOS":
            pass
        elif type == "TIZEN":
            pass
        elif type == "VIRTUAL":
            pass
        elif type == "CHRONO":
            pass
        elif type == "WINMETRO":
            pass
        elif type == "S40":
            pass
        elif type == "WINPHONE":
            pass
        elif type == "BLACKBERRY":
            pass
        elif type == "INTERNAL":
            pass
        else:
            raise Exception(f"未知的Device , 請至 config.py 新增")
        self.APP_TYPE = type
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
        if self.isSecondary:
            self.APP_NAME += ';SECONDARY'
