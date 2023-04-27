from dsxquant import EventType
from dsxquant import logger
from dsxquant.trade.base import BaseTrade
class Cancel(BaseTrade):
    __title__ = "撤单"
    __desc__ = "描述"
    __type__ = EventType.CANCEL

    def execute(self):
        datas = self.data
        logger.info("交易撤单%s %s"%(datas,self.event.timestamp))