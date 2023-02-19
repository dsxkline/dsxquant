from datas.parser.base import BaseParser
from config.logconfig import logger
from config import config
import json
class GetFinanceParser(BaseParser):

    def setApiName(self):
        self.api_name = "finance"
    
    def setParams(self, symbol,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date=""):
        """构建请求参数
        Args:
            symbols (list): 证券代码数组
        Returns:
            _type_: _description_
        """
        datas = self.transdata({
            "symbol":symbol,
            "market":market,
            "report_type":report_type,
            "report_date":report_date,
        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("执行  "+__name__+"  数据解析方法")

        return datas


        