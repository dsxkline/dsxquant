from dsx.parser.base import BaseParser
from config.logconfig import logger
import json
class GetQuotesParser(BaseParser):

    def setApiName(self):
        self.api_name = "finance"
    
    def setParams(self, symbol:str,market:int):
        #print(symbols)
        """构建请求参数
        Args:
            symbols (list): 证券代码数组
        Returns:
            _type_: _description_
        """
        # logger.debug("构造请求参数,封装成发送的数据包 send_pkg")
        datas = self.transdata({
            "symbol":symbol,
            "market":market
        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("执行  "+__name__+"  数据解析方法")

        return datas


        