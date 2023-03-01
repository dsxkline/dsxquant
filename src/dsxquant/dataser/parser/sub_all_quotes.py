from dsxquant.dataser.parser.base import BaseParser
class SubAllQuotesParser(BaseParser):

    def setApiName(self):
        self.api_name = "suballquotes"
    
    def setParams(self,):
        #print(symbols)
        """构建请求参数
        """
        datas = self.transdata({})
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("parseResponse  "+__name__+" ")

        return datas


        