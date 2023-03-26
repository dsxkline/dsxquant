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
        # 基准收益率
        self.norisk = 0
        # 实盘
        self.real = False
        # 最好有包装类
        self.data_model:DataModel = None
        self.kline:KlineModel = None
        # 游标
        self.cursor = 0
        # 订单
        self.order = None
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
            from dsxquant import Orders
            self.order = Orders(self.event.source,self.symbol,self.norisk)
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

    def stop(self):
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
        event_sinal = EventModel(self.event.bus,etype,data,target=EmulationEngin,source=self.event.source)
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
        self.stop()
        # 每笔交易止盈
        buyorder = self.order.buy_orders
        if buyorder:
            price = self.kline.CLOSE
            date = self.kline.DATE
            for item in buyorder:
                name = item[1]
                symbol = item[2]
                market = item[3]
                buy_price = item[4]
                amount = item[5]
                rate = (price - buy_price) / buy_price
                if rate>=self.take_profit and self.take_profit!=0:
                    # 止盈卖出
                    self.sell(name,symbol,market,amount,price,date,"止盈卖出")
                
                if rate<=self.stop_loss and self.stop_loss!=0:
                    # 止损卖出
                    self.sell(name,symbol,market,amount,price,date,"止损卖出")

