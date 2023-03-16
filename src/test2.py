from dsxquant.engins.engin import Engin
from dsxquant.backtest.back_test import BackTest
from dsxquant.strategy.common.myself_strategy import MyselfStrategy
from dsxquant import StrategyEngin
from dsxquant import EventType
from dsxquant import EmulationEngin,DataFeed
from dsxquant.strategy.common.macross_strategy import MACrossStrategy

# 先启动系统引擎
engin = Engin()
engin.start()
# 启动策略引擎
strategy = StrategyEngin()
strategy.start()
engin.install(strategy)
# 安装回测插件到系统,指定了回测处理的事件类型 处理日线数据事件类型
backtest = BackTest(strategy)
engin.install(backtest)
# 安装仿真交易引擎
emulation = EmulationEngin()
emulation.start()
engin.install(emulation)
# 数据引擎
datafeed = DataFeed()
datafeed.start()
engin.install(datafeed)
# 注册需要运行的策略
strategy.register(MyselfStrategy)
strategy.register(MACrossStrategy)
# 开始回测
backtest.start()
backtest.show()
