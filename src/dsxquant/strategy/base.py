from dsxquant import EventType,config,EventModel,EmulationEngin,TradeEngin
from dsxquant.strategy.data_model import DataModel
from dsxindexer.sindexer.models.kline_model import KlineModel
from progressbar import ProgressBar

class BaseStrategy:
    # 定义自己处理的类型
    __type__:EventType = EventType.NONE
    __title__ = "策略名称"
    __desc__ = "描述"

    def __init__(self,event:EventModel) -> None:
        # 事件
        self.event:EventModel = event
        # 策略标的，支持多只股票代码
        self.symbols:list = []
        # 代码
        self.symbol:str = None
        self.market:int = None
        # 实盘
        self.real = False
        # 最好有包装类
        self.data_model:DataModel = None
        self.kline:KlineModel = None
        self.cursor = 0
        self.pbar = ProgressBar()
        self.pbar.start()
        self.init()
    
    def load(self,event:EventModel):
        # 事件
        self.event:EventModel = event
        self.cursor = self.event.cursor
        if self.event.data:
            symbol,market,datas = self.event.data
            self.symbol = symbol
            self.market = market
            if isinstance(datas,list):
                if self.cursor < datas.__len__():
                    self.data_model = DataModel(symbol,datas,self.cursor,self.formula())
                    self.kline = self.data_model.data

                progress = self.cursor/datas.__len__() * 100
                self.pbar.update(progress)

    def init(self):
        """初始化
        """
        pass
    
    def formula(self):
        pass

    

    def __create_signal(self,data,etype:EventType):
        """生成总线事件

        Args:
            data (any): 数据
            type (EventType): 事件类型

        Returns:
            EventModel: 总线事件
        """
        target = self.real and TradeEngin or EmulationEngin
        event_sinal = EventModel(self.event.bus,etype,data,target=EmulationEngin,source=self)
        return event_sinal
    
    def buy(self,name,symbol:str,market:int,amount:int,price:float,date:str):
        """策略买入信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,price,amount,date)
        return self.__create_signal(data,EventType.BUY)
    
    def sell(self,name,symbol:str,market:int,amount:int,price:float,date:str):
        """策略卖出信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,price,amount,date)
        return self.__create_signal(data,EventType.SELL)
    
    def cancel(self,name,symbol:str,market:int,amount:int,date:str):
        """策略撤单信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,0,amount,date)
        return self.__create_signal(data,EventType.CANCEL)

    def execute(self):
        pass