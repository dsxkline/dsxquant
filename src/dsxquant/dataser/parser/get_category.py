from dsxquant.dataser.parser.base import BaseParser
class GetCategoryParser(BaseParser):

    def setApiName(self):
        self.api_name = "category"
    
    def setParams(self, category_id:int):
        """构建请求参数
        Args:
            category_id (int): 分类编号 0=行业 1=概念 2=地域
        """
        datas = self.transdata({
            "category_id":category_id,
        })
        self.send_datas = datas
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            datas (str): 服务端返回
        """

        # logger.debug("parseResponse  "+__name__+" ")

        return datas


        