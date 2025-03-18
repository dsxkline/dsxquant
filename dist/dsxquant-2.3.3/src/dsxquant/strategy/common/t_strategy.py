from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType
from dsxquant.engins.event_model import EventModel


class T0Strategy(BaseStrategy):

    __title__ = "放量T0策略"
    __desc__ = """
    日内T0策略，放量后买入，2%收益或缩量后卖出
    """
    __type__ = EventType.DAYBAR

    def init(self):
        """初始化
        """
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        """
        return ("ma","""
        MA5:MA(CLOSE,5);
        MA10:MA(CLOSE,10);
        LMA5:REF(MA5);
        LMA10:REF(MA10);
        """)

    def execute(self):
        symbol = self.symbol
        market = self.market
        price = self.kline.LOW
        # 得到公式的输出值
        MA5 = self.kline.ma.MA5
        MA10 = self.kline.ma.MA10
        LMA10 = self.kline.ma.LMA10
        LMA5 = self.kline.ma.LMA5
        if LMA5<LMA10 and MA5>MA10:
            return self.buy(symbol,market,100,price)
        if LMA10<LMA5 and MA10>MA5:
            return self.sell(symbol,market,100,price)

            
