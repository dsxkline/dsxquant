from dsxquant import EventType
from dsxquant import logger
from dsxquant.trade.base import BaseTrade

class Buy(BaseTrade):
    __title__ = "买入"
    __desc__ = "描述"
    __type__ = EventType.BUY

    def execute(self):
        datas = self.data
        logger.info("交易买入%s %s"%(datas,self.event.timestamp))