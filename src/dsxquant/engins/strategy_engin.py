from typing import List
from dsxquant.strategy.base import BaseStrategy    
from dsxquant.config.logconfig import logger
from dsxquant.engins.base import BaseEngin
from dsxquant.engins.event_model import EventModel

class StrategyEngin(BaseEngin):
    __name__ = "策略引擎"
    __interface_execute = "execute"
    __interface_load = "load"

    def __init__(self,event_types=None):
        super().__init__(event_types)
        self.strategies:List[BaseStrategy] = []
   
    def register(self,strategy:BaseStrategy):
        """注册需要执行的策略

        Args:
            strategy (BaseStrategy): _description_
        """
        self.strategies.append(strategy)

    def run(self):
        while(not self.exit):
            if self.strategies:
                if self.event and self.event.target==self.__class__:
                    i = 0
                    for strategy in self.strategies:
                        if type(strategy)==type: 
                            strategy = strategy(self.event)
                            self.strategies[i] = strategy
                        if strategy.__type__==self.event.type:
                            # load
                            if hasattr(strategy,self.__interface_load):
                                load = getattr(strategy,self.__interface_load)
                                if callable(load):
                                    load(self.event)
                            # execute
                            if hasattr(strategy,self.__interface_execute):
                                execute = getattr(strategy,self.__interface_execute)
                                if callable(execute):
                                    event = execute()
                                    self.sendbus(event)
                        i += 1
                # 处理后销毁
                self.destroy()
                self.next()
    
   