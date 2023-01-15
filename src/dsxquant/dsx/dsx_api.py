import json
import socket
import struct
import threading
from config import config
from config.logconfig import logger
from dsx.parser.base import BaseParser
from dsx.parser.get_quotes import GetQuotesParser
from dsx.parser.register import RegisterParser
from dsx.parser.get_kline import GetKlinesParser

class DsxApi(object):
    client:socket.socket = None
    # 调用中的api线程 {apiname,apihandle}
    apis = {}
    # 异步订阅线程
    recv_thread = None
    # 是否关闭
    is_close = False

    def __init__(self,ip:str=config.server_ip,port:int=config.port,
    app_id:str=config.app_id,app_secret:str=config.app_secret,
    email:str=config.email,sync:bool=True,debug:bool=config.DSXDEBUG) -> None:
        # load_logging_cfg()
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

    @staticmethod
    def asyncconnect():
        """异步订阅服务器

        Returns:
            DsxApi: 返回实例本身
        """
        dsx = DsxApi(sync=False)
        return dsx.connect()

    def connect(self):
        """连接服务器

        Returns:
            DsxApi: 返回实例本身
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(config.CONNECT_TIMEOUT)
        logger.debug("connecting to server : %s on port :%d sync:%s" % (self.ip, self.port,self.sync))
        try:
            self.client.connect((self.ip, self.port))
            
        except socket.timeout as e:
            logger.error(e)
            logger.debug("connection expired")
            return False
        logger.debug("connected!")

        self.setup()
        if self.sync==False:
            # 启用订阅模式
            self._start_recv()

        return self

    def disconnect(self):
        if self.client:
            logger.debug("disconnecting...")
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                if not self.recv_thread: self.client.close()
            except Exception as e:
                logger.debug(str(e))
            logger.debug("disconnected")
    
    def close(self):
        logger.debug("close socket ....")
        self.sync = True
        self.is_close = True
        self.disconnect()
    
    def _save_api(self,api:BaseParser):
        if self.sync==False:
            self.apis[api.api_name] = api
        return True

    def _start_recv(self):
        self.recv_thread = threading.Thread(target=self._recv)
        self.recv_thread.start()
        
    def _recv(self):
        """订阅模式启动循环消息接收
        """
        while(self.sync==False):
            try:
                if self.is_close or self.sync : break
                head_buf = self.client.recv(config.RSP_HEADER_LEN)
                if self.is_close  or self.sync: break
                if len(head_buf) == config.RSP_HEADER_LEN:
                    # 解包头部长度
                    header_size = struct.unpack("i", head_buf)
                    body_buf = bytearray()
                    body_buf = self.client.recv(header_size[0])
                    # 解码字符串
                    body_info = body_buf.decode('utf-8')
                    # 还原json字典信息
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
            except socket.timeout as ex:
                # 超时处理
                logger.error("_revc timed out, server_ip=%s port=%d" % (self.ip,self.port))
                # logger.error(ex)
            except Exception as ex:
                logger.error(ex)
        # 关闭
        try:
            if self.is_close and self.sync:self.client.close()
        except Exception as ex:
            logger.error(ex)
                
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def cancel(self,parser:BaseParser):
        """取消订阅的接口

        Args:
            api_name (str): 接口名称

        Returns:
            bool: 是否成功
        """
        return parser.cancel()


    
    @staticmethod
    def reg(email):
        """注册
        连接成功服务器后即发送注册协议，如果注册成功会给邮箱发送 app_id 和 app_secret
        用户凭借app应用信息登录服务器并开始业务调用

        Args:
            ip (string): 服务器IP地址
            port (int): 端口
            email (string): 注册邮箱
        """
        # logger.debug("开始注册流程...")
        dsx = DsxApi(email=email)
        if dsx.connect():
            dsx.register(email)
            dsx.close()
            return True
        
        return None

    # 接口
    # 注册接口
    def register(self,email):
        """注册
        """
        # 请求注册接口
        r =  RegisterParser(self.client)
        r.setParams(email)
        return r.call_api()

    # 请求实时行情接口
    def get_quotes(self,symbols:list,callback:callable=None):
        """请求实时行情

        Args:
            symbol (str): 证券代码
        """
        # logger.debug("开始请求股票实时行情")
         # 请求行情接口
        r =  GetQuotesParser(self.client,self.sync,callback)
        r.setParams(symbols)
        if(not self.sync): self._save_api(r)
        return r.call_api()

    def get_klines(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,callback:callable=None):
        """请求历史K线图

        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            page (int, optional): 页码. Defaults to 1.
            page_size (int, optional): 每页大小. Defaults to 320.
            fq (str, optional): 复权类型. Defaults to config.FQ.DEFAULT.
            callback (callable, optional): 回调函数. Defaults to None.

        Returns:
            _type_: 历史行情数据
        """
        r =  GetKlinesParser(self.client,self.sync,callback)
        r.setParams(symbol,market,page,page_size,fq)
        if(not self.sync): self._save_api(r)
        return r.call_api()