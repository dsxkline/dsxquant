from pandas import DataFrame
from dsxquant import EventModel
from dsxquant import EventType,config
from dsxquant.strategy.data_model import DataModel
from dsxindexer.sindexer.models.kline_model import KlineModel
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
        # 最好有包装类
        self.data_model:DataModel = None
        self.data:KlineModel = None
        self.cursor = 0
        
        self.__init()
    
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
                    self.data_model = DataModel(datas,self.cursor,self.formula())
                    self.data = self.data_model.data

    def __init(self):
        """初始化
        """
        pass
    
    def formula(self):
        pass

    def __load_datas(self,event):
        # 直接给总线推送事件，Datafeed收到后会主动加载数据并传送过来
        self.event.bus.register(event)

    def load_dayline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY):
        return self.load_barline(page,page_size,fq,cycle)
    def load_weekline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.WEEK):
        return self.load_barline(page,page_size,fq,cycle)
    def load_monthline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.MONTH):
        return self.load_barline(page,page_size,fq,cycle)
    def load_yearline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.YEAR):
        return self.load_barline(page,page_size,fq,cycle)
    def load_minline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M1):
        return self.load_barline(page,page_size,fq,cycle)
     
    def load_barline(self,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY):
        """加载蜡烛图数据

        Args:
            page (int, optional): _description_. Defaults to 1.
            page_size (int, optional): _description_. Defaults to 320.
            fq (str, optional): 复权. Defaults to config.FQ.DEFAULT.
            cycle (config.CYCLE, optional): 周期. Defaults to config.CYCLE.DAY.
        """
        if self.symbols:
            for item in self.symbols:
                symbol,market = item
                data = (symbol,market,page,page_size,fq,cycle)
                # 指定给datafeed引擎处理
                from dsxquant import DataFeed
                etype = EventType.DAYLINE
                if cycle==config.CYCLE.WEEK:etype=EventType.WEEKLINE
                if cycle==config.CYCLE.MONTH:etype=EventType.MONTHLINE
                if cycle==config.CYCLE.YEAR:etype=EventType.YEARLINE
                if cycle==config.CYCLE.M1:etype=EventType.MINLINE
                event = EventModel(self.event.bus,etype,data,DataFeed)
                self.__load_datas(event)
    
    def __create_signal(self,data,etype:EventType):
        """生成总线事件

        Args:
            data (any): 数据
            type (EventType): 事件类型

        Returns:
            EventModel: 总线事件
        """
        event_sinal = EventModel(self.event.bus,etype,data,self)
        return event_sinal
    
    def buy(self,symbol:str,market:int,amount:int,price:float):
        """策略买入信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (symbol,market,amount,price)
        return self.__create_signal(data,EventType.BUY)
    
    def sell(self,symbol:str,market:int,amount:int,price:float):
        """策略卖出信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (symbol,market,amount,price)
        return self.__create_signal(data,EventType.SELL)
    
    def cancel(self,symbol:str,market:int,amount:int):
        """策略撤单信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量

        Returns:
            EventModel: 总线事件
        """
        data = (symbol,market,amount)
        return self.__create_signal(data,EventType.CANCEL)

    def execute(self):
        pass