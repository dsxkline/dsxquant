from dsxquant.engins.engin import Engin
from dsxquant.backtest.back_test import BackTest
from dsxquant import StrategyEngin
from dsxquant import MARKET
from dsxquant import EmulationEngin,DataFeed,EventType
from dsxquant.strategy.common.抛物线策略 import 抛物线策略
from dsxquant.strategy.common.macross_strategy import MACrossStrategy
from dsxquant.strategy.common.放量突破策略 import 放量突破策略
import dsxquant
# 先启动系统引擎
engin = Engin().start()
# 安装模块
engin.install(StrategyEngin,EmulationEngin,DataFeed)

stocks = [
    # ("600000",0),
    ("000002",1),
]

# stocks = dsxquant.get_stocks(MARKET.SZ).series()
# stocks = list(stocks)
# stocks.reverse()
i = 1
count = stocks.__len__()
for item in stocks:
    symbol,market = item
    code = dsxquant.MARKET_VAL[market]+symbol
    dsxquant.logger.debug("回测 %s %s/%s" % (code,i,count))
    # 安装回测模块到系统,需要设置回测参数
    backtest = BackTest(MACrossStrategy,code,start="20200201",end="20230518",data_type=EventType.DAYLINE)
    engin.install(backtest)
    # 等待回测完成并显示回测结果  
    backtest.show()
    i+=1

engin.shutdown()
