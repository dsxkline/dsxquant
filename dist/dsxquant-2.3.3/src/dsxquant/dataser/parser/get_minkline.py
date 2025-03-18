from dsxquant.dataser.parser.base import BaseParser
from dsxquant.config.config import FQ,CYCLE,MARKET_VAL
from dsxquant.common.cache import CacheHelper
class GetMinKlinesParser(BaseParser):

    def setApiName(self):
        self.api_name = "minklines"
    
    def setParams(self, symbol:str,market:int,page:int=1,page_size:int=240,fq:str=FQ.DEFAULT,cycle:CYCLE=CYCLE.M1,enable_cache:bool=True):
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            page (int): 页码 默认 1
            page_size (int): 每页大小 默认 320
            fq (str): 复权类型
            cycle (str): 周期
        """
        self.enable_cache = enable_cache
        self.symbol = symbol
        self.market = market
        self.fq = fq
        self.cycle = cycle
        if symbol:
            if not symbol[0:2].isdigit():
                market = MARKET_VAL.index(symbol[0:2])
                symbol = symbol[2:]

        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "page":page,
            "page_size":page_size,
            "fq":fq,
            "cycle":cycle,
        })
        self.send_datas = datas
       
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            body_buf (byte): 服务端返回的字节流
        """
        # logger.debug("parseResponse  "+__name__+"  ")
        return datas




        