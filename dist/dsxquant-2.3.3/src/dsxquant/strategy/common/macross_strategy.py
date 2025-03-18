from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType,MARKET


class MACrossStrategy(BaseStrategy):

    __title__ = "均线交叉策略"
    __desc__ = """
    MA5上穿MA20买入，反之卖出
    当短期均线（如5日均线）上穿长期均线（如20日均线）时，认为市场处于上升趋势，可以买入；当短期均线下穿长期均线时，认为市场处于下降趋势，可以卖出。
    """
    __type__ = (EventType.DAYBAR,EventType.MINBAR)

    def init(self):
        """初始化
        """
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        """
        return ("MAn","""
        MA5:MA(CLOSE,5);
        MA20:MA(CLOSE,20);
        LMA5:REF(MA5,1);
        LMA20:REF(MA20,1);
        """)

    def execute(self):
        name = self.symbol
        symbol = self.symbol
        market = self.market
        price = self.kline.LOW
        date = self.kline.DATE
        # h = self.kline.HOUR
        # m = self.kline.MINUTE
        # date = date + " %s:%s" % (h,m)
       
        # 得到公式的输出值
        MA5 = self.kline.MAn.MA5
        MA20 = self.kline.MAn.MA20
        LMA20 = self.kline.MAn.LMA20
        LMA5 = self.kline.MAn.LMA5

        # print(date,MA5,MA20)

        if LMA5<LMA20 and MA5>MA20:
            return self.buy(name,symbol,market,100,price,date)
        if LMA20<LMA5 and MA20>MA5:
            return self.sell(name,symbol,market,100,price,date)

            
