from datas.parser.base import BaseParser
from config.logconfig import logger
import json

from common.json2model import Json2Model
from datas.models.quotes import QuoteModel
class GetFactorsParser(BaseParser):

    def setApiName(self):
        self.api_name = "factors"
    
    def setParams(self, symbol:str,market:int):
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
        """
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

        # logger.debug("parseResponse  "+__name__+" ")

        return datas


        