from dsxquant.engins.engin import Engin
from dsxquant.backtest.back_test import BackTest
from dsxquant import StrategyEngin
from dsxquant import MARKET
from dsxquant import EmulationEngin,DataFeed,EventType
from dsxquant.strategy.common.抛物线策略 import 抛物线策略

# 先启动系统引擎
engin = Engin().start()
# 安装模块
engin.install(StrategyEngin,EmulationEngin,DataFeed)
# 安装回测模块到系统,需要设置回测参数
backtest = BackTest(抛物线策略,"000001",MARKET.SZ,"20220101","20230401",data=EventType.DAYLINE)
engin.install(backtest)
# 显示回测结果  
backtest.show(show_order=True)
backtest.show_kline()
# backtest2.show(show_order=True)
