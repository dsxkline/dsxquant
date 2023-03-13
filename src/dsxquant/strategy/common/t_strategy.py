from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType
from dsxquant.engins.event_model import EventModel


class MyselfStrategy(BaseStrategy):

    __title__ = "放量T0策略"
    __desc__ = """
    日内T0策略，放量后买入，缩量后卖出
    """
    __type__ = EventType.DAYBAR

    def init(self):
        """初始化
        """
        # 策略标的
        self.symbols = [("000001",0)]
        # 数据类型 日线数据策略
        self.load_dayline()
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        """
        return ("jinca","""
        金叉:CROSS("MACD.DIFF","MACD.DEA");
        死叉:CROSS("MACD.DEA","MACD.DIFF");
        """)

    def execute(self):
        symbol = self.symbol
        market = self.market
        price = self.data.LOW
        # 得到公式的输出值
        jc = self.data.jinca.金叉
        sc = self.data.jinca.死叉
        if jc:
            return self.buy(symbol,market,100,price)
        if sc:
            return self.sell(symbol,market,100,price)

            
