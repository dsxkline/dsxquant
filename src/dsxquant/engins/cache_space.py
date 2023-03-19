from dsxquant import MARKET,MARKET_VAL
class CacheSpace:
    def __init__(self) -> None:
        self.klines = {}
        self.finance = {}
        self.structure = {}
        pass

    def set_klines(self,symbol:str,market:MARKET,klines:list):
        code = symbol+MARKET_VAL[market]
        self.klines[code] = klines

    def get_klines(self,symbol:str,market:MARKET):
        code = symbol+MARKET_VAL[market]
        if code in self.klines:
            return self.klines.get(code)
    
    def set_finance(self,symbol:str,market:MARKET,finance:list):
        code = symbol+MARKET_VAL[market]
        self.finance[code] = finance

    def get_finance(self,symbol:str,market:MARKET):
        code = symbol+MARKET_VAL[market]
        if code in self.finance:
            return self.finance.get(code)
    
    def set_structure(self,symbol:str,market:MARKET,structure:list):
        code = symbol+MARKET_VAL[market]
        self.structure[code] = structure

    def get_structure(self,symbol:str,market:MARKET):
        code = symbol+MARKET_VAL[market]
        if code in self.structure:
            return self.structure.get(code)

