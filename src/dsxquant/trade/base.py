from dsxquant import EventType
from dsxquant.engins.event_model import EventModel


class BaseTrade:
    # 定义自己处理的类型
    __type__:EventType = EventType.NONE
    __title__ = "交易名称"
    __desc__ = "描述"

    def __init__(self,event:EventModel) -> None:
        self.event:EventModel = event
        # 最好有包装类
        self.data = self.event.data
        
        pass

    def execute(self):
        pass