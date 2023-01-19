class DummyProtocolData:
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
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))


class DummyProtocol:
    def __init__(self, protocol: int = 5, data: DummyProtocolData = None):
        self.protocol = protocol
        self.data = data

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))


class DummyThrift:
    def __init__(self, name: str = None, **kwargs):
        if name is not None:
            self.__name__ = name
        if kwargs:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))


class DummyProtocolSerializer:
    def __init__(self, instance: any, name: str, data: list, protocol: int):
        self.instance = instance
        self.name = name
        self.data = data
        self.protocol = protocol

    def __bytes__(self):
        """Convert to proto data."""
        data = []
        instance = self.instance
        protocol = self.protocol
        if protocol == 3:
            data = [128, 1, 0, 1] + instance.getStringBytes(self.name) + [0, 0, 0, 0]
        elif protocol in [4, 5]:
            protocol = 4
            data = [130, 33, 0] + instance.getStringBytes(self.name, isCompact=True)
        else:
            raise ValueError(f"Unknower protocol: {protocol}")
        data += instance.generateDummyProtocolField(self.data, protocol) + [0]
        return bytes(data)

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))
