# -*- coding: utf-8 -*- 
from CHRLINE import *

import rsa, binascii


cl = CHRLINE(authToken, device="ANDROID", os_version="8.0.1")

settings = cl.getSettings() # 41 is mail
print(settings)

session = cl.openAuthSession()
print(f"Session: {session}")

rsaInfo = cl.getAuthRSAKey(session)
print(f"Rsa Info: {rsaInfo}")

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

# res = cl.setIdentifier(session, keynm, crypto)
res = cl.updateIdentifier(session, keynm, crypto)
print(res)
responseType = res[2]
confirmationVerifier = res[3]

pincode = input('Pincode: ')
res = cl.confirmIdentifier(session, pincode)
print(res)