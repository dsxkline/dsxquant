from dsxquant.dataser.parser.base import BaseParser
from dsxquant.config import config
from dsxquant.common.cache import CacheHelper
class GetFinanceParser(BaseParser):

    def setApiName(self):
        self.api_name = "finance"
    
    def setParams(self,symbol,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date:str=None,start:str=None,end:str=None,enable_cache:bool=True):
        """构建请求参数
        Args:
            symbols (list): 证券代码数组
        Returns:
            _type_: _description_
        """
        self.symbol = symbol
        self.market = market
        self.report_type = report_type
        self.enable_cache = enable_cache
        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "report_type":report_type,
            "report_date":report_date,
            "start":start,
            "end":end
        })
        self.send_datas = datas

        if self.enable_cache:
            self.cache = CacheHelper.get_finance(symbol,market,report_type,report_date,start,end)
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("执行  "+__name__+"  数据解析方法")
        # 保存缓存数据
        if datas and self.enable_cache:
            if datas["success"]:
                data = datas["data"]
                if data:
                    if isinstance(data,dict):
                        date = None
                        if "DATE" in data:
                            date = data.get("DATE")
                        if "report_date" in data:
                            date = data.get("report_date")
                        if date:
                            CacheHelper.save_finance(self.symbol,self.market,self.report_type,date,data)
                    if isinstance(data,list):
                        for item in data:
                            date = None
                            if "DATE" in item:
                                date = item.get("DATE")
                            if "report_date" in item:
                                date = item.get("report_date")
                            if date and item:
                                CacheHelper.save_finance(self.symbol,self.market,self.report_type,date,item)
                

        return datas


        