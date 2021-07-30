"""
Author: YinMo
Version: 0.0.1-beta
Description: died
"""
import hashlib, json
import axolotl_curve25519 as Curve25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class E2EE():

    def generateSharedSecret(self, private_key, public_key):
    return Curve25519.calculateAgreement(private_key, public_key)

    def getSHA256Sum(*args):
        instance = hashlib.sha256()
        for arg in args:
            if isinstance(arg, str):
                arg = arg.encode()
            instance.update(arg)
        return instance.digest()
    
    def generateAAD(self, a, b, c, d, e=2, f=0):
        aad = b''
        aad += a.encode()
        aad += b.encode()
        aad += bytes(cl.getIntBytes(c))
        aad += bytes(cl.getIntBytes(d))
        aad += bytes(cl.getIntBytes(e))
        aad += bytes(cl.getIntBytes(f))
        return aad
    
    def decryptE2EETextMessage(self, messageObj):
        chunks = messageObj[20]
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        senderKeyId = __byte2int(chunks[3])
        receiverKeyId = __byte2int(chunks[4])
        
        _key = self.negotiateE2EEPublicKey(messageObj[0]) # todo: to or _from
        
        aesKey = self.generateSharedSecret(self.getPrivateKey(self.mid), _key[2][4])
        gcmKey = self.getSHA256Sum(aesKey, salt, b'Key')
        s = hashlib.sha256()
        s.update(aesKey)
        s.update(salt)
        s.update(b'IV')
        iv = s.digest()
        aad = self.generateAAD(message[0], message[1], senderKeyId, receiverKeyId)
        
        aesgcm = AESGCM(gcmKey)
        decrypted = aesgcm.decrypt(sign, message, aad)
        print(f'decrypted: {decrypted}')
        return json.loads(decrypted)['text'] # todo: contentType

def __byte2int(a):
    e = 0
    i = 0
    s = len(t)
    for i in range(s):
        e = 256 * e + t[i]
    return e