import datetime
from dsxquant.dataser.parser.base import BaseParser
from dsxquant.common.cache import CacheHelper
class GetTimeSharingParser(BaseParser):

    def setApiName(self):
        self.api_name = "timesharing"
    
    def setParams(self, symbol:str,market:int,trade_date:str="",day:int=1,enable_cache:bool=True):
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            trade_date (str): 交易日期 Y-m-d
        """
        self.enable_cache = enable_cache
        self.symbol = symbol
        self.market = market
        self.trade_date = trade_date
        self.day = day
        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "trade_date":trade_date,
            "day":day
        })
        self.send_datas = datas
        if self.enable_cache:
            self.cache = CacheHelper.get_timesharing(symbol,market,trade_date,day)
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("parseResponse  "+__name__+" ")
        # 保存缓存数据
        if datas and self.enable_cache:
            if datas["success"]:
                data = datas["data"]
                if data:
                    if not self.trade_date:self.trade_date = datetime.datetime.now().strftime("%Y%m%d")
                    CacheHelper.save_timesharing(self.symbol,self.market,self.trade_date,self.day,data)
               

        return datas


        