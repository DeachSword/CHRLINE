# -*- coding: utf-8 -*- 
from .hksc.types import HookTypes
from .hksc.events import HookEvents
from .hksc.utility import HookUtility
from .hksc.database import SqliteDatabase, JsonDatabase
import threading


class HooksTracer(HookTypes, HookUtility):
    HooksType = {
        'Operation': 0,
        'Content': 1,
        'Command': 2,
        'SquareEvent': 7
    }

    def __init__(self, cl, db=None, prefixes=["!"], accounts=[], db_type=3):
        self.cl = cl
        self.db = None
        if db_type == 2:
            self.db = SqliteDatabase(cl, db)
        elif db_type == 3:
            self.db = JsonDatabase(cl, db)
        else:
            raise NotImplementedError()
        self.prefixes = prefixes
        self.opFuncs = []
        self.contFuncs = []
        self.cmdFuncs = []
        self.beforeFuncs = []
        self.afterFuncs = []
        self.eventFuncs = HookEvents()
        self.accounts = accounts

        # OpenChat
        self.seFuncs = []

    def run(self, fetchType: int = 0):
        self.eventFuncs.onReady()
        for _cl in self.accounts:
            _td = threading.Thread(target=self.runByClient, args=(_cl, fetchType))
            _td.daemon = True
            _td.start()
        self.runByClient(self.cl, fetchType)

    def runByClient(self, cl, fetchType: int = 0, **kwargs):
        while cl.is_login:
            if fetchType == 0:
                for op in cl._Poll__fetchOps():
                    _td = threading.Thread(target=self.trace, args=(op, self.HooksType['Operation'], cl))
                    _td.daemon = True
                    _td.start()
            elif fetchType == 2:
                cl.legyPushers.hook_callback = self.PushCallback
                cl.legyPushers.initializeConn()
                cl.legyPushers.InitAndRead(**kwargs)
                print('legyPushers died')
                break
            else:
                raise ValueError("Invalid fetchType: %d" % fetchType)

    def trace(self, data, type, cl, *attr):
        if type == self.HooksType['Operation']:
            _a = self.opFuncs
        elif type == self.HooksType['Content']:
            _a = self.contFuncs
        elif type == self.HooksType['Command']:
            _a = self.cmdFuncs
        elif type == self.HooksType['SquareEvent']:
            _a = self.seFuncs
        else:
            raise Exception(f"unknow type: {type}")
        _b = self.beforeFuncs
        _c = self.afterFuncs
        for _before in _b:
            if _before.type == type:
                if _before(self, data, cl, *attr):
                    break
        for _func in _a:
            if _func(self, data, cl, *attr):
                return True
        for _after in _c:
            if _after.type == type:
                if _after(self, data, cl, *attr):
                    break
        return False
    
    def PushCallback(self, cl, serviceType, event):
        ht = None
        if serviceType == 3:
            ht = 'SquareEvent'
        elif serviceType == 5:
            ht = 'Operation'
        else:
            raise ValueError("Invalid serviceType: {serviceType}")
        _td = threading.Thread(target=self.trace, args=(event, self.HooksType[ht], cl))
        _td.daemon = True
        _td.start()
