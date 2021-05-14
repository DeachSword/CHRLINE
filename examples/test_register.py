from CHRLINE import *
import os, hashlib, hmac, base64, time
import axolotl_curve25519 as Curve25519
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def getSHA256Sum(*args):
    instance = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            arg = arg.encode()
        instance.update(arg)
    return instance.digest()

def get_issued_at() -> bytes:
    return base64.b64encode(
        f"iat: {int(time.time()) * 60}\n".encode("utf-8")) + b"."

def get_digest(key: bytes, iat: bytes) -> bytes:
    return base64.b64encode(hmac.new(key, iat, hashlib.sha1).digest())

def create_token(auth_key: str) -> str:
    mid, key = auth_key.partition(":")[::2]
    key = base64.b64decode(key.encode("utf-8"))
    iat = get_issued_at()

    digest = get_digest(key, iat).decode("utf-8")
    iat = iat.decode("utf-8")

    return mid + ":" + iat + "." + digest


UPDATE_NAME = True
DISPLAY_NAME = "yinmo"



cl = CHRLINE(noLogin=True)
session = cl.openPrimarySession()

private_key = Curve25519.generatePrivateKey(os.urandom(32))
public_key = Curve25519.generatePublicKey(private_key)
nonce = os.urandom(16)

b64_private_key = base64.b64encode(private_key)
b64_public_key = base64.b64encode(public_key)
b64_nonce = base64.b64encode(nonce)
print(f"private_key: {b64_private_key}")
print(f"public_key: {b64_public_key}")
print(f"nonce: {b64_nonce}")

print(f"[SESSION] {session}")
info = cl.getCountryInfo(session)
phone = input('input your phone number: ')
region = input('input phone number region: ')
phone2 = cl.getPhoneVerifMethod(session, phone, region)[3] # 1 is availableMethods

sendPin = cl.sendPinCodeForPhone(session, phone, region)
print(f"[SEND PIN CODE] {sendPin}")

pin = input('Enter Pin code: ')
verify = cl.verifyPhone(session, phone, region, pin)
print(f"[VERIFY PIN CODE] {verify}")
if 'error' in verify:
    if verify['error']['code'] == 5:
        print(f"[HUMAN_VERIFICATION_REQUIRED]")
        hv = HumanVerif(verify['error']['metadata'][11][1], verify['error']['metadata'][11][2])
        RetryReq(session, hv)

cl.validateProfile(session, 'yinmo')

exchangeEncryptionKey = cl.exchangeEncryptionKey(session, b64_public_key.decode(), b64_nonce.decode(), 1)
print(f'exchangeEncryptionKey: {exchangeEncryptionKey}')

exc_key = base64.b64decode(exchangeEncryptionKey[1])
exc_nonce = base64.b64decode(exchangeEncryptionKey[2])

sign = Curve25519.calculateAgreement(private_key, exc_key)
print(f"sign: {sign}")

password = 'test2021Chrline'

master_key = getSHA256Sum(b'master_key', sign, nonce, exc_nonce)
aes_key = getSHA256Sum(b'aes_key', master_key)
hmac_key = getSHA256Sum(b'hmac_key', master_key)

e1 = AES.new(aes_key[:16], AES.MODE_CBC, aes_key[16:32])
doFinal = e1.encrypt(pad(password.encode(), 16))
hmacd = hmac.new(
    hmac_key,
    msg=doFinal,
    digestmod=hashlib.sha256
).digest()
encPwd = base64.b64encode(doFinal + hmacd).decode()

setPwd = cl.setPassword(session, encPwd, 1)
print(setPwd)


register = cl.registerPrimaryUsingPhone(session)
print(f"[REGISTER] {register}")

authKey = register[1] #authKey, using create_token(the key)
authToken = create_token(authKey) #authToken for login

print(f"authKey: {authKey}")
print(f"authToken: {authToken}")


if UPDATE_NAME:
    cl = CHRLINE(authToken) #login
    cl.updateProfileAttribute(2, DISPLAY_NAME) #update display name

    # update email step:
    # openAuthSession -> getAuthRSAKey and encrypt -> setIdentifier -> confirmIdentifier

