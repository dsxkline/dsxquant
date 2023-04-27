import threading
from typing import List
from dsxindexer.sindexer.models.kline_model import KlineModel
import dsxindexer
class DataModel:
    lock = threading.Lock()
    __execute_history = []
    __init_klines = {}
    def __init__(self, symbol,datas, cursor=0,formula=None,norisk=None) -> None:
        self.datas = datas
        self.klines:List[KlineModel] = []
        self.cursor = cursor
        self.formula = formula
        self.symbol = symbol
        self.norisk = norisk
        self.init()

    @property
    def data(self):
        return self.klines[self.cursor]
    
    def init(self):
        # 初始化我们计算一遍指标
        if not self.datas : return
        ids = str(id(self.datas))+self.symbol
        with self.lock:
            if ids not in self.__init_klines.keys():
                sp = dsxindexer.sindexer(self.datas,enable_cache=False)
                if self.formula:
                    name,content = self.formula
                    fkey = name+ids
                    if fkey not in self.__execute_history:
                        self.__execute_history.append(fkey)
                        # 通过指标工厂自定义指标
                        m = dsxindexer.factory.create(name,content)
                        sp.register(m)
                # 执行计算结果
                self.klines = sp.execute()
                self.__init_klines[ids] = self.klines
            else:
                self.klines = self.__init_klines.get(ids)

    def execute(self):
        pass

     
