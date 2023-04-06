from typing import List
import threading
from dsxquant.engins.event_model import EventModel
from dsxquant import logger
from dsxquant import EventType

class BaseEngin:
    __name__ = "引擎基类"
    __interface_execute = "execute"
    def __init__(self,event_types:List[EventType]=None):
      self.exit = False
      self.events:List[EventModel] = []
      self.event:EventModel = None
      self.event_type:List[EventType] = event_types
      self.event_bus = None
    
    def receive(self,event:EventModel):
        """接收事件总线的事件

        Args:
            event (EventModel): _description_
        """
        if self.event_type:
            if event.type not in self.event_type:
                return
        if event.bus:self.event_bus = event.bus
        self.events.append(event)
    
    
    def sendbus(self,event:EventModel):
        """反馈信号
        给总线反馈处理结果，以事件的形式反馈
        """
        if event:
            bus = event.bus
            if bus:
                bus.register(event)

    def sendevent(self,event_type:EventType,data,target=None,cursor=0,source=None):
        if self.event_bus:
            event = EventModel(self.event.bus,event_type,data,target,cursor,source)
            self.sendbus(event)
        else:
            logger.warning("event bus not available")
    
    def get_current_event(self):
        if self.events.__len__()>0:
            self.event = self.events[0]
            return self.event

    def destroy(self):
        if self.events.__len__()>0:
            if self.event in self.events:
                self.events.remove(self.event)
        self.event = None
    
    def start(self):
        """启动
        """
        threading.Thread(target=self.run).start()
        logger.info("%s 引擎已启动...." % self.__name__)
        return self

    def run(self):
        pass

    def on_finished(self):
        """执行完成
        """
        pass

    def next(self):
        self.get_current_event()
        pass

    def shutdown(self):
        """关闭引擎
        """
        self.exit = True