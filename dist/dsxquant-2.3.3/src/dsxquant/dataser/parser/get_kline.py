from dsxquant.dataser.parser.base import BaseParser
from dsxquant.config.config import FQ,CYCLE,MARKET_VAL
from dsxquant.common.cache import CacheHelper
class GetKlinesParser(BaseParser):

    def setApiName(self):
        self.api_name = "klines"
    
    def setParams(self, symbol:str,market:int,page:int=1,page_size:int=320,fq:str=FQ.DEFAULT,cycle:CYCLE=CYCLE.DAY,start:str=None,end:str=None,enable_cache:bool=True):
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
            "start":start,
            "end":end
        })
        self.send_datas = datas
        if self.enable_cache:
            self.cache = CacheHelper.get_klines(symbol,market,page,page_size,fq,cycle,start,end)
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            body_buf (byte): 服务端返回的字节流
        """

        # 保存缓存数据
        if datas and self.enable_cache:
            if datas["success"]:
                data = datas["data"]
                if data:
                    CacheHelper.save_klines(self.symbol,self.market,self.cycle,self.fq,data)

        # logger.debug("parseResponse  "+__name__+"  ")
        return datas




        