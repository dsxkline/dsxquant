import json
import socket
import struct
import threading
from config import config
from config.logconfig import logger,load_logging_cfg
from dsx.parser.base import SendRequestPkgFails
from dsx.parser.base import BaseParser
from dsx.parser.get_quotes import GetQuotesParser
from dsx.parser.register import RegisterParser
from dsx.parser.get_kline import GetKlinesParser

class DsxApi(object):
    client = None
    # 调用中的api线程 {apiname,apihandle}
    apis = {}

    def __init__(self,ip:str,port:int,app_id:str=None,app_secret:str=None,email:str=None,sync:bool=True) -> None:
        load_logging_cfg()
        self.ip = ip
        self.port = port
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        self.sync = sync
        self.init()
        pass

    def init(self):
        pass
    
    def setup(self):
        pass

    def connect(self):
        """

        :param ip:  服务器ip 地址
        :param port:  服务器端口
        :return: 是否连接成功 True/False
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(config.CONNECT_TIMEOUT)
        logger.debug("connecting to server : %s on port :%d" % (self.ip, self.port))
        
        try:
            self.client.connect((self.ip, self.port))
            
        except socket.timeout as e:
            print(str(e))
            logger.debug("connection expired")
            return False
        logger.debug("connected!")

        self.setup()
        if self.sync==False:
            # 启用订阅模式
            self.start_recv()

        return self

    def disconnect(self):
        if self.client:
            logger.debug("disconnecting")
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                logger.debug(str(e))
            logger.debug("disconnected")
    
    def close(self):
        logger.debug("关闭连接....")
        self.disconnect()
    
    def save_api(self,api:BaseParser):
        if self.sync==False:
            self.apis[api.api_name] = api
        return True
    def start_recv(self):
        thread = threading.Thread(target=self.recv)
        thread.start()
        
    def recv(self):
        """订阅模式
        """
        while(self.sync==False):
            # 第一步：接收客户端发送过来的数据，因为使用了struct模块中"i"模式，它对任何长度的数据加密出来的长度为固定4字节，所以接收这里使用4
            try:
                head_buf = self.client.recv(config.RSP_HEADER_LEN)
                if len(head_buf) == config.RSP_HEADER_LEN:
                    # 第二步：解包头部长度
                    header_size = struct.unpack("i", head_buf)
                    body_buf = bytearray()
                    body_buf = self.client.recv(header_size[0])
                    # 第四步：解码字符串
                    body_info = body_buf.decode('utf-8')
                    # 第五步：还原json字典信息
                    body_info = json.loads(body_info)
                    # 得到接口名称
                    rct = body_info["rct"]
                    # 得到api调用句柄
                    if self.apis.__len__()>0:
                        api:BaseParser = self.apis.get(rct)
                        # 返回给api回调函数
                        if api!=None:
                            if api.call_back!=None:
                                body_info = api.parseResponse(body_info)
                                api.call_back(body_info)
            except Exception as ex:
                logger.error(ex)

                
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    @staticmethod
    def reg(ip,port,email):
        """注册
        连接成功服务器后即发送注册协议，如果注册成功会给邮箱发送 app_id 和 app_secret
        用户凭借app应用信息登录服务器并开始业务调用

        Args:
            ip (string): 服务器IP地址
            port (int): 端口
            email (string): 注册邮箱
        """
        logger.debug("开始注册流程...")
        dsx = DsxApi(ip,port,email=email)
        if dsx.connect():
            return dsx.register()
        
        return None

    # 接口
    # 注册接口
    def register(self):
        """注册
        """
        # 请求注册接口
        r =  RegisterParser(self.client)
        r.setParams()
        return r.call_api()

    # 请求实时行情接口
    def get_quotes(self,symbols:list,callback:callable=None):
        """请求实时行情

        Args:
            symbol (str): 证券代码
        """
        logger.debug("开始请求股票实时行情")
         # 请求行情接口
        r =  GetQuotesParser(self.client,self.sync,callback)
        r.setParams(symbols)
        if(not self.sync): self.save_api(r)
        return r.call_api()

    def get_klines(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,callback:callable=None):
        r =  GetKlinesParser(self.client,self.sync,callback)
        r.setParams(symbol,market,page,page_size,fq)
        if(not self.sync): self.save_api(r)
        return r.call_api()