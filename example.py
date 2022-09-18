from CHRLINE import *
from CHRLINE.hooks import HooksTracer

cl = CHRLINE(useThrift=True)
#cl = CHRLINE(device="IOSIPAD", version="10.21.3", os_name="iOS", os_ver="11")  #with IOSIPAD
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

    @tracer.Event
    def onInitializePushConn():
        print('onInitializePushConn!')


class SquareEventHook(object):

    @tracer.Before(tracer.HooksType["SquareEvent"])
    def __before(self, op, cl):
        pass

    @tracer.SquareEvent(29)
    def NOTIFICATION_MESSAGE(self, event, cl):
        payload = cl.checkAndGetValue(event, 'payload', 4)
        notificationMessage = cl.checkAndGetValue(payload, 'notificationMessage', 30)
        squareChatMid = cl.checkAndGetValue(notificationMessage, 'squareChatMid', 1)
        squareMessage = cl.checkAndGetValue(notificationMessage, 'squareMessage', 2)
        senderDisplayName = cl.checkAndGetValue(notificationMessage, 'senderDisplayName', 3)
        message = cl.checkAndGetValue(squareMessage, 'message', 1)
        text = cl.checkAndGetValue(message, 'text', 10)
        self.trace(message, self.HooksType["Content"], cl)

    @tracer.After(tracer.HooksType["SquareEvent"])
    def __after(self, op, cl):
        print(f"{op}")
        

class OpHook(object):

    @tracer.Operation(26)
    def recvMessage(self, op, cl):
        msg = op.message
        self.trace(msg, self.HooksType["Content"], cl)

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = msg.text
        self.trace(msg, self.HooksType['Command'], cl)

class NormalCmd(object):

    @tracer.Command(ignoreCase=True)
    def ping(self, msg, cl):
        '''Ping.'''
        cl.replyMessage(msg, "Pong!")

    @tracer.Command(ignoreCase=True)
    def ping(self, msg, cl, toType=[4]):
        '''Ping for OpenChat.'''
        cl.replyMessage(msg, "Pong!!!")

tracer.run()  # run for Talk only

# run for Square + Talk (use /PUSH path)
# tracer.run(2, **{
    # 'initServices': [3, 5]
# })