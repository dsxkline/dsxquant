from typing import List
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant import EventType
from dsxquant.config.logconfig import logger
from dsxquant.engins.base import BaseEngin
from dsxquant.trade.base import BaseTrade
from dsxquant.trade.buy import Buy
from dsxquant.trade.cancel import Cancel
from dsxquant.trade.sell import Sell

class TradeEngin(BaseEngin):
    __name__ = "实盘交易引擎"
    __interface_execute = "execute"
    
    def __init__(self,event_types:List[EventType]=None):
        super().__init__(event_types)
        self.trades:List[BaseTrade] = []
        self.autoregister()
    
    def autoregister(self):
        self.register(Buy)
        self.register(Sell)
        self.register(Cancel)
   
    def register(self,trade:BaseTrade):
        """注册需要执行的交易

        Args:
            trade (BaseStrategy): _description_
        """
        self.trades.append(trade)
    
    def run(self):
        while(not self.exit):
            if self.event and self.event.target==self.__class__:
                for trade in self.trades:
                    if trade.__type__==self.event.type:
                        if type(trade)==type: trade = trade(self.event)
                        if hasattr(trade,self.__interface_execute):
                            method = getattr(trade,self.__interface_execute)
                            if callable(method):
                                event = method()
                                self.sendbus(event)
            if self.event:
                if self.event.type==EventType.THEEND:
                        # 结束回测
                        break
            # 处理后销毁
            self.destroy()
            self.next()
    
    def on_finished(self):
        """回测结束
        """
        from dsxquant import Orders
        order = Orders.order_list.get(self.event.source)
        if order:
            # 持仓中
            logger.info("持仓中：")
            logger.info(order.positions)
            logger.info("已平仓：")
            logger.info(order.positions_closed)
            