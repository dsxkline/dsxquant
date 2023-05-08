import os
import threading
import time
from typing import List

import pandas
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant import EventType
from dsxquant import logger
from dsxquant import StrategyEngin,BaseSymbol,Engin,MARKET,config,FQ,MARKET_VAL
from prettytable import PrettyTable
# from pydsxkline.dsxkline import DsxKline,CycleType

class BackTest:
    last_backtest = []
    def __init__(self,strategy,symbol:str,market:MARKET=MARKET.SH,start:str=None,end:str=None,funds=100000,base_symbol:BaseSymbol=BaseSymbol.HS300,data:EventType=EventType.DAYLINE,fq:FQ=FQ.QFQ,norisk=2.5,export_path=None):
        """回测

        Args:
            strategy (BaseStrategy): 自定义策略类
            symbol (str): 股票代码
            market (MARKET): 市场
            start (str): 开始日期
            end (str): 结束日期
            funds (int, optional): 初始资金. Defaults to 100000.
            base_symbol (BaseSymbol, optional): 基准指数. Defaults to BaseSymbol.HS300.
            data (EventType, optional): _description_. 数据 to EventType.DAYLINE.
        """
        self.strategy = strategy
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
        if symbol[:2] in MARKET_VAL:
            self.symbol = symbol[2:]
            self.market = MARKET_VAL.index(symbol[:2])
        
        # 复权
        self.fq = fq
        # 数据
        self.data = data
        # 无风险收益率,默认指定为2.5%，一般取国债收益率
        self.norisk = norisk
        # 导出目录
        self.export_path = export_path
        # 回测天数
        self.days = 0

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
        # 首先注册策略到策略引擎
        self.strategy_engin.register(self.strategy)
        BackTest.last_backtest.append(self)
        # 启动自己的线程
        threading.Thread(target=self.run).start()
        logger.info("启动[%s][%s]回测...." % (self.symbol,self.strategy_engin.strategies[0].__title__))
        self.load_datas()
        return self

    def shutdown(self):
        self.exit = True
        
    
    def show(self,show_order:bool=False,show_position:bool=False):
        """显示回测结果
        """
        
        while True:
            time.sleep(0.1)
            if isinstance(self.event,EventModel):
                if self.event.type==EventType.THEEND:
                    # 结束回测
                    break
            # time.sleep(1)
        
        self.on_finished(show_order,show_position)
        self.close()

    def destroy(self):
        if self.events.__len__()>0:
            if self.event in self.events:
                self.events.remove(self.event)
        self.event = None

    def run(self):
        while not self.exit:
            if self.event:
                self.on_dayline()
                self.on_minline()
                if self.event.type==EventType.THEEND:
                    # 结束回测
                    break
            self.destroy()
            self.next()
        logger.debug("回测[%s]结束" % self.symbol)
    

    
    def close(self):
        """关闭回测
        """
        # logger.info("回测结束")
        self.destroy()
        self.strategy_engin.unregister(self.strategy)
        if self in BackTest.last_backtest:
            BackTest.last_backtest.remove(self)

    def on_dayline(self):
        """处理日线数据集事件
        """
        if (self.event.type==EventType.DAYLINE) and self.event.target==self:
            data = self.event.data
            symbol,market,datas = data
            data = (symbol,market,datas,self.norisk)
            event_bus:EventBus = self.event.bus
            self.days = len(datas)
            for i in range(len(datas)):
                event = EventModel(event_bus,EventType.DAYBAR,data,StrategyEngin,i,source=self)
                # 直接给策略引擎发消息
                self.sendevent(event)
            # 结束传送
            self.sendevent(EventModel(self.event_bus,EventType.THEEND,data=self.last_backtest,target=StrategyEngin,source=self))
    
    def on_minline(self):
        """处理分钟线数据集事件
        """
        if (self.event.type==EventType.MIN1LINE or self.event.type==EventType.MIN5LINE or self.event.type==EventType.MIN15LINE or self.event.type==EventType.MIN30LINE or self.event.type==EventType.MIN60LINE) and self.event.target==self:
            data = self.event.data
            symbol,market,datas = data
            data = (symbol,market,datas,self.norisk)
            event_bus:EventBus = self.event.bus
            self.days = len(datas)
            for i in range(len(datas)):
                event = EventModel(event_bus,EventType.MINBAR,data,StrategyEngin,i,source=self)
                # 直接给策略引擎发消息
                self.sendevent(event)
            # 结束传送
            self.sendevent(EventModel(self.event_bus,EventType.THEEND,data=self.last_backtest,target=StrategyEngin,source=self))
            
    
    def on_finished(self,show_order:bool=True,show_position:bool=False):
        """回测结束
        """
        from dsxquant import Orders
        sid = str(id(self))+self.symbol
        order:Orders = Orders.order_list.get(sid)
        if order:
            # self.base_orders(order.orders,show_order,show_position)
            self.export(self.symbol,order,show_order,show_position)
    
    @property
    def engin_cache(self):
        return Engin.get_instance().cachespace

    def base_orders(self,orders:dict,show_order:bool=True,show_position:bool=False):
        """计算基准收益率
        """
        from dsxquant import Orders        
        base_orders:Orders = Orders(self,self.base_symbol,self.norisk)
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
                    base_orders.insert(name,symbol,market,price,amount,date,EventType.BUY,self.norisk,"")
                
                if sellkey in orders:
                    sellorder = orders.get(sellkey)
                    amount = sellorder[5]
                    base_orders.insert(name,symbol,market,price,amount,date,EventType.SELL,self.norisk,"")
                    
        self.export(self.base_symbol,base_orders,show_order,show_position)

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
            etype = self.data
            event = EventModel(self.event_bus,etype,data,DataFeed,source=self)
            self.event_bus.register(event)

    def export(self,symbol,order,show_order:bool=True,show_position:bool=False):
        """导出订单表
        """
        path = self.export_path and self.export_path or config.EXPORT_PATH
        
        from dsxquant import Orders        
        order:Orders = order
        orders = order.orders.values()
        columns = ['订单列表', '股票名称','代码', '市场','价格','股数','平仓日期','类型','开仓日期','卖出价格','卖出股数','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%',"备注"]
        rs = pandas.DataFrame(orders,columns=columns)
        save_path = path+"/export/"+self.strategy.__title__+"/"+symbol
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        rs.to_csv(save_path+"/orders.csv")
        if show_order:
            # # 创建表格对象，并设置表头
            table:PrettyTable = PrettyTable(columns)
            table.add_rows(orders)
            print(table)


        columns = ['历史持仓', '股票代码', '市场','持仓价格','持仓股数','平仓日期','状态','持仓总股数','开仓日期','平仓价格','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%']
        rs = pandas.DataFrame(order.positions_closed,columns=columns)
        rs.to_csv(save_path+"/positions_closed.csv")
        if show_position:
            table:PrettyTable = PrettyTable(columns)
            table.add_rows(order.positions_closed)
            print(table)

        columns = ['持仓中', '股票代码', '市场','持仓价格','持仓股数','平仓日期','状态','持仓总股数','开仓日期','平仓价格','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%']
        rs = pandas.DataFrame(order.positions,columns=columns)
        rs.to_csv(save_path+"/positions.csv")
        if show_position:
            table:PrettyTable = PrettyTable(columns)
            table.add_rows(order.positions.values())
            print(table)

        columns = ['回测周期',"交易次数",'收益率%',"资产收益率%", '年化收益率%','夏普比率', '盈亏比%','胜率%','最大回撤%','最大收益率%','最小收益率%','总资产','盈利','亏损']
        rs = pandas.DataFrame(order.records,columns=columns)
        rs.to_csv(save_path+"/index.csv")

        table:PrettyTable = PrettyTable(columns)
        table.add_rows(order.records)
        print(symbol+" 回测结果:")
        print(table)
        

    # def show_kline(self):
    #     """显示导出的信息面板
    #     """
    #     from dsxquant import Orders
    #     sid = str(id(self))+self.symbol
    #     order:Orders = Orders.order_list.get(sid)
    #     if order:
    #         def draw_event():
    #             """显示交易买卖点"""
    #             buysells = []
    #             orders = order.orders.values()
    #             for item in orders:
    #                 price = item[4]
    #                 amount = item[5]
    #                 types = item[7] 
    #                 date = item[8]
    #                 color = types=="buy" and "orange" or "purple"
    #                 # price = types=="buy" and price*0.99 or price*1.01
    #                 cmd = DsxKline.draw_circle_with_date(date,types[0],color,"#ffffff",price)
    #                 buysells.append(cmd)

    #             return buysells

    #         header = """
    #             <h1 style="color:#fff;text-align:center;font-size:20px;line-height:50px;border-bottom:1px solid #191b28"> 回测结果 </h1>
    #             <ul class="mycss">
    #                 <li><span>回测天数：</span><b> %s 天</b></li>
    #                 <li><span>交易次数：</span><b> %s 天</b></li>
    #                 <li><span>收益率：</span><b> %s 天</b></li>
    #                 <li><span>资产收益率：</span><b> %s %% </b></li>
    #                 <li><span>年化收益率：</span><b> %s %% </b></li>
    #                 <li><span>夏普比率：</span><b> %s </b></li>
    #                 <li><span>盈亏比：</span><b> %s </b></li>
    #                 <li><span>胜率：</span><b> %s %% </b></li>
    #                 <li><span>最大回撤：</span><b> %s %% </b></li>
    #                 <li><span>最大收益率：</span><b> %s %% </b></li>
    #                 <li><span>最小收益率：</span><b> %s %% </b></li>
    #                 <li><span>总资产：</span><b> %s 元</b></li>
    #                 <li><span>盈利：</span><b> %s 元</b></li>
    #                 <li><span>亏损：</span><b> %s 元</b></li>
    #                 <li><span>换手率：</span><b> %s 天</b></li>
    #             </ul>
    #             <style>
    #                 .mycss{
    #                     list-style:none;
    #                     padding:10px 20px;
    #                     color:#c5cbc0;
    #                     font-size:14px;
    #                 }
    #                 .mycss li{
    #                     float:left;
    #                     width:25%%;
    #                     padding:5px 0;
    #                 }
    #                 .mycss li span{
    #                     color:#c5cbce;
    #                 }
    #             </style>
    #         """ % order.records[0]
    #         code = MARKET_VAL[self.market]+ self.symbol
    #         # 数据
    #         datas = self.engin_cache.get_klines(self.symbol,self.market)
    #         DsxKline.show(code,code,CycleType.day,draw_event=draw_event(),header_html=header,header_height=160,enable_data_api=False,datas=datas,main=["SAR"])

    