# -*- coding: utf-8 -*-

class BaseEvent:

    def onReady(self):
        pass

    def onPing(self):
        pass

    def onError(self):
        pass

    def onStop(self):
        print("bye")

class HookEvents(BaseEvent):

    def __init__(self):
        pass

    def onInitializePushConn(self):
        pass