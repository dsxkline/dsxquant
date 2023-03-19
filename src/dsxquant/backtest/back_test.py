import threading
import time
from typing import List
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant import EventType
from dsxquant import logger
from dsxquant import StrategyEngin,BaseSymbol,Engin,MARKET,config,FQ
from prettytable import PrettyTable

class BackTest:
    def __init__(self,symbol:str,market:MARKET,start:str,end:str,funds=100000,base_symbol:BaseSymbol=BaseSymbol.HS300,data:EventType=EventType.DAYLINE,fq:FQ=FQ.QFQ):
        """回测

        Args:
            symbol (str): 股票代码
            market (MARKET): 市场
            start (str): 开始日期
            end (str): 结束日期
            funds (int, optional): 初始资金. Defaults to 100000.
            base_symbol (BaseSymbol, optional): 基准指数. Defaults to BaseSymbol.HS300.
            data (EventType, optional): _description_. 数据 to EventType.DAYLINE.
        """
        self.exit = False
        self.events:List[EventModel] = []
        self.event:EventModel = None
        # 回测参数
        # 回测区间 %Y%m%d
        self.start_date = start
        self.end_date = end
        # 资金 默认10万
        self.funds = funds
        # 基准指数 沪深300（sz399300） ，标普500（spx），恒生指数 （hk800000）
        self.base_symbol = base_symbol
        # 标的 示例：000001
        self.symbol = symbol
        self.market = market
        # 复权
        self.fq = fq
        # 数据
        self.data = data


    @property
    def strategy_engin(self) ->StrategyEngin:
        """去系统找
        """
        return Engin.get_instance().get_app(StrategyEngin)

    @property
    def event_bus(self) ->EventBus:
        """去系统找
        """
        return Engin.get_instance().get_app(EventBus)

    
    def receive(self,event:EventModel):
        """接收事件总线的事件

        Args:
            event (EventModel): _description_
        """
        self.events.append(event)
    
    def get_current_event(self):
        if self.events.__len__()>0:
            self.event = self.events[0]
            return self.event
        
    def start(self):
        """启动回测
        """
        threading.Thread(target=self.run).start()
        logger.info("启动[%s]回测...." % self.strategy_engin.strategies[0].__title__)
        self.load_datas()
    
    def show(self):
        """显示回测结果
        """
        while True:
            if self.event:
                if self.event.type==EventType.THEEND:
                    # 结束回测
                    break
            time.sleep(1)
        
        self.on_finished()

    def destroy(self):
        if self.events.__len__()>0:
            if self.event in self.events:
                self.events.remove(self.event)
        self.event = None

    def run(self):
        while not self.exit:
            if self.event:
                self.on_dayline()
                if self.event.type==EventType.THEEND:
                    # 结束回测
                    break
            self.destroy()
            self.next()
    

    
    def close(self):
        """接收回测
        """
        logger.info("回测结束")
        self.destroy()

    def on_dayline(self):
        """处理日线数据集事件
        """
        if self.event.type==EventType.DAYLINE and self.event.target==self.__class__:
            data = self.event.data
            symbol,market,datas = data
            event_bus:EventBus = self.event.bus
            for i in range(len(datas)):
                event = EventModel(event_bus,EventType.DAYBAR,data,StrategyEngin,i,source=self.event.source)
                # 直接给策略引擎发消息
                self.sendevent(event)
            self.sendevent(EventModel(event_bus,EventType.THEEND,target=StrategyEngin,source=self.event.source))
    
    def on_finished(self):
        """回测结束
        """
        from dsxquant import Orders
        order:Orders = list(Orders.order_list.values())[0]
        if order:
            self.base_orders(order.orders)
            self.show_orders(order)

    def show_orders(self,order):
        from dsxquant import Orders
        order:Orders = order
        orders = order.orders.values()
        # # 创建表格对象，并设置表头
        table:PrettyTable = PrettyTable(['订单列表', '股票名称','代码', '市场','价格','股数','平仓日期','类型','开仓日期','卖出价格','卖出股数','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%'])
        table.add_rows(orders)
        print(table)
        table:PrettyTable = PrettyTable(['持仓中', '股票代码', '市场','持仓价格','持仓股数','平仓日期','状态','持仓总股数','开仓日期','平仓价格','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%'])
        table.add_rows(order.positions.values())
        print(table)
        table:PrettyTable = PrettyTable(['历史持仓', '股票代码', '市场','持仓价格','持仓股数','平仓日期','状态','持仓总股数','开仓日期','平仓价格','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%'])
        table.add_rows(order.positions_closed)
        print(table)

        table:PrettyTable = PrettyTable(['持有天数', '年化收益率%','夏普比率%', '盈亏比%','胜率%','最大回撤%','最大收益率%','最小收益率%'])
        table.add_rows(order.records)
        print(table)
    
    @property
    def engin_cache(self):
        return Engin.get_instance().cachespace

    def base_orders(self,orders:dict):
        """计算基准收益率
        """
        from dsxquant import Orders        
        base_orders:Orders = Orders(self,self.symbol)
        base_klines = self.engin_cache.get_klines(self.base_symbol,self.market)
        if base_klines and orders:
            for item in base_klines:
                d,o,h,l,c,v,a = item.split(",")
                buykey = self.symbol + d + EventType.BUY
                sellkey = self.symbol + d + EventType.SELL
                name = self.base_symbol
                symbol = self.base_symbol
                market = self.market
                date = d
                price = float(c)
                if buykey in orders:
                    buyorder = orders.get(buykey)
                    amount = buyorder[5]
                    base_orders.insert(name,symbol,market,price,amount,date,EventType.BUY)
                
                if sellkey in orders:
                    sellorder = orders.get(sellkey)
                    amount = sellorder[5]
                    base_orders.insert(name,symbol,market,price,amount,date,EventType.SELL)
        self.show_orders(base_orders)
        


    def sendevent(self,event:EventModel):
        """给策略引擎发送事件

        Args:
            event (EventModel): _description_
        """
        if self.strategy_engin and event:
            self.strategy_engin.receive(event)
    
    def sendbus(self,event:EventModel):
        """给总线发送事件

        Args:
            event (EventModel): _description_
        """
        if event:
            if event.bus:
                event.bus.register(event)
    
    def next(self):
        self.get_current_event()
        pass

    def load_datas(self):
        if self.symbol:
            data = (self.symbol,self.market,self.fq,self.start_date,self.end_date,self.base_symbol)
            # 指定给datafeed引擎处理
            from dsxquant import DataFeed
            etype = EventType.DAYLINE
            event = EventModel(self.event_bus,etype,data,DataFeed,source=self)
            self.event_bus.register(event)

        

    