# -*- coding: utf-8 -*-

class HookUtility(object):

    def __init__(self):
        pass

    def getPrefix(self, text: str):
        for x in self.prefixes:
            if text.startswith(x):
                return x
        return None

    def genHelp(self, prefix: str = None):
        '''[C:] Make help by functions'''
        if prefix is None:
            prefix = self.prefixes[0]
        # Make CmdList
        ls  = [[x.__name__.replace("_"," "), x.__doc__, x.prefixes] for x in self.cmdFuncs]
        ls  = [l for l in ls if l[1] != None]
        # Put Prefix
        ls2 = [[prefix+l[0],l[1]] if l[2] else [l[0],l[1]] for l in ls]
        text = '指令表如下:'
        for _cmd in ls2:
            text += f"\n{_cmd[0]}: {_cmd[1]}"
        return text

    def checkPermissions(self, mid: str, permissions: list, excludePermissions: list = []):
        if len(permissions) == 0:
            return True
        for permission in permissions:
            _p = self.db.getData(str(permission).lower(), [])
            if mid in _p:
                return True
        return False

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