import threading
import time
from typing import List
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant import EventType
from dsxquant import logger
from dsxquant import StrategyEngin
from prettytable import PrettyTable

class BackTest:
    def __init__(self,strategy_engin:StrategyEngin=None,event_types:List[EventType]=None):
        self.exit = False
        self.event_types:List[EventType] = event_types
        self.events:List[EventModel] = []
        self.event:EventModel = None
        self.strategy_engin:StrategyEngin = strategy_engin
    
    def receive(self,event:EventModel):
        """接收事件总线的事件

        Args:
            event (EventModel): _description_
        """
        if self.event_types:
            if event.type not in self.event_types:
                return
            # logger.debug("接收事件 %s" % event)
        self.events.append(event)
    
    def get_current_event(self):
        if self.events.__len__()>0:
            self.event = self.events[0]
            return self.event
        
    def start(self):
        """启动回测
        """
        threading.Thread(target=self.run).start()
        logger.info("启动回测....")
    
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
        order:Orders = Orders.order_list.get(self.event.source)
        if order:
            # # 创建表格对象，并设置表头
            table:PrettyTable = PrettyTable(['订单列表', 'Symbol', 'Market','Price','Amount','Date','Type'])
            table.add_rows(order.orders)
            print(table)
            table:PrettyTable = PrettyTable(['持仓中', 'Symbol', 'Market','Price','Amount','Date','Status'])
            table.add_rows(order.positions.values())
            print(table)
            table:PrettyTable = PrettyTable(['历史持仓', 'Symbol', 'Market','Price','Amount','Date','Status'])
            table.add_rows(order.positions_closed)
            print(table)

            # 打印一个图表
            x = [item[5] for item in order.orders]
            y = [item[3] for item in order.orders]
            
            import plotly.graph_objs as go
            import plotly.offline as pyo

            # 创建折线图数据
            trace = go.Scatter(x=x, y=y, mode='lines', name='line')
            # 定义布局
            layout = go.Layout(title='折线图', xaxis=dict(title='x轴'), yaxis=dict(title='y轴'))
            # 绘制图表
            fig = go.Figure(data=[trace], layout=layout)
            pyo.plot(fig, filename='line_chart.html')
            fig.show()

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
    