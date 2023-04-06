import json
import os
from dsxquant import MARKET,MARKET_VAL,config
class CacheSpace:
    def __init__(self) -> None:
        self.klines = {}
        self.finance = {}
        self.structure = {}
        pass

    def set_klines(self,symbol:str,market:MARKET,klines:list):
        code = MARKET_VAL[market]+symbol
        self.klines[code] = klines

    def get_klines(self,symbol:str,market:MARKET):
        code = MARKET_VAL[market]+symbol
        if code in self.klines:
            return self.klines.get(code)
    
    def set_finance(self,symbol:str,market:MARKET,finance:list):
        code = MARKET_VAL[market]+symbol
        self.finance[code] = finance

    def get_finance(self,symbol:str,market:MARKET):
        code = MARKET_VAL[market]+symbol
        if code in self.finance:
            return self.finance.get(code)
    
    def set_structure(self,symbol:str,market:MARKET,structure:list):
        code = MARKET_VAL[market]+symbol
        self.structure[code] = structure

    def get_structure(self,symbol:str,market:MARKET):
        code = MARKET_VAL[market]+symbol
        if code in self.structure:
            return self.structure.get(code)
    
    
            


        

