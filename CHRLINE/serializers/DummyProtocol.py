

class DummyProtocolData():

    def __init__(self, id, type, data, subType: list = None):
        self.id = id
        self.type = type
        self.data = data
        self.subType = []
        if subType is not None:
            for _subType in subType:
                self.addSubType(_subType)

    def addSubType(self, type):
        self.subType.append(type)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

class DummyProtocol():

    def __init__(self, type: int=5, data: DummyProtocolData= None):
        self.type = 5
        self.data = data
    
    def dump(self):
        data = b''
        data += bytes([130, 33, 0, 0])
        return data

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

class DummyThrift():

    def __init__(self, name: str = None, **kwargs):
        if name is not None:
            self.__name__ = name
        if kwargs:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))