from dsx.parser.base import BaseParser
from config.logconfig import logger

class RegisterParser(BaseParser):
    def setParams(self, *args, **xargs):
        """构建请求参数

        Returns:
            _type_: _description_
        """
        send_pkg = ""
        # logger.debug("构造请求参数,封装成发送的数据包 send_pkg")
        self.send_pkg = send_pkg
        
    
    def parseResponse(self, datas):
        """解析返回的数据

        Args:
            data (str): 服务端返回的数据
        """

        logger.debug("执行 "+__name__+" 数据解析方法")
        return datas



        