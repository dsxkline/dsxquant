from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
import gzip
import json
import socket
import struct
import threading
import time
import traceback
from typing import Union

from deprecated import deprecated
from dsxquant.config import config
from dsxquant.config.logconfig import logger
from dsxquant.dataser.parser.base import BaseParser
from dsxquant.dataser.parser.get_quotes import GetQuotesParser
from dsxquant.dataser.parser.register import RegisterParser
from dsxquant.dataser.parser.get_kline import GetKlinesParser
from dsxquant.dataser.parser.login import LoginParser
from dsxquant.dataser.parser.heart import HeartParser
from dsxquant.dataser.parser.get_finance import GetFinanceParser
from dsxquant.dataser.parser.get_stocks import GetStocksParser
from dsxquant.dataser.parser.get_factors import GetFactorsParser
from dsxquant.dataser.parser.get_sharebonus import GetShareBonusParser
from dsxquant.dataser.parser.get_timesharing import GetTimeSharingParser
from dsxquant.dataser.parser.get_translist import GetTransListParser
from dsxquant.dataser.parser.get_category import GetCategoryParser
from dsxquant.dataser.models.result import ResultModel
from dsxquant.dataser.parser.sub_all_quotes import SubAllQuotesParser
from dsxquant.dataser.parser.get_structure import GetStructureParser
from dsxquant.common.cache import CacheHelper

class WithExpationFails(BaseException):
    pass

class DsxDataser(object):

    lock = threading.Lock()
    debug = False

    def __init__(self,ip:str=config.DEFAULT_SERVER_IP,port:int=config.DEFAULT_PORT,
    app_id:str=None,app_secret:str=None,
    email:str=None,sync:bool=True) -> None:
        self.ip = ip
        self.port = port
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        self.sync = sync
        self.enable_zip = True
        self.connected = False
        self.__init()

    def __init(self):
        self.client:socket.socket = None
        # 调用中的api句柄 {apiname,apihandle}
        self.apis = {}
        # 是否关闭
        self.is_close = False
        # 开个线程池
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.pool2 = ThreadPoolExecutor(max_workers=10)
        self.connection_times = 0
        # 是否需要重连
        self.need_connect = False
        # 异步接收线程
        self.recv_thread = None
        self.__close_callback = None
    
    def __setup(self):
        pass

    @staticmethod
    def asyncconnect(ip:str=config.DEFAULT_SERVER_IP,port:int=config.DEFAULT_PORT,app_id:str=None,app_secret:str=None):
        """异步订阅服务器

        Returns:
            DsxDataser: 返回实例本身
        """
        dsx = DsxDataser(ip,port,app_id,app_secret,sync=False)
        return dsx.connect()
    
    # def asyncconnect(self):
    #     self.sync = False
    #     return self.connect()

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
            DsxDataser: 返回实例本身
        """
        self.connection_times += 1
        self.need_connect = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(config.CONNECT_TIMEOUT)
        if DsxDataser.debug : logger.debug("connecting to server : %s on port :%s sync:%s" % (self.ip, self.port,self.sync))
        try:
            self.client.connect((self.ip, self.port))
        except socket.timeout as e:
            logger.error(e)
            if DsxDataser.debug : logger.debug("connection expired")
            # 异步连接超时重连
            if self.sync==False:
                time.sleep(10)
                return self.connect(islogin)
            return False
        except socket.error as e:
            logger.error(e)
            return False
        except Exception as ex:
            logger.error(traceback.format_exc())
            return False
        # 登录
        if self.app_id!="" and self.app_secret!="" and islogin:
            result = self.login().datas()
            if result:
                success = result.success
                if success==False:
                    logger.info(result.msg)
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
        if DsxDataser.debug : logger.debug("connected!")
        return self

    def disconnect(self):
        if self.client:
            if DsxDataser.debug : logger.debug("disconnecting...")
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                # logger.debug(traceback.format_exc())
                pass
            if DsxDataser.debug : logger.debug("disconnected")
        
    
    def close(self):
        if DsxDataser.debug : logger.debug("close socket ....")
        self.sync = True
        self.is_close = True
        self.connected = False
        self.disconnect()
    
    def close_callback(self,callback):
        """关闭后回调函数

        Args:
            callback (function): 回调函数，会带是否需要重连标识，用户需根据标识自己实现重连机制
        """
        self.__close_callback = callback
        
    
    def __save_api(self,api:BaseParser):
        if self.sync==False:
            self.apis[api.api_name] = api
        return True

    def _start_recv(self):
        self.recv_thread = threading.Thread(target=self._recv)
        self.recv_thread.start()
        
    
    def reconnect(self,*args):
        """断线重连
        """
        # 线程结束后，检查是否需要重连
        if not self.need_connect: return
        self.close()
        # time.sleep(10)
        self.sync = False
        self.is_close = False
        if DsxDataser.debug : logger.debug("正在重新连接....")
        self.connect()
        return self
    
    def _recv(self):
        """订阅模式启动循环消息接收
        """
        while(self.sync==False):
            try:
                with DsxDataser.lock:
                    if self.is_close or self.sync : break
                    head_buf = self.client.recv(config.HEADER_LEN)
                    if self.is_close  or self.sync: break
                    body_buf = bytearray()
                    if len(head_buf) == config.HEADER_LEN:
                        # 解包头部长度
                        header_size = struct.unpack(config.PACK_TYPE, head_buf)
                        self.enable_zip = bool(header_size[0])
                        body_size = header_size[1]
                        body_buf = self.client.recv(body_size)
                        while(len(body_buf)<body_size):
                            # 继续接收 处理大数据，有可能一个数据流大于缓冲区
                            temp_size = body_size - len(body_buf)
                            if temp_size<=0 : break
                            body_buf += self.client.recv(temp_size)
                        if self.enable_zip:
                            # 解压
                            body_buf = gzip.decompress(body_buf)
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
                                    api.result = api.parseResponse(body_info)
                                    api.call_back(api)
                            del api
                        del body_info
                    else:
                        if DsxDataser.debug : logger.debug("_revc head buf is wrong...")
                        # 服务器关闭连接后会返回数据长度为0
                        self.need_connect = True
                        break
                    # 清理
                    del head_buf,body_buf
            except socket.timeout as ex:
                # 超时处理
                logger.error("_revc timed out, server_ip=%s port=%d" % (self.ip,self.port))
                time.sleep(1)
                # 重连
                self.need_connect = True
                break
                # logger.error(ex)
            except socket.error as ex:
                logger.error(ex)
                # IO通信异常退出
                self.need_connect = True
                break
            except Exception as ex:
                logger.error(traceback.format_exc())
                # logger.error(head_buf)
                # logger.error(body_buf)
        # 关闭
        try:
            self.close()
        except Exception as ex:
            logger.error(traceback.format_exc())
        if DsxDataser.debug: logger.debug("_revc end")
        
        if self.__close_callback:
            time.sleep(3)
            self.__close_callback(self.need_connect)
    
                
    
    def __enter__(self):
        # with 语法的时候自动连接
        if self.connect()!=False:
            return self
        

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        # 释放资源
        print("Closing resource")
        
        # 如果发生异常，打印异常信息
        if exc_type is not None:
            print(f"Caught exception: {exc_type}, {exc_val}")
        
        # 如果返回False，异常会被重新抛出
        # 如果返回True，异常会被吞噬
        return False

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
        DsxDataser.debug = debug
    
    @staticmethod
    def reg(email:str,ip:str=config.DEFAULT_SERVER_IP,port:int=config.DEFAULT_PORT,findapp:bool=False) ->ResultModel:
        """注册
        连接成功服务器后即发送注册协议，如果注册成功会给邮箱发送 app_id 和 app_secret
        用户凭借app应用信息登录服务器并开始业务调用

        Args:
            ip (string): 服务器IP地址
            port (int): 端口
            email (string): 注册邮箱
            findapp (bool): 查询应用信息
        """
        # logger.debug("开始注册流程...")
        dsx = DsxDataser(ip,port,email=email)
        if dsx.connect(islogin=False):
            result = dsx.register(email,findapp=findapp).datas()
            dsx.close()
            return result
        
        return ResultModel().show_error("注册失败")

    # 接口
    # 注册接口
    def register(self,email:str,findapp:bool=False):
        """注册
        """
        # 请求注册接口
        r =  RegisterParser(self.client)
        r.setParams(email,findapp=findapp)
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
            # if DsxDataser.debug : logger.debug(response)
            pass
        r =  HeartParser(self.client,False,heart_response)
        r.setParams(self.app_id,self.app_secret)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    def get_category(self,category_id:int=0):
        """请求分类信息

        Args:
            category_id (int): 分类代码 0=行业 1=概念 2=地域
        """
        if not self.connected:return
        r =  GetCategoryParser(self.client)
        r.setParams(category_id)
        return r.call_api()

    def get_hangye(self):
        """请求行业分类
        """
        return self.get_category(0)
    def get_gainian(self):
        """请求概念分类
        """
        return self.get_category(1)
    def get_diyu(self):
        """请求地域分类
        """
        return self.get_category(2)
    
    # 请求证券信息
    def get_stocks(self,market:int=None,symbol:str=None,hangye:str=None,gainian:str=None,diyu:str=None,listing_date:str=None,category:int=0):
        """请求证券详情信息

        Args:
            market (int): 市场编号 
            symbol (str): 证券代码 为空返回市场股票代码列表
        """
        if not self.connected:return
        r =  GetStocksParser(self.client)
        r.setParams(symbol,market,hangye,gainian,diyu,listing_date,category)
        return r.call_api()

    def get_quotes(self,symbols:Union[list,str,tuple]):
        """请求实时行情

        Args:
            symbol (str): 证券代码
        """
        if not self.connected:return
        r =  GetQuotesParser(self.client,self.sync,None)
        r.setParams(symbols)
        if(not self.sync): self.__save_api(r)
        return r.call_api()
    
    def get_price(self,symbols:Union[list,str,tuple]):
        """请求实时行情

        Args:
            symbol (str): 证券代码
        """
        return self.get_quotes(symbols)

    def sub_quotes(self,symbols:Union[list,str,tuple],callback):
        """订阅实时行情
        订阅后系统会持续推行情过来，需要用户自己实现回调函数

        Args:
            symbol (str): 证券代码
        """
        if not self.connected:return
        r =  GetQuotesParser(self.client,self.sync,callback)
        r.setParams(symbols)
        if(not self.sync): self.__save_api(r)
        return r.call_api()
    
    def sub_price(self,symbols:Union[list,str,tuple],callback):
        return self.sub_quotes(symbols,callback)
    
    def sub_all_quotes(self,callback):
        """订阅全市场实时行情

        """
        if not self.connected:return
        r =  SubAllQuotesParser(self.client,self.sync,callback)
        r.setParams()
        if(not self.sync): self.__save_api(r)
        return r.call_api()
        
    def sub_all_price(self,callback):
        return self.sub_all_quotes(callback)

    def get_klines(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,start:str=None,end:str=None,enable_cache:bool=True):
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
        r =  GetKlinesParser(self.client,self.sync,None)
        r.setParams(symbol,market,page,page_size,fq,cycle,start,end,enable_cache)
        if(not self.sync): self.__save_api(r)
        return r.call_api()


    def get_finance(self,symbol,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date="",start:str=None,end:str=None,enable_cache:bool=True):
        """请求财务信息

        Args:
            symbol (str): 证券代码
            market (int): 市场代码
            report_type (config.REPORT_TYPE): 财务报表类型 
            class REPORT_TYPE:
                DEFAULT='index'                 # 财务指标
                PROFIT="profit"                 # 利润表
                CASHFLOW="cashflow"             # 现金流量表
                BALANCESHEET="balancesheet"     # 资产负债表
            report_date (str): 报表日期 %Y-%m-%d，默认为空是取最新日期的报表
           
        Returns:
            dict: 财务数据
        """
        if not self.connected:return
        r =  GetFinanceParser(self.client)
        r.setParams(symbol,market,report_type,report_date,start,end,enable_cache)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    def get_sharebonus(self,symbol:str,market:int,start:str=None,end:str=None,enable_cache:bool=True):
        """请求分红配股信息

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            start (str, optional): 开始日期 %Y-%m-%d Defaults to None.
            end (str, optional): 结束日期 %Y-%m-%d. Defaults to None.

        Returns:
            _type_: _description_
        """
        if not self.connected:return
        r =  GetShareBonusParser(self.client)
        r.setParams(symbol,market,start,end,enable_cache)
        return r.call_api()

    def get_structure(self,symbol:str,market:int,start:str=None,end:str=None,enable_cache:bool=True):
        """请求股本结构信息

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            start (str, optional): 开始日期 %Y-%m-%d Defaults to None.
            end (str, optional): 结束日期 %Y-%m-%d. Defaults to None.

        Returns:
            _type_: _description_
        """
        if not self.connected:return
        r =  GetStructureParser(self.client)
        r.setParams(symbol,market,start,end,enable_cache)
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
    
    @deprecated
    def get_timeshring(self,symbol:str,market:int,trade_date:str="",enable_cache:bool=True):
        """请求分时线

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            trade_date (str, optional): 交易日期 %Y-%m-%d. Defaults to "".

        Returns:
            _type_: _description_
        """
        if not self.connected:return
        r =  GetTimeSharingParser(self.client,self.sync,None)
        r.setParams(symbol,market,trade_date,enable_cache)
        if(not self.sync): self.__save_api(r)
        return r.call_api()
    
    def get_timesharing(self,symbol:str,market:int,trade_date:str="",enable_cache:bool=True):
        """请求分时线

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            trade_date (str, optional): 交易日期 %Y-%m-%d. Defaults to "".

        Returns:
            _type_: _description_
        """
        if not self.connected:return
        r =  GetTimeSharingParser(self.client,self.sync,None)
        r.setParams(symbol,market,trade_date,enable_cache)
        if(not self.sync): self.__save_api(r)
        return r.call_api()

    def sub_timeshring(self,symbol:str,market:int,trade_date:str="",callback=None):
        """订阅分时线
        订阅后会主动推送每分钟的分时数据过来，用户需自行实现callback函数

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            trade_date (str, optional): 交易日期 %Y-%m-%d. Defaults to "".
            callback (_type_, optional): 回调函数. Defaults to None.

        Returns:
            _type_: _description_
        """
        if not self.connected:return
        r =  GetTimeSharingParser(self.client,self.sync,callback)
        r.setParams(symbol,market,trade_date)
        if(not self.sync): self.__save_api(r)
        return r.call_api()
    
    def get_translist(self,symbol:str,market:int,trade_date:str="",page:int=1,page_size:int=10,enable_cache:bool=True):
        """获取逐笔交易信息

        Args:
            symbol (str): 证券代码
            market (int): 市场编号
            trade_date (str, optional): 交易日期 %Y-%m-%d. Defaults to "".
            page (int, optional): 页码. Defaults to 1.
            page_size (int, optional): 每页大小. Defaults to 10.

        Returns:
            _type_: GetTransListParser
        """
        if not self.connected:return
        r =  GetTransListParser(self.client)
        r.setParams(symbol,market,trade_date,page,page_size,enable_cache)
        return r.call_api()