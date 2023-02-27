from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CHRLINE import CHRLINE


class BaseService:
    def __init__(self):
        pass


class BaseServiceStruct:
    @staticmethod
    def BaseRequest(request: list):
        return [[12, 1, request]]

    @staticmethod
    def SendRequestByName():
        raise NotImplementedError


class BaseServiceHandler:
    def __init__(self, client: "CHRLINE") -> None:
        self.cl = client
