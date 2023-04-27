from dsxquant.strategy.base import BaseStrategy
from dsxquant import EventType,MARKET

class 抛物线策略(BaseStrategy):

    __title__ = "抛物线策略"
    __desc__ = """
    利用SAR指标
    """
    __type__ = (EventType.DAYBAR,EventType.MINBAR)

    def init(self):
        """初始化
        """
    
    def formula(self):
        """这里写指标公式，支持通达信公式
        公式的输出结果可以在 execute 函数中引用，例如 self.kline.VOLN.VOL30
        """
        return ("SAR","""
        ma30:MA(VOL,30);
        sar:SAR(4,2,20);
        sart:SARTURN(4,2,20);
        dif:MACD.DIF;
        BUY:IF(sart=1 AND dif<0,1,0);
        SELL:IF(sart=-1,1,0);
        """)
    
    def stop(self,order:tuple):
        """止损止盈
        设置每笔交易的止盈止损，或者设置资产收益的止盈止损，或者设置止盈止损的策略
        """
        # 止损 跌破5%时止损
        self.stop_loss = -0.03
        # 止盈 盈利5%时止盈
        self.take_profit = 0.05
        # 当前价格
        price = self.kline.CLOSE
        # 当前时间日期
        date = self.kline.DATE
        # 订单信息
        name,symbol,market,buy_price,amount = order
        # 盈亏
        rate = (price - buy_price) / buy_price
        if rate>=self.take_profit and self.take_profit!=0:
            # 止盈卖出
            self.sell(name,symbol,market,amount,price,date,"止盈卖出")
        
        if rate<=self.stop_loss and self.stop_loss!=0:
            # 止损卖出
            self.sell(name,symbol,market,amount,price,date,"止损卖出")


    def execute(self):
        """交易信号
        """
        name = self.symbol
        symbol = self.symbol
        market = self.market
        price = self.kline.CLOSE
        date = self.kline.DATE
        sar = self.kline.SAR.sar
        if sar==None: sar=0
        # print(date+"="+str(sar))
        # 得到公式的输出值
        buy = self.kline.SAR.BUY
        if buy:
            return self.buy(name,symbol,market,1000,price,date)
        sell = self.kline.SAR.SELL
        if sell:
            return self.sell(name,symbol,market,1000,price,date)
        

            