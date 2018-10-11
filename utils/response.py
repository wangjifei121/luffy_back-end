class BaseResponse:

    def __init__(self):
        self.code = 1000
        self.data = ""
        self.error = ""

    @property
    def dict(self):
        return self.__dict__
