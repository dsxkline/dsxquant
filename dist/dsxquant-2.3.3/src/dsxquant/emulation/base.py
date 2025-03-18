from dsxquant import EventType
from dsxquant.engins.event_model import EventModel
from dsxquant.orders.orders import Orders

class BaseEmulation:
    # 定义自己处理的类型
    __type__:EventType = EventType.NONE
    __title__ = "仿真交易名称"
    __desc__ = "描述"

    def __init__(self,event:EventModel) -> None:
        self.event:EventModel = event
        # 订单数据 name,symbol,market,price,amount,date,norisk
        self.data = self.event.data
        # 订单管理
        self.orders:Orders = Orders(self.event.source,self.event.source.symbol,self.data[6])
        pass

    def execute(self):
        pass