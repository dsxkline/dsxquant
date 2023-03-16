from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType,MARKET


class MACrossStrategy(BaseStrategy):

    __title__ = "均线交叉策略"
    __desc__ = """
    MA5上穿MA10买入，反之卖出
    """
    __type__ = EventType.DAYBAR

    def init(self):
        """初始化
        """
        # 策略标的
        self.symbols = [("600000",MARKET.SH)]
        # 是否实盘
        self.real = False
        # 数据类型 日线数据
        self.load_dayline()
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        """
        return ("MAn","""
        MA5:MA(CLOSE,5);
        MA10:MA(CLOSE,10);
        LMA5:REF(MA5,1);
        LMA10:REF(MA10,1);
        """)

    def execute(self):
        name = self.symbol
        symbol = self.symbol
        market = self.market
        price = self.data.LOW
        date = self.data.DATE
        h = self.data.HOUR
        m = self.data.MINUTE
        # date = date + " %s:%s" % (h,m)
        # 得到公式的输出值
        MA5 = self.data.MAn.MA5
        MA10 = self.data.MAn.MA10
        LMA10 = self.data.MAn.LMA10
        LMA5 = self.data.MAn.LMA5
        if LMA5<LMA10 and MA5>MA10:
            return self.buy(name,symbol,market,100,price,date)
        if LMA10<LMA5 and MA10>MA5:
            return self.sell(name,symbol,market,100,price,date)

            
