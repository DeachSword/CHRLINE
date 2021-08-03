# -- coding utf-8 --

class ShopAuthService(object)
    
    def __init__(self)
        pass
    
    def establishE2EESession(self)
        params = []
        sqrd = self.generateDummyProtocol('establishE2EESession', params, 4)
        return self.postPackDataAndGetUnpackRespData("/SHOPA" ,sqrd, 4)