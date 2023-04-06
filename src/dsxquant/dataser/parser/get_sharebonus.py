from dsxquant.dataser.parser.base import BaseParser
from dsxquant.common.cache import CacheHelper
class GetShareBonusParser(BaseParser):

    def setApiName(self):
        self.api_name = "sharebonus"
    
    def setParams(self, symbol:str,market:int,start:str=None,end:str=None,enable_cache:bool=True):
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            start (str): 开始日期 Y-m-d
            end (str): 结束日期 Y-m-d
        """
        self.enable_cache = enable_cache
        self.symbol = symbol
        self.market = market
        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "start":start,
            "end":end
        })
        self.send_datas = datas
        if self.enable_cache:
            self.cache = CacheHelper.save_sharebonus(symbol,market,start,end)
        
        
    
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
                    if isinstance(data,dict):
                        date = None
                        if "share_day" in data:
                            date = data.get("share_day")
                        if date:
                            CacheHelper.save_sharebonus(self.symbol,self.market,date,data)
                    if isinstance(data,list):
                        for item in data:
                            date = None
                            if "share_day" in item:
                                date = item.get("share_day")
                            if date:
                                CacheHelper.save_sharebonus(self.symbol,self.market,date,item)

        return datas


        