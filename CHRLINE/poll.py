# -*- coding: utf-8 -*-
import os, sys, threading, time, traceback

class Poll(object):

    def __init__(self):
        pass

    def __fetchOps(self, count=100):
        ops = self.fetchOps(self.revision, count)
        if 'error' in ops:
            raise Exception(ops['error'])
        for op in ops:
            opType = self.checkAndGetValue(op, 'type', 3)
            if opType != -1:
                self.setRevision(self.checkAndGetValue(op, 'revision', 1))
            yield op

    def __execute(self, op, func):
        try:
            func(op, self)
        except Exception as e:
            self.log(traceback.format_exc())

    def setRevision(self, revision):
        self.revision = max(revision, self.revision)

    def trace(self, func, isThreading=True):
        while self.is_login:
            for op in self.__fetchOps():
                opType = self.checkAndGetValue(op, 'type', 'val_3', 3)
                if opType != 0 and opType != -1:
                    if isThreading:
                        _td = threading.Thread(target=self.__execute, args=(op, func))
                        _td.daemon = True
                        _td.start()
                    else:
                        self.__execute(op, func)