# -*- coding: utf-8 -*-

class HookUtility(object):

    def __init__(self):
        pass

    def checkCmd(self, **kwargs):
        print(f'[checkCmd] {kwargs}')
        return True

    def getPrefix(self, text: str):
        for x in self.prefixes:
            if text.startswith(x):
                return x
        return None

    def genHelp(self, prefix: str = None, user_mid: str = None, msg: any = None):
        '''[C:] Make help by functions'''
        if prefix is None:
            prefix = self.prefixes[0]
        # Make CmdList
        ls = [[x.__name__.replace("_", " "), x.__doc__, x.prefixes,
               x.permissions, x.toType] for x in self.cmdFuncs]
        ls = [l for l in ls if l[1] != None]
        if user_mid is not None:
            ls = [l for l in ls if self.checkPermissions(user_mid, l[3])]
        if msg is not None:
            toType = self.cl.checkAndGetValue(msg, 'toType', 3)
            ls = [l for l in ls if toType in l[4]]
        # Put Prefix
        ls2 = [[prefix+l[0], l[1]] if l[2] else [l[0], l[1]] for l in ls]
        text = '指令表如下:'
        for _cmd in ls2:
            text += f"\n{_cmd[0]}: {_cmd[1]}"
        return text

    def checkPermissions(self, mid: str, permissions: list, excludePermissions: list = []):
        if len(permissions) == 0:
            return True
        for permission in permissions:
            _p = self.getPermission(permission)
            if mid in _p:
                return True
        return False

    def getPermission(self, permission: str):
        return self.db.getData(str(permission).lower(), [])

    def addPermission(self, mid: str, permission: str):
        _k = str(permission).lower()
        _p = self.db.getData(_k, [])
        if mid not in _p:
            _p.append(mid)
            self.db.saveData(_k, _p)
            return True
        return False

    def removePermission(self, mid: str, permission: str):
        _k = str(permission).lower()
        _p = self.db.getData(_k, [])
        if mid in _p:
            _p.remove(mid)
            self.db.saveData(_k, _p)
            return True
        return False

    def getArgs(self, text: str, splitchar: str = ":", defVal: any = None, maxSplit: int = -1):
        args = text.split(splitchar, maxSplit)
        if len(args) > 1:
            return args[1:]
        if defVal is not None:
            return [defVal]
        return None
