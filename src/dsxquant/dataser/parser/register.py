from dsxquant.dataser.parser.base import BaseParser

class RegisterParser(BaseParser):

    def setApiName(self):
        self.api_name = "reg"

    def setParams(self, email,findapp:bool=False):
        """构建请求参数
        """
        self.send_datas = self.transdata({
            "email":email,
            "findapp":findapp
        })
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            data (str): 服务端返回的数据
        """

        # logger.debug("parseResponse "+__name__+"")
        return datas



        