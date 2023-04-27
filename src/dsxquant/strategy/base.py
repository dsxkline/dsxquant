from dsxquant import EventType,config,EventModel,EmulationEngin,TradeEngin,MARKET
from dsxquant.strategy.data_model import DataModel
from dsxindexer.sindexer.models.kline_model import KlineModel
from progressbar import ProgressBar
import dsxquant
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
        # 市场
        self.market:MARKET = None
        # 基准收益率
        self.norisk = 0
        # 实盘
        self.real = False
        # 数据及指标模型
        self.data_model:DataModel = None
        # k线模型
        self.kline:KlineModel = None
        # 游标
        self.cursor = 0
        # 订单
        self.order = None
        # 资金,会从订单里读取
        self.funds = 0
        # 初始资金
        self.init_funds = 0
        # 止盈
        self.take_profit = 0
        # 止损
        self.stop_loss = 0
        # 进度条
        self.pbar = ProgressBar()
        self.pbar.start()
        self.init()
    
    def load(self,event:EventModel):
        # 事件
        self.event:EventModel = event
        self.cursor = self.event.cursor
        if self.event.data:
            symbol,market,datas,norisk = self.event.data
            self.symbol = symbol
            self.market = market
            self.norisk = norisk
            self.order = dsxquant.Orders(self.event.source,self.symbol,self.norisk)
            if isinstance(datas,list):
                if self.cursor < datas.__len__():
                    self.data_model = DataModel(symbol,datas,self.cursor,self.formula())
                    self.kline = self.data_model.data

        progress = (self.cursor+1)/(datas.__len__()) * 100
        # print("%s=%s" % (self.cursor,progress))
        self.pbar.update(progress)
        if progress>=100: self.pbar.finish()

    def init(self):
        """初始化
        """
        pass
    
    def formula(self):
        pass

    def stop(self,order:tuple):
        """止盈止损
        """
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
        event_sinal = EventModel(self.event.bus,etype,data,target=target,source=self.event.source)
        if self.event:
            if self.event.bus:
                self.event.bus.register(event_sinal)
                while(not event_sinal.status):
                    pass
        return event_sinal
    
    def buy(self,name,symbol:str,market:int,amount:int,price:float,date:str,desc="买点"):
        """策略买入信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,price,amount,date,self.norisk,desc)
        return self.__create_signal(data,EventType.BUY)
    
    def sell(self,name,symbol:str,market:int,amount:int,price:float,date:str,desc="卖点"):
        """策略卖出信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量
            price (_type_): 价格

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,price,amount,date,self.norisk,desc)
        return self.__create_signal(data,EventType.SELL)
    
    def cancel(self,name,symbol:str,market:int,amount:int,date:str,desc="撤销"):
        """策略撤单信号

        Args:
            symbol (_type_): 代码
            market (_type_): 市场编号
            amount (_type_): 数量

        Returns:
            EventModel: 总线事件
        """
        data = (name,symbol,market,0,amount,date,self.norisk,desc)
        return self.__create_signal(data,EventType.CANCEL)

    def execute_all(self,event:EventModel):
        self.stop_execute()
        self.execute()
        event.success()

    def execute(self):
        pass

    def snapshot(self):
        """更新每日收益快照"""

    def stop_execute(self):
        """执行止盈止损策略
        """
        self.funds = self.order.funds
        self.init_funds = self.order.init_funds

        # 每笔交易止盈
        buyorder = self.order.buy_orders
        if buyorder:
            for item in buyorder:
                self.stop((item[1],item[2],item[3],item[4],item[5]))

