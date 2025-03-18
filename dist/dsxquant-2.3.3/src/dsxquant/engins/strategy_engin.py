import threading
from typing import Dict, List
from dsxquant.strategy.base import BaseStrategy    
from dsxquant.config.logconfig import logger
from dsxquant.engins.base import BaseEngin
from dsxquant import EventType
from progressbar import ProgressBar

class StrategyEngin(BaseEngin):
    __name__ = "策略引擎"
    __interface_execute = "execute_all"
    __interface_load = "load"

    def __init__(self,event_types=None):
        super().__init__(event_types)
        self.strategies:List[BaseStrategy] = []
        self.strategies_test:Dict[BaseStrategy] = {}
   
    def register(self,strategy:BaseStrategy):
        """注册需要执行的策略

        Args:
            strategy (BaseStrategy): _description_
        """
        self.strategies.append(strategy)

    def unregister(self,strategy:BaseStrategy):
        """注册需要执行的策略

        Args:
            strategy (BaseStrategy): _description_
        """
        if strategy in self.strategies:
            self.strategies.remove(strategy)


    def run(self):
        real = False
        end_count = 0
        while(not self.exit):
            if self.strategies:
                if self.event and self.event.target==self.__class__:
                    if self.event.type!=EventType.NONE:
                        i = 0
                        for strategy in list(self.strategies):
                            if self.event.source in self.strategies_test.keys():
                                strategy = self.strategies_test.get(self.event.source)
                            if type(strategy)==type: 
                                strategy = strategy(self.event)
                                self.strategies_test[self.event.source] = strategy
                            if strategy.__type__==self.event.type or self.event.type in strategy.__type__:
                                # load
                                if hasattr(strategy,self.__interface_load):
                                    load = getattr(strategy,self.__interface_load)
                                    if callable(load):
                                        load(self.event)
                                if hasattr(strategy,"real"):
                                    real = getattr(strategy,"real")
                                # execute
                                if hasattr(strategy,self.__interface_execute):
                                    execute = getattr(strategy,self.__interface_execute)
                                    if callable(execute):
                                        execute(self.event)
                            else:
                                if self.event.type!=EventType.THEEND : logger.debug("策略与事件数据类型不匹配")
                                    
                        if self.event.type==EventType.THEEND and self.event.target==self.__class__:
                            # 最后一个策略运行完毕
                            # 结束回测,通知其他组件
                            end_count += 1
                            if end_count>=len(self.event.data):
                                self.event.target=None
                                self.sendbus(self.event)
                                # break
                                    
                            i += 1
                # 处理后销毁
                self.destroy()
                self.next()
    
        logger.debug("策略引擎关闭")