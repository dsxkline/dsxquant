from dsxquant.dataser.parser.base import BaseParser
from dsxquant.config.logconfig import logger

class LoginParser(BaseParser):

    def setApiName(self):
        self.api_name = "login"

    def setParams(self, app_id,app_secret):
        """构建请求参数
        如果还没有应用信息，需调用 DsxApi.reg(email) 注册后会发送app_id到您的邮箱

        Args:
            app_id (str): 应用ID
            app_secret (str): 应用密钥
        """
        self.send_datas = self.transdata({
            "app_id":app_id,
            "app_secret":app_secret
        })
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            data (str): 服务端返回的数据
        """

        # logger.debug("parseResponse "+__name__+"")
        return datas



        