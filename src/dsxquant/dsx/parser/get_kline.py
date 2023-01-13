from dsx.parser.base import BaseParser
from config.logconfig import logger
from config.config import FQ
import json
class GetKlinesParser(BaseParser):
    
    def setParams(self, symbol:str,market:int,page:int=1,page_size:int=320,fq:str=FQ.DEFAULT):
        #print(symbol)
        """构建请求参数
        Args:
            symbol (str): 证券代码
            market (int): 市场代码
        Returns:
            _type_: _description_
        """
        self.api_name = "kline"
        # logger.debug("构造请求参数,封装成发送的数据包 send_pkg")
        datas = self.transdata(self.api_name,{
            symbol:symbol,
            market:market,
            page:page,
            page_size:page_size,
            fq:fq
        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            body_buf (byte): 服务端返回的字节流
        """

        logger.debug("执行  "+__name__+"  数据解析方法")
        return datas




        