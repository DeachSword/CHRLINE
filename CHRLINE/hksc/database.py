# -*- coding: utf-8 -*-
import json
# import sqlite

class BaseDatabase:

    def __init__(self, cl, db_name):
        self.cl = cl
        if db_name is None:
            db_name = self.cl.mid
        self.db_name = db_name
        print("Initialize database...")
        self.loadDatabase()

class SqliteDatabase(BaseDatabase):

    def loadDatabase(self):
        print(f"Loading db_{self.db_name} with Sqli")
        raise Exception("Not implemented yet.")

class JsonDatabase(BaseDatabase):

    def loadDatabase(self):
        print(f"Loading db_{self.db_name} with Json")
        _data = self.cl.getCacheData(".database", f"{self.db_name}.json")
        self._json = json.loads(_data) if _data is not None and _data != '' else {}

    def getData(self, _key, _defVal=None):
        return self._json.get(_key, _defVal)

    def saveData(self, _key, _val):
        self._json[_key] = _val
        self.saveDatabase()

    def saveDatabase(self):
        self.cl.saveCacheData(".database", f"{self.db_name}.json", json.dumps(self._json))
        print(f"Save db_{self.db_name} with Json success")
