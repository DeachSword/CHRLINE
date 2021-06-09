# -*- coding: utf-8 -*- 

#######################################
# Author: YinMo
# Source: https://github.com/DeachSword/CHRLINE/blob/master/examples/test_set_mail.py
# Version: 1.0.1
#######################################

from CHRLINE import *

import rsa, binascii

cl = CHRLINE(token, device="ANDROID", os_version="8.0.1")

settings = cl.getSettings() # 41 is mail
currEmail = settings.get(41)

session = cl.openAuthSession()
print(f"Session: {session}")

rsaInfo = cl.getAuthRSAKey(session)
# print(f"Rsa Info: {rsaInfo}")

keynm = rsaInfo[1]
nvalue = rsaInfo[2]
evalue = rsaInfo[3]
sessionKey = rsaInfo[4]

email = input('Email: ')
pw = ''
message = (chr(len(sessionKey)) + sessionKey +
           chr(len(email)) + email + 
           chr(len(pw)) + pw).encode('utf-8')
pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()

if currEmail is None:
    res = cl.setIdentifier(session, keynm, crypto)
else:
    res = cl.updateIdentifier(session, keynm, crypto)
print(res)
responseType = res[2]
confirmationVerifier = res[3]

pincode = input('Pincode: ')
res = cl.confirmIdentifier(session, pincode)
responseType = res.get(2)

if responseType == 1:
    print('SUCCESS!')
else:
    print(f'Expected got 1, but received {responseType}')