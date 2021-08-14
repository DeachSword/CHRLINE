"""
Author: YinMo
Version: 0.0.1-beta
Description: died
"""
import hashlib, json, os
import axolotl_curve25519 as Curve25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from Crypto.Cipher import AES

class E2EE():

    def generateSharedSecret(self, private_key, public_key):
        return Curve25519.calculateAgreement(bytes(private_key), bytes(public_key))
    
    def _xor(self, buf):
        buf_length = int(len(buf) / 2)
        buf2 = bytearray(buf_length)
        for i in range(buf_length):
            buf2[i] = buf[i] ^ buf[buf_length + i]
        return bytes(buf2)
    
    def getSHA256Sum(self, *args):
        instance = hashlib.sha256()
        for arg in args:
            if isinstance(arg, str):
                arg = arg.encode()
            instance.update(arg)
        return instance.digest()
    
    def _encryptAESECB(self, aes_key, plain_data):
        aes = AES.new(aes_key, AES.MODE_ECB)
        return aes.encrypt(plain_data)
    
    def decryptKeyChain(self, publicKey, privateKey, encryptedKeyChain):
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        aes_key = self.getSHA256Sum(shared_secret, 'Key')
        aes_iv = self._xor(self.getSHA256Sum(shared_secret, 'IV'))
        aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        keychain_data = aes.decrypt(encryptedKeyChain)
        key = keychain_data.hex()
        key = bin2bytes(key)
        key = self.tryReadThriftContainerStruct(key)
        public_key = bytes(key[1][0][4])
        private_key = bytes(key[1][0][5])
        return [private_key, public_key]
    
    def encryptDeviceSecret (self, publicKey, privateKey, encryptedKeyChain):
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        aes_key = self.getSHA256Sum(shared_secret, 'Key')
        encryptedKeyChain = self._xor(self.getSHA256Sum(encryptedKeyChain))
        keychain_data = self._encryptAESECB(aes_key, encryptedKeyChain)
        return keychain_data
    
    def generateAAD(self, a, b, c, d, e=2, f=0):
        aad = b''
        aad += a.encode()
        aad += b.encode()
        aad += bytes(self.getIntBytes(c))
        aad += bytes(self.getIntBytes(d))
        aad += bytes(self.getIntBytes(e))
        aad += bytes(self.getIntBytes(f))
        return aad
    
    def encryptE2EETextMessage(self, senderKeyId, receiverKeyId, keyData, specVersion, text, to ,_from):
        #selfKey = self.getE2EEKeys(self.mid)
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b'Key')
        gcmIV = self.getSHA256Sum(keyData, salt, b'IV')
        aad = self.generateAAD(to, _from, senderKeyId, receiverKeyId, specVersion, 0)
        sign = os.urandom(16)
        data = json.dumps({
            'text': text
        }).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        print(f'senderKeyId: {senderKeyId} ({self.getIntBytes(senderKeyId)})')
        print(f'receiverKeyId: {receiverKeyId} ({self.getIntBytes(receiverKeyId)})')
        return [salt, encData, sign, bytes(self.getIntBytes(senderKeyId)), bytes(self.getIntBytes(receiverKeyId))]
    
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
    
    def decryptE2EETextMessageV2(self, to , _from, chunks, privK, pubK):
        for i in range(len(chunks)):
            if isinstance(chunks[i], str):
                chunks[i] = chunks[i].encode()
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])
        print(f'senderKeyId: {senderKeyId}')
        print(f'receiverKeyId: {receiverKeyId}')
        
        aesKey = self.generateSharedSecret(privK, pubK)
        gcmKey = self.getSHA256Sum(aesKey, salt, b'Key')
        iv = self.getSHA256Sum(aesKey, salt, b'IV')
        aad = self.generateAAD(to, _from, senderKeyId, receiverKeyId)
        
        aesgcm = AESGCM(gcmKey)
        decrypted = aesgcm.decrypt(sign, message, aad)
        print(f'decrypted: {decrypted}')
        return json.loads(decrypted)['text']
    
    def encryptE2EEMessageV2(self, data, gcmKey, nonce, aad):
        aesgcm = AESGCM(gcmKey)
        return aesgcm.encrypt(nonce, data, aad)

def byte2int(t):
    e = 0
    i = 0
    s = len(t)
    for i in range(s):
        e = 256 * e + t[i]
    return e

def bin2bytes(k):
    e = []
    for i in range(int(len(k) / 2)):
        _i = int(k[i * 2:i * 2 + 2], 16)
        e.append(_i)
    return bytearray(e)