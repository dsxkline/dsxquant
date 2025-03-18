from dsxquant import EventType
from dsxquant.emulation.base import BaseEmulation
from dsxquant import logger
class SellEmulation(BaseEmulation):
    __title__ = "卖出仿真"
    __desc__ = "描述"
    __type__ = EventType.SELL

    def execute(self):
        datas = self.data
        #logger.info("仿真交易卖出%s %s"%(datas,self.event.timestamp))
        # 生成订单
        name,symbol,market,price,amount,date,norisk,desc = datas
        success = self.orders.insert(name,symbol,market,price,amount,date,self.__type__,norisk,desc)
        return success