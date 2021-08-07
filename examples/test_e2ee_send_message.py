from CHRLINE import *

import base64

cl = CHRLINE()

to = '' # user mid
_from = cl.mid
selfKeyData = cl.getE2EESelfKeyData(_from)
if len(to) == 0 or cl.getToType(to) != 0:
    raise Exception('Invalid mid')
if selfKeyData is None:
    raise Exception('E2EE Key has not been saved, try register or use SQR Login')
senderKeyId = selfKeyData['keyId']
private_key = base64.b64decode(selfKeyData['privKey'])
receiver_key_data = cl.negotiateE2EEPublicKey(to)
if receiver_key_data[3] == -1:
    raise Exception(f'Not support E2EE on {to}')
receiverKeyId = receiver_key_data[2][2]
keyData = cl.generateSharedSecret(bytes(private_key), receiver_key_data[2][4])
specVersion = receiver_key_data[3]
text = 'bao別再搞事'
encData = cl.encryptE2EETextMessage(senderKeyId, receiverKeyId, keyData, specVersion, text, to ,_from)

print(cl.sendMessageWithChunks(to, encData, 0, {'e2eeVersion': '2', 'contentType': '0'}))