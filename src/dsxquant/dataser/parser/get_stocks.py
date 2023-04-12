from dsxquant.dataser.parser.base import BaseParser
class GetStocksParser(BaseParser):

    def setApiName(self):
        self.api_name = "stocks"
    
    def setParams(self,symbol:str=None,market:int=None,hangye:str=None,gainian:str=None,diyu:str=None,listing_date:str=None,category:int=0):
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            hangye (str): 行业名称 例如 汽车
            gainian (str): 概念名称 例如 5G
            diyu (str): 地域名称 例如 北京
            listing_date (str): 上市日期 %Y-%m-%d 这个可以用查找次新股
        """
        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "hangye":hangye,
            "gainian":gainian,
            "diyu":diyu,
            "listing_date":listing_date,
            "category":category

        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("parseResponse  "+__name__+" ")

        return datas


        