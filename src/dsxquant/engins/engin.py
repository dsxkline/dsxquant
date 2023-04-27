"""主引擎负责系统启动，管理事件总线，热插拔插件等
"""
from dsxquant import logger,EventType
import threading
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant.engins.cache_space import CacheSpace


class Engin:
    _instance = None
    # 系统安装的应用列表
    _apps = {}
    # 缓存空间
    cachespace = CacheSpace()

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        return Engin._instance
    
    def __init__(self) -> None:
        self.event_bus:EventBus = None
        self.exit = False
        pass

    def _start_event_bus(self):
        """启动事件总线
        """
        self.event_bus = EventBus()
        self._apps[EventBus] = self.event_bus
    
    def install(self,*args):
        """安装插件
        """
        for item in args:
            if type(item)==type: item = item()
            self.event_bus.install(item)
            self._apps[item.__class__] = item
            if hasattr(item,"start"):
                # 启动引擎
                start = getattr(item,"start")
                start()
    
    def get_app(self,cls):
        if cls in self._apps.keys():
            return self._apps.get(cls)
    
    def sendbus(self,type:EventType,data):
        """系统也可以扔事件给总线
        """
        event = EventModel(self.event_bus,type,data,self)
        self.event_bus.register(event)

    def start(self):
        """启动引擎
        """
         # 启动事件总线
        self._start_event_bus()
        # 启动系统
        threading.Thread(target=self.run).start()
        logger.info("系统引擎启动...")
        return self
    
    def shutdown(self):
        """关闭引擎
        """
        if self.event_bus:self.event_bus.shutdown()
        self.exit = True
        logger.debug("主引擎关闭")

    def run(self):
        pass
    
