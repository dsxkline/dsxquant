from dsxquant import EventType
import datetime
class EventModel:
    def __init__(self,bus=None,type:EventType=EventType.NONE,data=None,target=None,cursor=0,source=None,status=False) -> None:
        from dsxquant.engins.event_bus import EventBus
        # 总线地址
        self.bus:EventBus = bus
        # 事件类型
        self.type:EventType = type
        # 事件数据
        self.data = data
        # 事件引用计数
        self.count = 0
        # 目标
        self.target = target
        # 来源
        self.source = source
        # 时间戳
        self.timestamp = datetime.datetime.now()
        # 数据游标
        self.cursor = cursor
        # 事件处理状态
        self.status = status
    
    def success(self):
        self.status = True
    
    def fail(self):
        self.status = False
    
    def copy(self):
        e = EventModel(self.bus,self.type,self.data,self.target,self.cursor,self.source,self.status)
        return e

