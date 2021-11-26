# -- coding utf-8 --

class SearchService(object):

    def __init__(self):
        pass

    def searchAll(self):
        params = []
        sqrd = self.generateDummyProtocol('searchAll', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def searchCollection(self):
        params = []
        sqrd = self.generateDummyProtocol('searchCollection', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def searchLineat(self):
        params = []
        sqrd = self.generateDummyProtocol('searchLineat', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def searchByPopularCategory(self):
        params = []
        sqrd = self.generateDummyProtocol('searchByPopularCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def searchByCategory(self):
        params = []
        sqrd = self.generateDummyProtocol('searchByCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def getPopularCategory(self):
        params = []
        sqrd = self.generateDummyProtocol('getPopularCategory', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def getNotice(self):
        params = []
        sqrd = self.generateDummyProtocol('getNotice', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def getSearchSection(self):
        params = []
        sqrd = self.generateDummyProtocol('getSearchSection', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def getAutocomplete(self):
        params = []
        sqrd = self.generateDummyProtocol('getAutocomplete', params, 4)
        return self.postPackDataAndGetUnpackRespData("/search/v3", sqrd, 4)

    def searchAll(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchAll is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchAll", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def searchInContext(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchInContext is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchInContext", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def getPopularCategory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularCategory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularCategory", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def getAutocomplete(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAutocomplete is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getAutocomplete", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def searchByPopularCategory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchByPopularCategory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchByPopularCategory", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def searchByCategory(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchByCategory is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchByCategory", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def searchLineat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchLineat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchLineat", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def getNotice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNotice is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNotice", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def getSearchSection(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSearchSection is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getSearchSection", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)

    def searchCollection(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("searchCollection is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "searchCollection", params, SearchService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(SearchService_API_PATH, sqrd, SearchService_RES_TYPE)
