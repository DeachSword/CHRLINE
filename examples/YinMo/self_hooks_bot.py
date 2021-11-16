# -*- coding: utf-8 -*- 
from CHRLINE import *
from CHRLINE.hooks import HooksTracer
import time

cl = CHRLINE(device="IOSIPAD")

tracer = HooksTracer(
    cl, # main account
    prefixes=[""], # cmd prefixes
    # db="test_hook", # database name, if None will use main account's mid
    # accounts=[cl2, cl3] # sub accounts
)

class EventHook:

    @tracer.Event
    def onReady():
        print('Ready!')

class OpHook(object):

    @tracer.Operation(25)
    def sendMessage(self, op, cl):
        msg = op[20]
        self.trace(msg, self.HooksType["Content"], cl)

    @tracer.Operation(26)
    def recvMessage(self, op, cl):
        msg = op[20]
        #if msg[1] == cl8.mid:
        #    return # pass if is bot message
        self.trace(msg, self.HooksType["Content"], cl)

    @tracer.Operation(124)
    def recvChatInvite(self, op, cl):
        gid = op[10]
        inviter = op[11]
        mid = op[12]
        if mid == cl.mid:
            # someone invited the bot
            cl.acceptChatInvitation(gid) # join
            cl.sendCompactMessage(gid, 'hello! Korone is my waifu >w<')

    @tracer.Operation(127)
    def deleteSelfFromChat(self, op, cl):
        gid = op[10]
        if gid in cl.groups:
            cl.groups.remove(gid) # update local cache data

    @tracer.Operation(129)
    def joinChat(self, op, cl):
        gid = op[10]
        if gid not in cl.groups:
            cl.groups.append(gid) # update local cache data

    @tracer.Operation(133)
    def recvDeleteOtherFromChat(self, op, cl):
        gid = op[10]
        kicker = op[11]
        mid = op[12]
        if mid == cl.mid:
            # someone kick the bot
            if gid in cl.groups:
                cl.groups.remove(gid) # update local cache data

    @tracer.Before(tracer.HooksType["Operation"])
    def __before(self, op, cl):
        # handle all op
        # u can do something here for the same operation when multiple accounts
        # print(f"[{op[3]}]{op}")
        pass

    @tracer.After(tracer.HooksType["Operation"])
    def __after(self, op, cl):
        # handle not tracked op
        opType = op[3]
        if opType not in [0, 48]:
            print(f"[{op[3]}]{op}")

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = msg.get(10)
        self.trace(msg, self.HooksType['Command'], cl)

    @tracer.Content(1)
    def ImageMessage(self, msg, cl):
        id = msg[4]
        metadata = msg[18]

class NormalCmd(object):

    @tracer.Command(ignoreCase=True)
    def hi(self, msg, cl):
        '''Debug.'''
        cl.replyMessage(msg, "Hi!")

    @tracer.Command(ignoreCase=True, inpart=True)
    def test(self, msg, cl):
        '''Test.'''
        cl.replyMessage(msg, "this is test!")

    @tracer.Command(alt=["指令"], ignoreCase=True)
    def help(self, msg, cl):
        '''cmd list'''
        cl.replyMessage(msg, self.genHelp(self.getPrefix(msg[10])))

    @tracer.Command(alt=["sp"], ignoreCase=True)
    def speed(self, msg, cl):
        '''測速用'''
        a = time.time()
        cl.replyMessage(msg, 'okok...')
        b = time.time() - a
        cl.replyMessage(msg, f'speed: {b}s')

    @tracer.Command(permissions=["admin"], ignoreCase=True)
    def checkOp(self, msg, cl):
        '''Admin Only.'''
        cl.replyMessage(msg, f'u is Admin!')

tracer.run()