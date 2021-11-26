# -*- coding: utf-8 -*-

"""
Author: YinMo (https://github.com/WEDeach)
Project: CHRLINE-side (https://github.com/DeachSword/CHRLINE)
Version: v1.0.2_202111260001 (Free Ver.)
"""

from CHRLINE import *
import requests


def checkFacebookAccess(accessToken: str):
    api_url = f"https://graph.facebook.com/v9.0/me?access_token={accessToken}&fields=id%2Cname%2Cfirst_name%2Cmiddle_name%2Clast_name&format=json&sdk=android"
    data = requests.get(api_url).json()
    if 'id' in data:
        print(f"Your FB account uid: {data['id']}")
        return True
    return False


def issueFacebookOAuthUrl():
    line_dev_id = "106149969545611"
    url = f"https://m.facebook.com/v9.0/dialog/oauth?cct_prefetching=0&client_id={line_dev_id}&cbt=1637864855809&e2e=%7B%22init%22%3A1637864855809%7D&ies=0&sdk=android-9.1.1&sso=chrome_custom_tab&state=%7B%220_auth_logger_id%22%3A%228b1421c6-edeb-4160-a115-fd80d42bf08b%22%2C%223_method%22%3A%22custom_tab%22%2C%227_challenge%22%3A%22rjvvnq8aodeobsqhvd3s%22%7D&default_audience=friends&login_behavior=NATIVE_WITH_FALLBACK&redirect_uri=fb{line_dev_id}%3A%2F%2Fauthorize&auth_type=rerequest&response_type=token%2Csigned_request%2Cgraph_domain&return_scopes=true"
    return url


token = input("Your bot primary token or v3 token (login to ANDROID): ")
fb_access_token = input("Your fb access token: ")
if not checkFacebookAccess(fb_access_token):
    print("無效的fb access token...")
    exit()

cl = CHRLINE(token, device="ANDROID")
# cl.disconnectEapAccount(1)  # if u want :>

setting = cl.getSettings()
if 1 in setting[42]:
    print(
        f"your bot has been connected the fb account: {setting[42][1]}, if u want remove it, just use \"cl.disconnectEapAccount(1)\"")
    exit()

udid = ""  # can i use empty?

session = cl.openAAFECSession(udid)[1]
print(f"session: {session}")

# get login url from issueFacebookOAuthUrl() and get the "location" url of resp, u can found "access_token"

verify = cl.verifyEapLogin(session, 1, fb_access_token)[1]
if verify:
    if input(f"This fb account is bound to other LINE accounts.\nDo you want to continue? (y/n)").lower() != "y":
        exit()
print(f"verify: {verify}")
print(f"try to connect fb account...")
connect = cl.connectEapAccount(session)
print(f"connect: {True if connect == {} else False}")
