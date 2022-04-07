from CHRLINE import *
from CHRLINE.hooks import HooksTracer

cl = CHRLINE()
#cl = CHRLINE(device="IOSIPAD", version="10.21.3", os_name="iOS", os_ver="11")#with IOSIPAD
#cl = CHRLINE("your email", "your password") #with Email
#cl = CHRLINE(phone="your phone number(0911....)", region="your phone region(TW ,JP, ID..)") #with phone number

token = cl.authToken
print(f"authToken: {token}")

# #
# HooksTracer is implemented in CHRLINE v1.5.0, thanks to the code provided by Domao!
# For more detailed usage, just refer to examples/test_hooks_bot.py
# #
tracer = HooksTracer(
    cl, # main account
    prefixes=[""], # cmd prefixes
)

class EventHook:

    @tracer.Event
    def onReady():
        print('Ready!')

class OpHook(object):

    @tracer.Operation(26)
    def recvMessage(self, op, cl):
        msg = op[20]
        self.trace(msg, self.HooksType["Content"], cl)

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = msg.get(10)
        self.trace(msg, self.HooksType['Command'], cl)

class NormalCmd(object):

    @tracer.Command(ignoreCase=True)
    def ping(self, msg, cl):
        '''Ping.'''
        cl.replyMessage(msg, "Pong!")

tracer.run()