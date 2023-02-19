from datas.parser.base import BaseParser
from config.logconfig import logger
import json

from common.json2model import Json2Model
from datas.models.quotes import QuoteModel
class GetQuotesParser(BaseParser):

    def setApiName(self):
        self.api_name = "quotes"
    
    def setParams(self, symbols:list):
        #print(symbols)
        """构建请求参数
        Args:
            symbols (list): 证券代码数组 ("000001",0) 或 ["000001",0] 或者 [["000001",0],["000001",1]....]

        """
        datas = self.transdata({
            "symbols":symbols
        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("parseResponse  "+__name__+" ")

        return datas


        