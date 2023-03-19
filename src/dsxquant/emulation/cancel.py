from dsxquant import EventType
from dsxquant.emulation.base import BaseEmulation
from dsxquant import logger
class CancelEmulation(BaseEmulation):
    __title__ = "撤单仿真"
    __desc__ = "描述"
    __type__ = EventType.CANCEL

    def execute(self):
        datas = self.data
        #logger.info("仿真交易撤单%s %s"%(datas,self.event.timestamp))