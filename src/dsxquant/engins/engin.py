"""主引擎负责系统启动，管理事件总线，热插拔插件等
"""
from dsxquant import logger,EventType
import threading
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel


class Engin:
    def __init__(self) -> None:
        self.event_bus:EventBus = None
        self.exit = False
        pass

    def _start_event_bus(self):
        """启动事件总线
        """
        self.event_bus = EventBus()
    
    def install(self,*args):
        """安装插件
        """
        for item in args:
            self.event_bus.install(item)
    
    def sendbus(self,type:EventType,data):
        """系统也可以扔事件给总线
        """
        event = EventModel(self.event_bus,type,data,self)
        self.event_bus.register(event)

    def start(self):
        """启动引擎
        """
        # 启动系统
        threading.Thread(target=self.run).start()
        # 启动事件总线
        self._start_event_bus()
        
        logger.info("系统引擎启动...")
    
    def shutdown(self):
        """关闭引擎
        """
        if self.event_bus:self.event_bus.shutdown()
        self.exit = True


    def run(self):
        while(not self.exit):

            pass
    
