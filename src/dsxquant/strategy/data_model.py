import threading
from typing import List
from dsxindexer.processors.sindexer_processor import SindexerProcessor
from dsxindexer.sindexer.models.kline_model import KlineModel
from dsxindexer.configer import Cursor
from dsxindexer.sindexer.sindexer_factory import SindexerFactory
class DataModel:
    lock = threading.Lock()
    __execute_history = []
    __init_klines = {}
    def __init__(self, datas, cursor=0,formula=None) -> None:
        self.datas = datas
        self.klines:List[KlineModel] = []
        self.cursor = cursor
        self.formula = formula
        self.init()

    @property
    def data(self):
        return self.klines[self.cursor]
    
    def init(self):
        ids = id(self.datas)
        with self.lock:
            if ids not in self.__init_klines.keys():
                sp = SindexerProcessor(self.datas)
                if self.formula:
                    name,content = self.formula
                    if name not in self.__execute_history:
                        self.__execute_history.append(name)
                        # 通过指标工厂自定义指标
                        m = SindexerFactory.create(name,content,functioner=sp.functioner)
                        sp.register(m)
                # 执行计算结果
                self.klines = sp.execute()
                self.__init_klines[ids] = self.klines
            else:
                self.klines = self.__init_klines.get(ids)

    def execute(self):
        pass

     
