# -*- coding: utf-8 -*-
"""
Author: YinMo
Version: 2.1.0
Description: support pm and group chat!
"""
import hashlib
import json
import os
import base64
import axolotl_curve25519 as Curve25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .exceptions import LineServiceException


class E2EE:
    def getE2EELocalPublicKey(self, mid, keyId):
        toType = self.getToType(mid)
        if toType == 0:
            fd = ".e2eePublicKeys"
            fn = f"key_id_{keyId}.json"
            key = None
            if keyId is not None:
                key = self.getCacheData(fd, fn, False)
            if key is None:
                receiver_key_data = self.negotiateE2EEPublicKey(mid)
                specVersion = self.checkAndGetValue(receiver_key_data, "specVersion", 3)
                if specVersion == -1:
                    raise Exception(f"Not support E2EE on {mid}")
                publicKey = self.checkAndGetValue(receiver_key_data, "publicKey", 2)
                receiverKeyId = self.checkAndGetValue(publicKey, "keyId", 2)
                receiverKeyData = self.checkAndGetValue(publicKey, "keyData", 4)
                if receiverKeyId == keyId:
                    key = base64.b64encode(receiverKeyData)
                    self.saveCacheData(fd, fn, key.decode(), False)
                else:
                    raise Exception(
                        f"E2EE key id-{keyId} not found on {mid}, key id should be {receiverKeyId}"
                    )
        else:
            fd = ".e2eeGroupKeys"
            fn = f"{mid}.json"
            key = self.getCacheData(fd, fn, False)
            if keyId is not None and key is not None:
                keyData = json.loads(key)
                if keyId != keyData["keyId"]:
                    self.log(f"keyId mismatch: {mid}")
                    key = None
            else:
                key = None
            if key is None:
                try:
                    E2EEGroupSharedKey = self.getLastE2EEGroupSharedKey(2, mid)
                except LineServiceException as e:
                    if e.code == 5:
                        self.log(f"E2EE key not registered on {mid}: {e.message}")
                        E2EEGroupSharedKey = self.tryRegisterE2EEGroupKey(mid)
                groupKeyId = self.checkAndGetValue(E2EEGroupSharedKey, "groupKeyId", 2)
                creator = self.checkAndGetValue(E2EEGroupSharedKey, "creator", 3)
                creatorKeyId = self.checkAndGetValue(
                    E2EEGroupSharedKey, "creatorKeyId", 4
                )
                receiver = self.checkAndGetValue(E2EEGroupSharedKey, "receiver", 5)
                receiverKeyId = self.checkAndGetValue(
                    E2EEGroupSharedKey, "receiverKeyId", 6
                )
                encryptedSharedKey = self.checkAndGetValue(
                    E2EEGroupSharedKey, "encryptedSharedKey", 7
                )
                selfKey = base64.b64decode(
                    self.getE2EESelfKeyDataByKeyId(receiverKeyId)["privKey"]
                )
                creatorKey = self.getE2EELocalPublicKey(creator, creatorKeyId)
                aesKey = self.generateSharedSecret(selfKey, creatorKey)
                aes_key = self.getSHA256Sum(aesKey, b"Key")
                aes_iv = self._xor(self.getSHA256Sum(aesKey, b"IV"))
                aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
                try:
                    decrypted = unpad(aes.decrypt(encryptedSharedKey), 16)
                except ValueError:
                    decrypted = aes.decrypt(encryptedSharedKey)
                self.log(f"[getE2EELocalPublicKey] decrypted: {decrypted}", True)
                data = {
                    "privKey": base64.b64encode(decrypted).decode(),
                    "keyId": groupKeyId,
                }
                key = json.dumps(data)
                self.saveCacheData(fd, fn, key, False)
            return json.loads(key)
        return base64.b64decode(key)

    def generateSharedSecret(self, private_key, public_key):
        return Curve25519.calculateAgreement(bytes(private_key), bytes(public_key))

    def tryRegisterE2EEGroupKey(self, group_mid: str):
        E2EEPublicKeys = self.getLastE2EEPublicKeys(group_mid)
        members = []
        keyIds = []
        encryptedSharedKeys = []
        selfKeyId = [
            self.checkAndGetValue(E2EEPublicKeys[key], "keyId", 2)
            for key in E2EEPublicKeys
            if key == self.mid
        ][0]
        selfKey = base64.b64decode(self.getE2EESelfKeyDataByKeyId(selfKeyId)["privKey"])
        private_key = Curve25519.generatePrivateKey(bytes(32))  # ios patch
        # you can use bytes(32) for LINE Android & PC ver. but it will failed to decrypt on iOS & ChromeOS
        for key_mid in E2EEPublicKeys:
            members.append(key_mid)
            key = E2EEPublicKeys[key_mid]
            keyId = self.checkAndGetValue(key, "keyId", 2)
            keyData = self.checkAndGetValue(key, "keyData", 4)
            keyIds.append(keyId)
            aesKey = self.generateSharedSecret(selfKey, keyData)
            aes_key = self.getSHA256Sum(aesKey, b"Key")
            aes_iv = self._xor(self.getSHA256Sum(aesKey, b"IV"))
            aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
            encryptedSharedKey = aes.encrypt(pad(private_key, 16))
            encryptedSharedKeys.append(encryptedSharedKey)
        E2EEGroupSharedKey = self.registerE2EEGroupKey(
            1, group_mid, members, keyIds, encryptedSharedKeys
        )
        self.log(f"E2EE key register on {group_mid}: {E2EEGroupSharedKey}")
        return E2EEGroupSharedKey

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
        aes_key = self.getSHA256Sum(shared_secret, "Key")
        aes_iv = self._xor(self.getSHA256Sum(shared_secret, "IV"))
        aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        keychain_data = aes.decrypt(encryptedKeyChain)
        key = keychain_data.hex()
        key = bin2bytes(key)
        tc = self.TCompactProtocol(self, passProtocol=True)
        tc.data = key
        key = tc.x(False)[1]
        public_key = bytes(key[0][4])
        private_key = bytes(key[0][5])
        return [private_key, public_key]

    def encryptDeviceSecret(self, publicKey, privateKey, encryptedKeyChain):
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        aes_key = self.getSHA256Sum(shared_secret, "Key")
        encryptedKeyChain = self._xor(self.getSHA256Sum(encryptedKeyChain))
        keychain_data = self._encryptAESECB(aes_key, encryptedKeyChain)
        return keychain_data

    def generateAAD(self, a, b, c, d, e=2, f=0):
        aad = b""
        aad += a.encode()
        aad += b.encode()
        aad += bytes(self.getIntBytes(c))
        aad += bytes(self.getIntBytes(d))
        aad += bytes(self.getIntBytes(e))  # e2ee version
        aad += bytes(self.getIntBytes(f))  # content type
        return aad

    def encryptE2EEMessage(
        self, to, text, specVersion=2, isCompact=False, contentType=0
    ):
        _from = self.mid
        selfKeyData = self.getE2EESelfKeyData(_from)
        if len(to) == 0 or self.getToType(to) not in [0, 1, 2]:
            raise Exception("Invalid mid")
        senderKeyId = selfKeyData["keyId"]
        if self.getToType(to) == 0:
            private_key = base64.b64decode(selfKeyData["privKey"])
            receiver_key_data = self.negotiateE2EEPublicKey(to)
            specVersion = self.checkAndGetValue(receiver_key_data, "specVersion", 3)
            if specVersion == -1:
                raise Exception(f"Not support E2EE on {to}")
            publicKey = self.checkAndGetValue(receiver_key_data, "publicKey", 2)
            receiverKeyId = self.checkAndGetValue(publicKey, "keyId", 2)
            receiverKeyData = self.checkAndGetValue(publicKey, "keyData", 4)
            keyData = self.generateSharedSecret(bytes(private_key), receiverKeyData)
        else:
            groupK = self.getE2EELocalPublicKey(to, None)
            privK = base64.b64decode(groupK["privKey"])
            pubK = base64.b64decode(selfKeyData["pubKey"])
            receiverKeyId = groupK["keyId"]
            keyData = self.generateSharedSecret(privK, pubK)
        if contentType == 15:
            chunks = self.encryptE2EELocationMessage(
                senderKeyId,
                receiverKeyId,
                keyData,
                specVersion,
                text,
                to,
                _from,
                isCompact=isCompact,
            )
        else:
            chunks = self.encryptE2EETextMessage(
                senderKeyId,
                receiverKeyId,
                keyData,
                specVersion,
                text,
                to,
                _from,
                isCompact=isCompact,
            )
        return chunks

    def encryptE2EETextMessage(
        self,
        senderKeyId,
        receiverKeyId,
        keyData,
        specVersion,
        text,
        to,
        _from,
        isCompact=False,
    ):
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b"Key")
        aad = self.generateAAD(to, _from, senderKeyId, receiverKeyId, specVersion, 0)
        sign = os.urandom(16)
        data = json.dumps({"text": text}).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        bSenderKeyId = bytes(self.getIntBytes(senderKeyId))
        bReceiverKeyId = bytes(self.getIntBytes(receiverKeyId))
        if isCompact:
            compact = self.TCompactProtocol(self)
            bSenderKeyId = bytes(compact.writeI32(int(senderKeyId)))
            bReceiverKeyId = bytes(compact.writeI32(int(receiverKeyId)))
        self.log(f"senderKeyId: {senderKeyId} ({bSenderKeyId})", True)
        self.log(f"receiverKeyId: {receiverKeyId} ({bReceiverKeyId})", True)
        return [salt, encData, sign, bSenderKeyId, bReceiverKeyId]

    def encryptE2EELocationMessage(
        self,
        senderKeyId,
        receiverKeyId,
        keyData,
        specVersion,
        location,
        to,
        _from,
        isCompact=False,
    ):
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b"Key")
        aad = self.generateAAD(to, _from, senderKeyId, receiverKeyId, specVersion, 15)
        sign = os.urandom(16)
        data = json.dumps({"location": location}).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        bSenderKeyId = bytes(self.getIntBytes(senderKeyId))
        bReceiverKeyId = bytes(self.getIntBytes(receiverKeyId))
        if isCompact:
            compact = self.TCompactProtocol(self)
            bSenderKeyId = bytes(compact.writeI32(int(senderKeyId)))
            bReceiverKeyId = bytes(compact.writeI32(int(receiverKeyId)))
        self.log(f"senderKeyId: {senderKeyId} ({bSenderKeyId})", True)
        self.log(f"receiverKeyId: {receiverKeyId} ({bReceiverKeyId})", True)
        return [salt, encData, sign, bSenderKeyId, bReceiverKeyId]

    def encryptE2EEMessageV2(self, data, gcmKey, nonce, aad):
        aesgcm = AESGCM(gcmKey)
        return aesgcm.encrypt(nonce, data, aad)

    def decryptE2EETextMessage(self, messageObj, isSelf=True):
        _from = self.checkAndGetValue(messageObj, "_from", 1)
        to = self.checkAndGetValue(messageObj, "to", 2)
        toType = self.checkAndGetValue(messageObj, "toType", 3)
        metadata = self.checkAndGetValue(messageObj, "contentMetadata", 18)
        specVersion = metadata.get("e2eeVersion", "2")
        contentType = self.checkAndGetValue(messageObj, "contentType", 15)
        chunks = self.checkAndGetValue(messageObj, "chunks", 20)
        for i in range(len(chunks)):
            if isinstance(chunks[i], str):
                chunks[i] = chunks[i].encode()
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])
        self.log(f"senderKeyId: {senderKeyId}", True)
        self.log(f"receiverKeyId: {receiverKeyId}", True)

        selfKey = self.getE2EESelfKeyData(self.mid)
        privK = base64.b64decode(selfKey["privKey"])
        if toType == 0:
            pubK = self.getE2EELocalPublicKey(
                to if isSelf else _from, receiverKeyId if isSelf else senderKeyId
            )
        else:
            groupK = self.getE2EELocalPublicKey(to, receiverKeyId)
            privK = base64.b64decode(groupK["privKey"])
            pubK = base64.b64decode(selfKey["pubKey"])
            if _from != self.mid:
                pubK = self.getE2EELocalPublicKey(_from, senderKeyId)

        if specVersion == "2":
            decrypted = self.decryptE2EEMessageV2(
                to, _from, chunks, privK, pubK, specVersion, contentType
            )
        else:
            decrypted = self.decryptE2EEMessageV1(chunks, privK, pubK)
        return decrypted.get("text", "")

    def decryptE2EELocationMessage(self, messageObj, isSelf=True):
        _from = self.checkAndGetValue(messageObj, "_from", 1)
        to = self.checkAndGetValue(messageObj, "to", 2)
        toType = self.checkAndGetValue(messageObj, "toType", 3)
        metadata = self.checkAndGetValue(messageObj, "contentMetadata", 18)
        specVersion = metadata.get("e2eeVersion", "2")
        contentType = self.checkAndGetValue(messageObj, "contentType", 15)
        chunks = self.checkAndGetValue(messageObj, "chunks", 20)
        for i in range(len(chunks)):
            if isinstance(chunks[i], str):
                chunks[i] = chunks[i].encode()
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])
        self.log(f"senderKeyId: {senderKeyId}", True)
        self.log(f"receiverKeyId: {receiverKeyId}", True)

        selfKey = self.getE2EESelfKeyData(self.mid)
        privK = base64.b64decode(selfKey["privKey"])
        if toType == 0:
            pubK = self.getE2EELocalPublicKey(
                to, receiverKeyId if isSelf else senderKeyId
            )
        else:
            groupK = self.getE2EELocalPublicKey(to, receiverKeyId)
            privK = base64.b64decode(groupK["privKey"])
            pubK = base64.b64decode(selfKey["pubKey"])
            if _from != self.mid:
                pubK = self.getE2EELocalPublicKey(_from, senderKeyId)

        if specVersion == "2":
            decrypted = self.decryptE2EEMessageV2(
                to, _from, chunks, privK, pubK, specVersion, contentType
            )
        else:
            decrypted = self.decryptE2EEMessageV1(chunks, privK, pubK)
        return decrypted.get("location", None)

    def decryptE2EEMessageV1(self, chunks, privK, pubK):
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        aesKey = self.generateSharedSecret(privK, pubK)
        aes_key = self.getSHA256Sum(aesKey, salt, b"Key")
        aes_iv = self._xor(self.getSHA256Sum(aesKey, salt, "IV"))
        aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        decrypted = aes.decrypt(message)
        self.log(f"decrypted: {decrypted}", True)
        decrypted = unpad(decrypted, 16)
        return json.loads(decrypted)

    def decryptE2EEMessageV2(
        self, to, _from, chunks, privK, pubK, specVersion=2, contentType=0
    ):
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])

        aesKey = self.generateSharedSecret(privK, pubK)
        gcmKey = self.getSHA256Sum(aesKey, salt, b"Key")
        aad = self.generateAAD(
            to, _from, senderKeyId, receiverKeyId, specVersion, contentType
        )

        aesgcm = AESGCM(gcmKey)
        decrypted = aesgcm.decrypt(sign, message, aad)
        self.log(f"decrypted: {decrypted}", True)
        return json.loads(decrypted)


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
        _i = int(k[i * 2 : i * 2 + 2], 16)
        e.append(_i)
    return bytearray(e)
