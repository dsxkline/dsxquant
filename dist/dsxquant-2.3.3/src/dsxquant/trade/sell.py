from dsxquant import EventType
from dsxquant import logger
from dsxquant.trade.base import BaseTrade
class Sell(BaseTrade):
    __title__ = "卖出"
    __desc__ = "描述"
    __type__ = EventType.SELL

    def execute(self):
        datas = self.data
        logger.info("交易卖出%s %s"%(datas,self.event.timestamp))