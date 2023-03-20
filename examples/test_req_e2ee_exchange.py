"""
Exchange E2EE Key.

Send message `test` to your bot's group for use.
and enter pincode `010519` on bot account's phone.

This example uses HooksTracer, 
and uses the `/PUSH` endpoint for fetch messages.
some devices may not work (IOSIPAD has been tested success :3)
"""
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
import base64
import json

cl = CHRLINE(device="IOSIPAD", useThrift=True)


tracer = HooksTracer(
    cl,  # main account
    prefixes=[""],  # cmd prefixes
)

GLOBAL_PRIV_KEY = None
GLOBAL_E2EE_KEY_ID = None
GLOBAL_E2EE_PUB_KEY = None
GLOBAL_E2EE_VER = None

class OpHook(object):

    @tracer.Operation(26)  # change 25 if self send message
    def recvMessage(self, op, cl):
        msg = cl.checkAndGetValue(op, 'message', 20)
        text = cl.checkAndGetValue(msg, 'text', 10)
        to = cl.checkAndGetValue(msg, 'to', 2)
        _from = cl.checkAndGetValue(msg, '_from', 1)
        self.trace(msg, self.HooksType["Content"], cl)
        
    @tracer.Operation(74)
    def NOTIFIED_E2EE_KEY_EXCHANGE_RESP(self, op, cl):
        param1 = cl.checkAndGetValue(op, 'param1', 10)
        print(f"[NOTIFIED_E2EE_KEY_EXCHANGE_RESP] {param1}")
        if GLOBAL_PRIV_KEY is not None:
            data = json.loads(param1)
            data['keyId'] = GLOBAL_E2EE_KEY_ID
            data['publicKey'] = GLOBAL_E2EE_PUB_KEY
            data['e2eeVersion'] = GLOBAL_E2EE_VER
            decode = cl.decodeE2EEKeyV1(data, GLOBAL_PRIV_KEY, cl.mid)
            print(f'Recv E2EE key data: {decode}')
        else:
            raise ValueError('GLOBAL_PRIV_KEY is nil.')

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = cl.checkAndGetValue(msg, 'text', 10)
        to = cl.checkAndGetValue(msg, 'to', 2)
        _from = cl.checkAndGetValue(msg, '_from', 1)
        relatedMessageId = cl.checkAndGetValue(msg, 'relatedMessageId', 21)
        r = self.trace(msg, self.HooksType['Command'], cl)

class NormalCmd(object):

    @tracer.Command(ignoreCase=True, inpart=True, toType=[2, 4])  # toType is GROUP
    def test(self, msg, cl):
        '''Test.'''
        text = cl.checkAndGetValue(msg, 'text', 10)
        to = cl.checkAndGetValue(msg, 'to', 2)
        _from = cl.checkAndGetValue(msg, '_from', 1)
        pks = cl.getE2EEPublicKeys()
        if pks:
            global GLOBAL_PRIV_KEY, GLOBAL_E2EE_KEY_ID, GLOBAL_E2EE_PUB_KEY, GLOBAL_E2EE_VER
            targetKey = pks[0]
            privK, pubB64 = cl.createSqrSecret(True)
            targetKeyVer = cl.checkAndGetValue(targetKey, 'version', 1)
            targetKeyId = cl.checkAndGetValue(targetKey, 'keyId', 2)
            targetPubK = cl.checkAndGetValue(targetKey, 'keyData', 4)
            PINCODE = '010519'
            sign = cl.generateSharedSecret(privK, targetPubK)
            enc_pin = cl.getSHA256Sum(sign, cl.mid, PINCODE)
            cl.requestE2EEKeyExchange(base64.b64decode(pubB64), targetKeyVer, targetKeyId, enc_pin)
            print(f'Send E2EE key exchange req, enter pincode `{PINCODE}` on your phone.')
            GLOBAL_PRIV_KEY = privK
            GLOBAL_E2EE_KEY_ID = targetKeyId
            GLOBAL_E2EE_PUB_KEY = base64.b64encode(targetPubK)
            GLOBAL_E2EE_VER = targetKeyVer
        else:
            raise ValueError('No E2EE Keys.')

tracer.run(2, **{
    'initServices': [5]
})