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
                if op[3] in [25, 26]:
                    op[20]['opType'] = op[3]
                    op[20]['isE2EE'] = False
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

    def Command(self, permissions: list = [], alt: list = [], toType: list=[0, 1, 2], ignoreCase: bool = False, inpart: bool = False, prefixes: bool = True, splitchar: str=None):
        """
        - permissions:
            List of permission's name.
            eg. ['admin']
        - alt:
            Sub cmds.
            eg: Command name is "GetOps", and use alt=["ops"], so u can use "GetOps" and "ops" to run the command.
        - toType:
            Only run when receives the command with the specific toType 
        - ignoreCase:
            *As the name suggests*
        - inpart:
            If False, match the command that same style.
            If True, match any command that starts with command name.
        - prefixes:
            Match the prefixs.
        - splitchar:
            If not None, match the first value after the command is split by this value
        """
        def __wrapper(func):
            func.prefixes = prefixes
            @wraps(func)
            def __check(self, *args):
                _fname = lambda _name = None: func.__name__ if _name is None else _name
                msg = args[0]
                sender = msg[1]
                receiver = msg[2]
                cl = args[1]
                if sender != cl.mid and not self.checkPermissions(sender, permissions):
                    return False
                msgToType = msg[3]
                msgType = msg[15]
                isInpart = inpart
                if msgToType in toType:
                    if msgType == 0:
                        text = msg.get(10)
                        for __name in [None] + alt:
                            fname = _fname(__name)
                            if text is None:
                                # TODO: E2EE Message
                                msg['isE2EE'] = True
                                text = cl.decryptE2EETextMessage(msg, msg.get('opType', 26) == 25)
                                msg[10] = text # maybe fixed in Operation__check?
                            if ignoreCase:
                                text = text.lower()
                                fname = fname.lower()
                            if splitchar is not None:
                                text = text.split(splitchar)[0]
                                isInpart = False # force
                            isUsePrefixes = not prefixes
                            if prefixes and len(self.prefixes) > 0:
                                for _prefix in self.prefixes:
                                    if text.startswith(_prefix):
                                        fname = _prefix + fname
                                        isUsePrefixes = True
                                        break
                                if not isUsePrefixes:
                                    return False
                            if text == fname or isInpart and text.startswith(fname):
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