# -*- coding: utf-8 -*-
import os, sys, threading, time, traceback

class Poll(object):
    opFuncs = {}

    def __init__(self):
        pass
    def __fetchOps(self, revision, count=100):
        return self.fetchOps(revision, count)
    
    def __execute(self, op, func):
        try:
            func(op, self)
        except Exception as e:
            self.log(traceback.format_exc())

    def addOpFunc(self, opType, func):
        self.opFuncs[opType] = func
    
    def setRevision(self, revision):
        self.revision = max(revision, self.revision)

    def trace(self, func, isThreading=True):
        while self.is_login:
            ops = self.__fetchOps(self.revision)
            if 'error' in ops:
                raise Exception(ops['error'])
            for op in ops:
                if op[3] != 0 and op[3] != -1:
                    self.setRevision(op[1])
                    if isThreading:
                        _td = threading.Thread(target=self.__execute, args=(op, func))
                        _td.daemon = True
                        _td.start()
                    else:
                        self.__execute(op, func)