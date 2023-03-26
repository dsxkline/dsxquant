from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType,MARKET

class 放量突破策略(BaseStrategy):

    __title__ = "放量突破策略"
    __desc__ = """
    主力放量后，第二天上涨买入
    止盈：5% 收益
    止损：-3% 止损
    """
    __type__ = EventType.DAYBAR

    def init(self):
        """初始化
        """
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        公式的输出结果可以在 execute 函数中引用，例如 self.kline.VOLN.VOL30
        """
        return ("VOLN","""
        VOL30:MA(VOL,30);
        MA30:MA(CLOSE,30);
        BUY:VOL>VOL30 AND VOL30>0 AND REF(VOL,1)>REF(VOL,2) AND VOL>REF(VOL,1);
        """)
    
    def stop(self):
        """止损止盈
        设置每笔交易的止盈止损，或者设置资产收益的止盈止损，或者设置止盈止损的策略
        """
        # 止损 跌破5%时止损
        self.stop_loss = -0.03
        # 止盈 盈利5%时止盈
        self.take_profit = 0.05


    def execute(self):
        """交易信号
        """
        name = self.symbol
        symbol = self.symbol
        market = self.market
        price = self.kline.CLOSE
        date = self.kline.DATE
        # 得到公式的输出值
        buy = self.kline.VOLN.BUY
        if buy:
            return self.buy(name,symbol,market,1000,price,date)
        

            