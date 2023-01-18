from dsx.parser.base import BaseParser
from config.logconfig import logger

class HeartParser(BaseParser):

    def setApiName(self):
        self.api_name = "heart"

    def setParams(self, app_id,app_secret):
        """构建请求参数

        Returns:
            _type_: _description_
        """
        # logger.debug("构造请求参数,封装成发送的数据包 send_pkg")
        self.send_datas = self.transdata()
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            data (str): 服务端返回的数据
        """

        # logger.debug("parseResponse "+__name__+"")
        return datas



        