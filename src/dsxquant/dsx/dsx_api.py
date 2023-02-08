import json
import socket
import struct
import threading
import time
from config import config
from config.logconfig import logger
from dsx.parser.base import BaseParser
from dsx.parser.get_quotes import GetQuotesParser
from dsx.parser.register import RegisterParser
from dsx.parser.get_kline import GetKlinesParser
from dsx.parser.login import LoginParser
from dsx.parser.heart import HeartParser
from dsx.parser.get_finance import GetFinanceParser
from dsx.parser.get_stocks import GetStocksParser
from dsx.parser.get_factors import GetFactorsParser
from dsx.parser.get_sharebonus import GetShareBonusParser
from dsx.parser.get_timesharing import GetTimeSharingParser
from dsx.parser.get_translist import GetTransListParser

class DsxApi(object):

    debug = False

    def __init__(self,ip:str=None,port:int=None,
    app_id:str=None,app_secret:str=None,
    email:str=None,sync:bool=True,enable_zip:bool=False) -> None:
        self.ip = ip
        self.port = port
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        self.sync = sync
        self.enable_zip = enable_zip
        self.connected = False
        self.__init()

    def __init(self):
        self.client:socket.socket = None
        # 调用中的api线程 {apiname,apihandle}
        self.apis = {}
        # 异步订阅线程
        self.recv_thread = None
        # 是否关闭
        self.is_close = False
    
    def __setup(self):
        pass

    @staticmethod
    def asyncconnect(ip:str=None,port:int=None,
    app_id:str=None,app_secret:str=None):
        """异步订阅服务器

        Returns:
            DsxApi: 返回实例本身
        """
        dsx = DsxApi(ip,port,app_id,app_secret,sync=False)
        return dsx.connect()

    def connect(self,islogin=True):
        """连接服务器

        family:
            socket.AF_INET - IPv4(默认)
            socket.AF_INET6 - IPv6
            socket.AF_UNIX - 只能够用于单一的Unix系统进程间通信
        type:
            socket.SOCK_STREAM - 流式socket, for TCP (默认)
            socket.SOCK_DGRAM - 数据报式socket, for UDP
            socket.SOCK_RAW - 原始套接字
            socket.SOCK_RDM - 可靠UDP形式
            socket.SOCK_SEQPACKET - 可靠的连续数据包服务
        Returns:
            DsxApi: 返回实例本身
        """

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(config.CONNECT_TIMEOUT)
        if DsxApi.debug : logger.debug("connecting to server : %s on port :%d sync:%s" % (self.ip, self.port,self.sync))
        try:
            self.client.connect((self.ip, self.port))
        except socket.timeout as e:
            logger.error(e)
            if DsxApi.debug : logger.debug("connection expired")
            return False
        except socket.error as e:
            logger.error(e)
            return False
        except Exception as ex:
            logger.error(ex)
            return False
        # 登录
        if self.app_id!="" and self.app_secret!="" and islogin:
            result = self.login()
            if result:
                success = result["success"]
                if success==False:
                    if DsxApi.debug : logger.debug(result["msg"])
                    return success
            else:
                return False

        self.__setup()
        self.connected = True
        if self.sync==False:
            # 启用订阅模式
            # 异步订阅模式需要启动心跳包
            self.heart()
            self._start_recv()
        if DsxApi.debug : logger.debug("connected!")
        return self

    def disconnect(self):
        if self.client:
            if DsxApi.debug : logger.debug("disconnecting...")
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                if not self.recv_thread: self.client.close()
            except Exception as e:
                logger.debug(str(e))
            if DsxApi.debug : logger.debug("disconnected")
    
    def close(self):
        if DsxApi.debug : logger.debug("close socket ....")
        self.sync = True
        self.is_close = True
        self.connected = False
        self.disconnect()
    
    def __save_api(self,api:BaseParser):
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
                head_buf = self.client.recv(config.HEADER_LEN)
                if self.is_close  or self.sync: break
                if len(head_buf) == config.HEADER_LEN:
                    # 解包头部长度
                    header_size = struct.unpack(config.PACK_TYPE, head_buf)
                    body_buf = bytearray()
                    body_size = header_size[0]
                    body_buf = self.client.recv(body_size)
                    while(len(body_buf)<body_size):
                        # 继续接收 处理大数据，有可能一个数据流大于缓冲区
                        temp_size = body_size - len(body_buf)
                        if temp_size<=0 : break
                        body_buf += self.client.recv(temp_size)
                    # 解码字符串
                    body_info = body_buf.decode('utf-8')
                    body_info = json.loads(body_info)
                    # 得到接口名称
                    rct = body_info["act"]
                    # 得到api调用句柄
                    if self.apis.__len__()>0:
                        api:BaseParser = self.apis.get(rct)
                        # 返回给api回调函数
                        if api!=None:
                            if api.call_back!=None:
                                body_info = api.parseResponse(body_info)
                                api.call_back(body_info)
                else:
                    if DsxApi.debug : logger.debug("_revc head buf is wrong...")
                    # 服务器关闭连接后会返回数据长度为0
                    if len(head_buf)==0:
                        self.close()
                    time.sleep(1)
            except socket.timeout as ex:
                # 超时处理
                logger.error("_revc timed out, server_ip=%s port=%d" % (self.ip,self.port))
                time.sleep(1)
                # 超时重连
                self.close()
                self.connect()
                # logger.error(ex)
            except socket.error as ex:
                logger.error(ex)
                # IO通信异常退出
                self.close()
            except Exception as ex:
                logger.error(ex)
                logger.error(head_buf)
                logger.error(body_buf)
        # 关闭
        try:
            if self.is_close :self.client.close()
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
    def set_debug(debug:bool=False):
        DsxApi.debug = debug
    
    @staticmethod
    def reg(ip:str,port:int,email:str):
        """注册
        连接成功服务器后即发送注册协议，如果注册成功会给邮箱发送 app_id 和 app_secret
        用户凭借app应用信息登录服务器并开始业务调用

        Args:
            ip (string): 服务器IP地址
            port (int): 端口
            email (string): 注册邮箱
        """
        # logger.debug("开始注册流程...")
        dsx = DsxApi(ip,port,email=email)
        if dsx.connect(islogin=False):
            result = dsx.register(email)
            dsx.close()
            return result
        
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
    
    # 登录接口
    def login(self):
        """登录
        """
        # 请求注册接口
        r =  LoginParser(self.client)
        r.setParams(self.app_id,self.app_secret)
        return r.call_api()
    
    # 心跳接口
    def heart(self):
        """心跳包
        """
        # 处理心跳包
        def heart_response(response):
            # if DsxApi.debug : logger.debug(response)
            pass
        r =  HeartParser(self.client,False,heart_response)
        r.setParams(self.app_id,self.app_secret)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    # 请求证券信息
    def get_stocks(self,symbol:str,market:int):
        """请求证券详情信息

        Args:
            symbol (str): 证券代码
        """
        if not self.connected:return
        r =  GetStocksParser(self.client)
        r.setParams(symbol,market)
        return r.call_api()

    def get_quotes(self,symbols:list,callback:callable=None):
        """请求实时行情

        Args:
            symbol (str): 证券代码
        """
        if not self.connected:return
        r =  GetQuotesParser(self.client,self.sync,callback)
        r.setParams(symbols)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    def get_klines(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,callback:callable=None):
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
        if not self.connected:return
        r =  GetKlinesParser(self.client,self.sync,callback)
        r.setParams(symbol,market,page,page_size,fq,cycle)
        if(not self.sync): self.__save_api(r)
        return r.call_api()


    def get_finance(self,symbol,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date=""):
        """请求财务信息

        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            report_type (config.REPORT_TYPE): 财务报表类型
            report_date (str): 报表日期 %Y-%m-%d
           
        Returns:
            dict: 财务数据
        """
        if not self.connected:return
        r =  GetFinanceParser(self.client)
        r.setParams(symbol,market,report_type,report_date)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    def get_sharebonus(self,symbol:str,market:int,start:str=None,end:str=None):
        """请求分红配股信息

        Args:
            symbol (str): 证券代码
            market (str): 市场代码
        """
        if not self.connected:return
        r =  GetShareBonusParser(self.client)
        r.setParams(symbol,market,start,end)
        return r.call_api()
    
    def get_factors(self,symbol:str,market:int):
        """请求复权因子信息

        Args:
            symbol (str): 证券代码
            market (str): 市场代码
        """
        if not self.connected:return
        r =  GetFactorsParser(self.client)
        r.setParams(symbol,market)
        return r.call_api()
    
    def get_timeshring(self,symbol:str,market:int,trade_date:str="",callback:callable=None):
        """请求分时线

        Args:
            symbol (str): 证券代码
            market (str): 市场代码
        """
        if not self.connected:return
        r =  GetTimeSharingParser(self.client,self.sync,callback)
        r.setParams(symbol,market,trade_date)
        if(not self.sync): self.__save_api(r)
        return r.call_api()
    
    def get_translist(self,symbol:str,market:int,trade_date:str=""):
        """请求分时线

        Args:
            symbol (str): 证券代码
            market (str): 市场代码
        """
        if not self.connected:return
        r =  GetTransListParser(self.client)
        r.setParams(symbol,market,trade_date)
        return r.call_api()