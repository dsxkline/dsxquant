import threading
from typing import List
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant import EventType
from dsxquant import logger
from dsxquant import StrategyEngin

class BackTest:
    def __init__(self,strategy_engin:StrategyEngin=None,event_types:List[EventType]=None):
        self.exit = False
        self.event_types:List[EventType] = event_types
        self.events:List[EventModel] = []
        self.event:EventModel = None
        self.strategy_engin:StrategyEngin = strategy_engin
    
    def receive(self,event:EventModel):
        """接收事件总线的事件

        Args:
            event (EventModel): _description_
        """
        if self.event_types:
            if event.type not in self.event_types:
                return
            # logger.debug("接收事件 %s" % event)
        self.events.append(event)
    
    def get_current_event(self):
        if self.events.__len__()>0:
            self.event = self.events[0]
            return self.event
        
    def start(self):
        """启动回测
        """
        threading.Thread(target=self.run).start()
        logger.info("启动回测....")

    def destroy(self):
        if self.events.__len__()>0:
            if self.event in self.events:
                self.events.remove(self.event)
        self.event = None

    def run(self):
        while not self.exit:
            if self.event:
                self.on_dayline()
            self.destroy()
            self.next()
    
    def close(self):
        """接收回测
        """
        logger.info("回测结束")
        self.destroy()

    def on_dayline(self):
        """处理日线数据集事件
        """
        if self.event.type==EventType.DAYLINE and self.event.target==self.__class__:
            data = self.event.data
            symbol,market,datas = data
            event_bus:EventBus = self.event.bus
            for i in range(len(datas)):
                event = EventModel(event_bus,EventType.DAYBAR,data,StrategyEngin,i)
                # 直接给策略引擎发消息
                self.sendevent(event)
    
    def sendevent(self,event:EventModel):
        """给策略引擎发送事件

        Args:
            event (EventModel): _description_
        """
        if self.strategy_engin and event:
            self.strategy_engin.receive(event)
    
    def next(self):
        self.get_current_event()
        pass
    