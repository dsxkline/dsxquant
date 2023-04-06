from dsxquant.engins.engin import Engin
from dsxquant.backtest.back_test import BackTest
from dsxquant import StrategyEngin
from dsxquant import MARKET
from dsxquant import EmulationEngin,DataFeed,EventType
from dsxquant.strategy.common.抛物线策略 import 抛物线策略
from dsxquant.strategy.common.macross_strategy import MACrossStrategy
from dsxquant.strategy.common.放量突破策略 import 放量突破策略

# 先启动系统引擎
engin = Engin().start()
# 安装模块
engin.install(StrategyEngin,EmulationEngin,DataFeed)

symbols = [
    "sz000001",
    "sz000002",
    "sh600000",
    "sz301110"
]
for symbol in symbols:
    # 安装回测模块到系统,需要设置回测参数
    backtest = BackTest(放量突破策略,symbol,start="20220101",end="20230501",data=EventType.DAYLINE)
    engin.install(backtest)
    # 等待回测完成并显示回测结果  
    backtest.show()
    # backtest.show_kline()

engin.shutdown()
# backtest2.show(show_order=True)
