"""事件总线
事件总线需要提供标准事件收发协议，事件处理接口，热插拔接口
"""
import threading
import time
from dsxquant.engins.event_model import EventModel
from dsxquant import logger,EventType

class EventBus:
    # 插件的接收接口
    __plugin_interface = "receive"
    # 插件的卸载接口
    __plugin_shutdown = "shutdown"

    def __init__(self) -> None:
        self.exit = False
        self.events = []
        self.plugins = []
        self.current_event:EventModel = EventModel()
        self.lock = threading.Lock()
        threading.Thread(target=self.run).start()
        pass

    def install(self,plugin):
        """安装插件

        Args:
            plugin (_type_): _description_
        """
        self.plugins.append(plugin)
        self.send_event_to_plugin(plugin,EventModel(self,target=plugin.__class__))
        # logger.info("%s plugin is installed" % plugin)

    def uninstall(self,plugin):
        """卸载插件

        Args:
            plugin (_type_): _description_
        """
        if plugin in self.plugins:
            self.plugins.remove(plugin)
            logger.info("%s plugin is uninstalled" % plugin)

    def register(self,model:EventModel):
        """向总线注册事件
        意思是给总线仍一个事件

        Args:
            model (EventModel): _description_
        """
        self.events.append(model)
        # logger.info("%s event is registed" % model.type)
    
    def unregister(self,model:EventModel):
        """向总线卸载一个事件
        Args:
            model (EventModel): _description_
        """
        if model in self.events:
            self.events.remove(model)
            # logger.info("%s event is unregisted" % model.type)
    
    def get_last_event():
        pass
    
    def next_event(self):
        with self.lock:
            if self.events.__len__()>0:
                self.current_event = self.events[0]

    def destroy(self):
        """销毁事件
        """
        with self.lock:
            if self.current_event:
                if self.current_event.count<=0:
                    if self.current_event in self.events:
                        self.events.remove(self.current_event)
                self.current_event = None
    
    def shutdown(self):
        """关闭总线
        """
        self.exit = True
        # 卸载插件
        for plugin in self.plugins:
            if hasattr(plugin,self.__plugin_shutdown):
                shutdown = getattr(plugin,self.__plugin_shutdown)
                shutdown()
        
        logger.debug("总线关闭")
    
    def send_event_to_plugin(self,plugin,event:EventModel):
        """给插件发送事件

        Args:
            plugin (_type_): _description_
            event (EventModel): _description_
        """
        # 插件接收事件
        if event and plugin:
            if hasattr(plugin,self.__plugin_interface):
                receive = getattr(plugin,self.__plugin_interface)
                if callable(receive):
                    # 引用次数加1
                    # self.current_event.count += 1
                    event.bus = self
                    receive(event)

    def run(self):
        """运行总线线程
        """
        while(not self.exit):
            if self.plugins:
                # 分发事件
                # 每个插件必须实现事件接收
                if self.current_event:
                    with self.lock:
                        for plugin in self.plugins:
                            self.send_event_to_plugin(plugin,self.current_event)
                    # if self.current_event.type==EventType.THEEND:
                    #     # 结束回测
                    #     break 
                # 销毁
                self.destroy()
                # 下一个事件
                self.next_event()
