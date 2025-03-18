from dsxquant.dataser.parser.base import BaseParser

class HeartParser(BaseParser):

    def setApiName(self):
        self.api_name = "heart"

    def setParams(self, app_id,app_secret):
        """构建请求参数

        Returns:
            _type_: _description_
        """
        self.send_datas = self.transdata()
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            data (str): 服务端返回的数据
        """

        # logger.debug("parseResponse "+__name__+"")
        return datas



        