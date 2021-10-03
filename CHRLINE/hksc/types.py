from functools import wraps
import traceback,json
import re

class HookTypes(object):

    def Event(self, func):
        setattr(self.eventFuncs, func.__name__, func)
        return func

    def Operation(self, type: int):
        def __wrapper(func):
            @wraps(func)
            def __check(self, *args):
                op = args[0]
                if op[3] == type:
                    func(self, args[0], args[1])
                    return True
                return False
            self.opFuncs.append(__check)
        return __wrapper

    def Content(self, type: int):
        def __wrapper(func):
            @wraps(func)
            def __check(self, *args):
                op = args[0]
                if op[15] == type:
                    func(self, args[0], args[1])
                    return True
                return False
            self.contFuncs.append(__check)
        return __wrapper

    def Command(self, permissions: list = [], alt: list = [], toType: list=[0, 1, 2], ignoreCase: bool = False, inpart: bool = False, prefixes: bool = True):
        def __wrapper(func):
            func.prefixes = prefixes
            @wraps(func)
            def __check(self, *args):
                _fname = lambda _name = None: func.__name__ if _name is None else _name
                msg = args[0]
                sender = msg[1]
                if not self.checkPermissions(sender, permissions):
                    return False
                msgToType = msg[3]
                msgType = msg[15]
                if msgToType in toType:
                    if msgType == 0:
                        text = msg.get(10)
                        for __name in [None] + alt:
                            fname = _fname(__name)
                            if ignoreCase:
                                text = text.lower()
                                fname = fname.lower()
                            isUsePrefixes = not prefixes
                            if text is None:
                                # TODO: E2EE Message
                                return False
                            if prefixes and len(self.prefixes) > 0:
                                for _prefix in self.prefixes:
                                    if text.startswith(_prefix):
                                        fname = _prefix + fname
                                        isUsePrefixes = True
                                        break
                                if not isUsePrefixes:
                                    return False
                            if text == fname or inpart and text.startswith(fname):
                                func(self, args[0], args[1])
                                return True
                    else:
                        raise ValueError(f'wrong content type: {msgType}')
                return False
            self.cmdFuncs.append(__check)
        return __wrapper

    def Before(self, type: int):
        def __wrapper(func):
            func.type = type
            @wraps(func)
            def __bf(self, *args, **kwargs):
                func(self, args[0], args[1])
                return True
            self.beforeFuncs.append(__bf)
        return __wrapper

    def After(self,type):
        def __wrapper(func):
            func.type = type
            @wraps(func)
            def __af(self, *args, **kwargs):
                func(self, args[0], args[1])
                return True
            self.afterFuncs.append(__af)
        return __wrapper