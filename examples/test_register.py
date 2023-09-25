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



cl = CHRLINE(device="ANDROID", noLogin=True)
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
phone = input('input your phone number(0936....): ')
region = input('input phone number region(TW or JP or...): ')
phone2 = cl.getPhoneVerifMethodV2(session, phone, region)
print(f"[PHONE] {phone2[3]}")
print(f"[VerifMethod] {phone2[1]}") # if it is not include number 1, maybe will return error

sendPin = cl.requestToSendPhonePinCode(session, phone2[3], region, phone2[1][0])
print(f"[SEND PIN CODE] {sendPin}")

pin = input('Enter Pin code: ')
verify = cl.verifyPhonePinCode(session, phone, region, pin)
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
print(f"[encPwd] {encPwd}")

setPwd = cl.setPassword(session, encPwd, 1)
print(f"[setPassword] {setPwd}")

register = cl.registerPrimaryWithTokenV3(session)
print(f"[REGISTER] {register}")
print(f"---------------------------")
authKey = register[1]
tokenV3IssueResult = register[2]
mid = register[3]
primaryToken = create_token(authKey)
print(f"[AuthKey]: {authKey}")
print(f"[PrimaryToken]: {primaryToken}")
print(f"[UserMid]: {mid}")
print(f"---------------------------")
accessTokenV3 = tokenV3IssueResult[1]
print(f"[accessTokenV3]: {accessTokenV3}")
refreshToken = tokenV3IssueResult[2]
print(f"[refreshToken]: {refreshToken}")
durationUntilRefreshInSec = tokenV3IssueResult[3]
print(f"[durationUntilRefreshInSec]: {durationUntilRefreshInSec}")
refreshApiRetryPolicy = tokenV3IssueResult[4]
loginSessionId = tokenV3IssueResult[5]
print(f"[loginSessionId]: {loginSessionId}")
tokenIssueTimeEpochSec = tokenV3IssueResult[6]
print(f"[tokenIssueTimeEpochSec]: {tokenIssueTimeEpochSec}")

cl = CHRLINE(primaryToken, device="ANDROID") #login

if UPDATE_NAME:
    cl.updateProfileAttribute(2, DISPLAY_NAME) #update display name

# for i in range(100):
    # accessTokenV3 = cl.refreshAccessToken(refreshToken)
    # print(f"[accessTokenV3_2]: {accessTokenV3}")
