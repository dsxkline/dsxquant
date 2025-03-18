from dsxquant.dataser.parser.base import BaseParser
class GetQuotesParser(BaseParser):

    def setApiName(self):
        self.api_name = "quotes"
    
    def setParams(self, symbols:any):
        #print(symbols)
        """构建请求参数
        Args:
            symbols (list|str): 证券代码数组 ("000001",0) 或 ["000001",0] 或者 [["000001",0],["000001",1]....] 或者 "sh000001,sz000001...."

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


        