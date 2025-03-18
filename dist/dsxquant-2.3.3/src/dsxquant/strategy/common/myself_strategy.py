from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType,MARKET
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
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        """
        return ("jinca","""
        金叉:CROSS(MACD.DIF,MACD.DEA);
        死叉:LONGCROSS(MACD.DIF,MACD.DEA,5);
        """)

    def execute(self):
        name = self.symbol
        symbol = self.symbol
        market = self.market
        price = self.kline.LOW
        date = self.kline.DATE
        h = self.kline.HOUR
        m = self.kline.MINUTE
        # date = date + " %s:%s" % (h,m)
        # 得到公式的输出值
        jc = self.kline.jinca.金叉
        sc = self.kline.jinca.死叉
        if sc:
            return self.sell(name,symbol,market,100,price,date)
        if jc:
            return self.buy(name,symbol,market,100,price,date)

            
