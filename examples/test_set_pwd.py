# -*- coding: utf-8 -*- 

#######################################
# Author: YinMo
# Source: https://github.com/DeachSword/CHRLINE/blob/master/examples/test_set_pwd.py
# Version: 1.0.0
#######################################

from CHRLINE import *

import rsa, binascii

cl = CHRLINE()  # maybe need primary

settings = cl.getSettings()
currEmail = cl.checkAndGetValue(settings, 'identityIdentifier', 41)
if currEmail is None:
    raise ValueError("Email is None.")

session = cl.openAuthSession()
print(f"Session: {session}")

rsaInfo = cl.getAuthRSAKey(session)

keynm = cl.checkAndGetValue(rsaInfo, 1)
nvalue = cl.checkAndGetValue(rsaInfo, 2)
evalue = cl.checkAndGetValue(rsaInfo, 3)
sessionKey = cl.checkAndGetValue(rsaInfo, 4)

pw = input('Pwd: ')
message = (chr(len(sessionKey)) + sessionKey +
           chr(len(currEmail)) + currEmail + 
           chr(len(pw)) + pw).encode('utf-8')
pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()

cl.updatePassword(session, 1, keynm, crypto)
responseType = cl.checkAndGetValue(res, 2)

if responseType == 1:
    print('SUCCESS!')
else:
    print(f'Expected got 1, but received {responseType}')