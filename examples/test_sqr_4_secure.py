# -*- coding: utf-8 -*-
"""
QrCode Login For Secure (LoginV2).
Line version limit: (not-set)
Author: YinMo0913
CreatedTime: 2022/11/16
"""
from CHRLINE import *

cl = CHRLINE(device="DESKTOPMAC", useThrift=True, noLogin=True)

s = cl.checkAndGetValue(cl.createSession(), 1)
print(f'Session: {s}')
qr = cl.createQrCodeForSecure(s)
url = cl.checkAndGetValue(qr, 1)
secureCode = cl.checkAndGetValue(qr, 4)
secret, secretUrl = cl.createSqrSecret()
url = url + secretUrl
print(f'QrCode: {qr}')
imgPath = cl.genQrcodeImageAndPrint(url)
print(f"URL: {url}")
if cl.checkQrCodeVerified(s):
    try:
        cl.verifyCertificate(s, cl.getSqrCert())
    except:
        c = cl.checkAndGetValue(cl.createPinCode(s), 1)
        print(f"請輸入pincode: {c}")
        cl.checkPinCodeVerified(s)
    res = cl.qrCodeLoginV2ForSecure(s, 'DeachSword', cl.SYSTEM_NAME, secureCode)
    pem = cl.checkAndGetValue(res, 1)
    cl.saveSqrCert(pem)
    print("證書: ", pem)
    tokenV3Info = cl.checkAndGetValue(res, 3)
    _mid = cl.checkAndGetValue(res, 4)
    bT = cl.checkAndGetValue(res, 9)
    metadata = cl.checkAndGetValue(res, 10)
    e2eeKeyInfo = cl.decodeE2EEKeyV1(metadata, secret)
    authToken = cl.checkAndGetValue(tokenV3Info, 1)
    refreshToken = cl.checkAndGetValue(tokenV3Info, 2)
    cl.saveCacheData(
        '.refreshToken', authToken, refreshToken)
    print(f"AuthToken: {authToken}")
    print(f"RefreshToken: {refreshToken}")
else:
    raise Exception('can not check qr code, try again?')