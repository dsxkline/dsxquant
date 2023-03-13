from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType
from dsxquant.engins.event_model import EventModel


class MyselfStrategy(BaseStrategy):

    __title__ = "MACD金叉交易策略"
    __desc__ = """
    金叉定义：当MACD指标中的DIFF线从下而上与DEA线交叉时，这个交叉为金叉，金叉一般情况下是买入的信号。
    死叉定义：当MACD指标中的DIFF线从上而下与DEA线交叉时，这个交叉为死叉，死叉一般情况下是卖出的信号。
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

            
