import json
import socket
import struct
import threading
import time
import traceback
from dsxquant.config.logconfig import logger
from dsxquant.common import fn
from dsxquant.config import config
import gzip
import pandas
from typing import Union,TypeVar,Callable

from dsxquant.common.json2model import Json2Model
from dsxquant.dataser.models.result import ResultModel
from dsxquant.common.cache import CacheHelper

T = TypeVar("T")

class SocketClientNotReady(BaseException):
    pass

class SendPkgNotReady(BaseException):
    pass

class SendRequestPkgFails(BaseException):
    pass

class ResponseHeaderRecvFails(BaseException):
    pass

class ResponseRecvFails(BaseException):
    pass

class BaseParser(object):
    # 锁，主要是发送数据的时候防止并发
    lock = threading.Lock()
    reclock = threading.Lock()

    def __init__(self, client:socket.socket,sync:bool=True,callback=None):
        self.client = client
        # 发送数据字符串
        self.send_datas = None
        # 发送包
        self.send_pkg = None
        # 包头子节长度
        self.rsp_header_len = config.HEADER_LEN
        # 异步长连接回调
        self.call_back = callback
        # sync=True 同步直接收数据
        self.sync = sync
        # 请求ID
        self.request_id = fn.create_unique_id()
        # 发送后返回
        self.send_result = None
        # 定义接口协议名称
        self.api_name = None
        # 返回结果
        self.result:dict = None
        # 缓存数据
        self.cache = None
        # 是否开启缓存
        self.enable_cache = False
        # 设置好api的名称
        self.setApiName()
        
        # logger.debug("base parser init ...")
    
    def open_cache(self):
        self.enable_cache = True
    
    def setApiName(self):
        pass

    def setParams(self, *args, **xargs):
        """
        构建请求
        :return:
        """
        pass
    def transdata(self,datas={},cancel=None):
        td = {
            "act":self.api_name,
            "sync":self.sync,
            "request_id":self.request_id,
            "params":datas
        }
        if cancel==True:
            td["cancel"] = cancel
        return td

    def parseResponse(self, datas):
        pass

    def setup(self):
        pass

    def cancel(self):
        """取消订阅
        """
        self.send_datas = self.transdata(cancel=True)
        # logger.debug("cancel "+json.dumps(self.send_datas))
        return self.call_api()

    def call_api(self):
        # logger.debug("执行base统一发送方法")
        result = None
        try:
            if self.sync:
                self._send()
                result = self._call_api()
            else:
                # 异步send
                threading.Thread(target=self._send).start()

        except SocketClientNotReady as ex:
            logger.error(ex)
        except SendRequestPkgFails as ex:
            logger.error(ex)
        except ResponseRecvFails as ex:
            logger.error(ex)
        except ResponseHeaderRecvFails as ex:
            logger.error(ex)
        except json.JSONDecodeError as ex:
            logger.error(ex)
        except Exception as ex:
            logger.error(ex)
        self.result = result
        return self
    def _send(self):
        if self.cache: return
        try:
            with BaseParser.lock:
                # 设置一些公共信息
                self.setup()
                # 第一步：将json格式的数据转换为字符串
                body_info = not self.send_datas == None and json.dumps(self.send_datas) or ''
                # 第二步：对数据body_info进行编码为二进制数据
                body_pkg = body_info.encode('utf-8')
                if(self.send_datas != None and config.ENABLE_GZIP):
                    # logger.debug("ungzip size:%d",len(body_pkg))
                    # logger.debug(body_pkg)
                    body_pkg = gzip.compress(body_pkg)
                    # logger.debug("gzip size:%d",len(body_pkg))
                # 第三步：使用python中struct模块对数据的长度进行编码为固定长度的数据，这是struct模块的特点，能将任何长度的数据编码为固定长度的数据
                send_size = len(body_pkg)
                # 头包
                header_pkg = struct.pack(config.PACK_TYPE, (config.ENABLE_GZIP==True and 1 or 0), send_size)
                # 总包
                self.send_pkg = bytearray()
                # 组装完成
                self.send_pkg.extend(header_pkg)
                self.send_pkg.extend(body_pkg)
                # logger.debug("_send:%s" % self.send_pkg)
                if self.client==None:
                    return SocketClientNotReady("client is none")
                # 发送包成功返回包大小
                self.send_result = self.client.send(self.send_pkg)
        except socket.error as ex:
            pass
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error(ex)
        # logger.debug("_send:"+self.send_result.__str__())
        # logger.debug(self.send_pkg)

    def _call_api(self):

        # 如果有缓存，启用缓存数据
        if self.cache:
            result = ResultModel().show("缓存数据",True,0,self.cache,self.request_id,self.api_name).dict()
            return result

        if self.send_result != len(self.send_pkg):
            logger.debug("send bytes error")
            raise SendRequestPkgFails("send fails")
        else:
            try:
                with BaseParser.reclock:
                    # 接收客户端发送过来的数据，因为使用了struct模块中"i"模式，它对任何长度的数据加密出来的长度为固定4字节，所以接收这里使用4
                    head_buf = self.client.recv(self.rsp_header_len)
                    if len(head_buf) == self.rsp_header_len:
                        # 解包头部长度
                        header_size = struct.unpack(config.PACK_TYPE, head_buf)
                        config.ENABLE_GZIP = bool(header_size[0])
                        body_size = header_size[1]
                        body_buf = bytearray()
                        body_len = len(body_buf)
                        while body_len<body_size:
                            b_buf = self.client.recv(body_size-body_len)
                            body_buf.extend(b_buf)
                            body_len = len(body_buf)
                        if config.ENABLE_GZIP:
                            body_buf = gzip.decompress(body_buf)
                        # 解码字符串
                        body_info = body_buf.decode('utf-8')
                        
                        # 还原json字典信息
                        body_info = json.loads(body_info)
                        
                        # logger.debug(body_info)
                        return self.parseResponse(body_info)
                    else:
                        logger.error("head_buf is not 0x4")
                        logger.error(head_buf)
                        raise ResponseHeaderRecvFails("head_buf is not 0x4")

            except socket.timeout as ex:
                raise ResponseRecvFails("socket timeout")
            except json.JSONDecodeError as ex:
                raise ex
            except Exception as ex:
                raise ex
            
    def datas(self,cls:Callable[...,T]=None) -> ResultModel:
        if self.result==None:return ResultModel().show_error("返回值为空")
        if cls!=None:
            if self.result:
                if self.result["success"]:
                    data = self.result["data"]
                    # 转成model
                    model = Json2Model(data).trans_model(cls)
                    self.result["data"] = model
        return Json2Model(self.result).trans_model(ResultModel)
    
    def dataframe(self) ->Union[pandas.DataFrame,pandas.Series]:
        """转成pandas对象
        """
        if self.result:
            data = "data" in self.result.keys() and self.result.get("data") or None
            if data:
                if type(data)==dict:
                    return pandas.DataFrame(data.values(),data.keys())
                else:
                    return pandas.Series(data)
        return pandas.DataFrame()
    
    def series(self) ->Union[pandas.DataFrame,pandas.Series]:
        """转成pandas对象
        """
        if self.result:
            data = "data" in self.result.keys() and self.result.get("data") or None
            if data:
                if type(data)==list:
                    return pandas.Series(data)
                else:
                    return pandas.DataFrame(data)
        return pandas.Series()
    
    def csv(self,file_path:str=None) ->Union[list,dict ,None]:
        """转成csv文件格式

        Args:
            file_path (str, optional): 保存路径. Defaults to None.

        Returns:
            str: return csv str
        """
        if not self.series().empty:
            if file_path:
                self.series().to_csv(file_path)
            return self.datas().data



