# -*- coding: utf-8 -*-
from .hksc.types import HookTypes
from .hksc.events import HookEvents
from .hksc.utility import HookUtility
from .hksc.database import SqliteDatabase, JsonDatabase
import threading
import time


class HooksTracer(HookTypes, HookUtility):
    HooksType = {"Operation": 0, "Content": 1, "Command": 2, "SquareEvent": 7}

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

    def run(self, fetchType: int = 0, **kwargs):
        self.eventFuncs.onReady()
        for _cl in self.accounts:
            _td = threading.Thread(
                target=self.runByClient, args=(_cl, fetchType), kwargs=kwargs
            )
            _td.daemon = True
            _td.start()
        self.runByClient(self.cl, fetchType, **kwargs)

    def runByClient(self, cl, fetchType: int = 0, **kwargs):
        IGNORE_ERRORS = ["ConnectionResetError", "gaierror"]
        while cl.is_login:
            if fetchType == 0:
                for op in cl._Poll__fetchOps():
                    _td = threading.Thread(
                        target=self.trace, args=(op, self.HooksType["Operation"], cl)
                    )
                    _td.daemon = True
                    _td.start()
            elif fetchType == 2:
                cl.legyPushers.hook_callback = self.PushCallback
                if cl.DEVICE_TYPE not in ["ANDROID", "IOS", "DESKTOPWIN", "DESKTOPMAC"]:
                    raise ValueError("device not supported PUSH: {cl.DEVICE_TYPE}")
                try:
                    cl.legyPushers.conns = []
                    cl.legyPushers.initializeConn()
                    self.eventFuncs.onInitializePushConn()
                    cl.legyPushers.InitAndRead(**kwargs)
                except Exception as e:
                    cl.log(f"[POLLING] Push dead by `{e.__class__.__name__}`: {e}")
                    if e.__class__.__name__ not in IGNORE_ERRORS:
                        raise e
                cl.log("[POLLING] Push conn is dead! retry after 3.3 sec.")
                time.sleep(3.3)
            else:
                raise ValueError("Invalid fetchType: %d" % fetchType)

    def trace(self, data, type, cl, *attr):
        if type == self.HooksType["Operation"]:
            _a = self.opFuncs
        elif type == self.HooksType["Content"]:
            _a = self.contFuncs
        elif type == self.HooksType["Command"]:
            _a = self.cmdFuncs
        elif type == self.HooksType["SquareEvent"]:
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
            ht = "SquareEvent"
        elif serviceType == 5:
            ht = "Operation"
        else:
            raise ValueError(f"Invalid serviceType: {serviceType}")
        _td = threading.Thread(target=self.trace, args=(event, self.HooksType[ht], cl))
        _td.daemon = True
        _td.start()
