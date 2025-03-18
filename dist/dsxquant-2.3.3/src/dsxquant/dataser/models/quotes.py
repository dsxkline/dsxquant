

import json


class QuoteModel(object):
    def __init__(self) -> None:
        self.name:str = None
        self.code:str = None
        self.price:float = None
        self.last:float = None
        self.open:float = None
        self.buy_1:float = None
        self.buy_1_v:int = None
        self.buy_2:float = None
        self.buy_2_v:int = None
        self.buy_3:float = None
        self.buy_3_v:int = None
        self.buy_4:float = None
        self.buy_4_v:int = None
        self.buy_5:float = None
        self.sell_1:float = None
        self.sell_1_v:int = None
        self.sell_2:float = None
        self.sell_2_v:int = None
        self.sell_3:float = None
        self.sell_3_v:int = None
        self.sell_4:float = None
        self.sell_4_v:int = None
        self.sell_5:float = None
        self.sell_5_v:int = None
        self.lastdate:str = None
        self.lasttime:str = None
        self.vol:int = None
        self.amount:float = None
        self.high:float = None
        self.low:float = None
        self.ampl:float = None
        self.flow:float = None
        self.total:float = None
        self.tr:float = None
        self.pbr: float = None
        self.per: float = None

