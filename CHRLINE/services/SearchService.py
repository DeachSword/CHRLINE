# -- coding utf-8 --

class SearchService(object)
    
    def __init__(self)
        pass
    
    def searchAll(self)
        params = []
        sqrd = self.generateDummyProtocol('searchAll', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def searchCollection(self)
        params = []
        sqrd = self.generateDummyProtocol('searchCollection', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def searchLineat(self)
        params = []
        sqrd = self.generateDummyProtocol('searchLineat', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def searchByPopularCategory(self)
        params = []
        sqrd = self.generateDummyProtocol('searchByPopularCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def searchByCategory(self)
        params = []
        sqrd = self.generateDummyProtocol('searchByCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def getPopularCategory(self)
        params = []
        sqrd = self.generateDummyProtocol('getPopularCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def getNotice(self)
        params = []
        sqrd = self.generateDummyProtocol('getNotice', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def getSearchSection(self)
        params = []
        sqrd = self.generateDummyProtocol('getSearchSection', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)

    def getAutocomplete(self)
        params = []
        sqrd = self.generateDummyProtocol('getAutocomplete', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3" ,sqrd, 4)