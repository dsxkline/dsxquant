from dsxquant.engins.base import BaseEngin
import dsxquant
from dsxquant import config,logger,EventModel
from dsxquant.config.config import EventType

class DataFeed(BaseEngin):
    __name__ = "数据响应"
    __interface_execute = "execute"

    def __init__(self):
        super().__init__()
    
    def run(self):
        while(not self.exit):
            if self.event and self.event.target==self.__class__:
                if self.event.type==EventType.DAYLINE:
                    args = tuple(self.event.data)
                    self.dayline(*args)
            if self.event:
                if self.event.type==EventType.THEEND:
                        # 结束回测
                        break
            # 处理后销毁
            self.destroy()
            self.next()
    
    def dayline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY):
        try:
            result = dsxquant.get_klines(symbol,market,page,page_size,fq,cycle).datas()
            if result.success:
                data:list = result.data
                data.reverse()
                data = (symbol,market,data)
                logger.debug("send dataevent to BackTest...")
                self.sendevent(EventType.DAYLINE,data,dsxquant.BackTest,source=self.event.source)
        except Exception as e:
            logger.error(e)


    
   