# -*- coding: utf-8 -*-
from ..CHRLINE import *
from ..CHRLINE.hooks import HooksTracer


# Use DESKTOPWIN to test
# because I don't trust IOSIPAD -w-|||
cl = CHRLINE(device="DESKTOPWIN")

# Instantiate HooksTracer
tracer = HooksTracer(
    cl,  # main account
    prefixes=[""],  # cmd prefixes
)

class SquareEventHook(object):

    @tracer.SquareEvent(29)
    def NOTIFICATION_MESSAGE(self, event, cl):
        payload = cl.checkAndGetValue(event, 'payload', 4)
        notificationMessage = cl.checkAndGetValue(payload, 'notificationMessage', 30)
        squareChatMid = cl.checkAndGetValue(notificationMessage, 'squareChatMid', 1)
        squareMessage = cl.checkAndGetValue(notificationMessage, 'squareMessage', 2)
        senderDisplayName = cl.checkAndGetValue(notificationMessage, 'senderDisplayName', 3)
        message = cl.checkAndGetValue(squareMessage, 'message', 1)
        text = cl.checkAndGetValue(message, 'text', 10)
        print(f'收到訊息: {senderDisplayName} -> {text}')

        # OpenChat's msg is exactly same as Talk's msg
        # so you can track in the same way
        self.trace(message, self.HooksType["Content"], cl)

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        self.trace(msg, self.HooksType['Command'], cl)

class NormalCmd(object):

    # Default toType only works in Talk
    # you need to specify a special toType to make it work in OpenChat
    @tracer.Command(ignoreCase=True, toType=[4])
    def hi(self, msg, cl):
        '''Debug.'''
        cl.replyMessage(msg, "Hi!")