class PriceDoesNotExist(Exception):

    def __init__(self):
        self.error = "您选择的价格策略不存在！！！"


class CommonException(Exception):
    def __init__(self,error,code=1100):
        self.error=error
        self.code=code