import json
import socket
import struct
import threading
import time
from config.logconfig import logger
from common import fn
from config import config
import gzip

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

    def __init__(self, client:socket.socket,sync:bool=True,callback:callable=None,enable_zip:bool=False):
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
        # 是否启用zip
        self.enable_zip = enable_zip
        # 设置好api的名称
        self.setApiName()
        
        # logger.debug("base parser init ...")
    
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
        result = False
        try:
            
            if self.sync:
                self._send()
                result = self._call_api()
            else:
                # 异步send
                threading.Thread(target=self._send).start()
                result = self

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

        return result
    def _send(self):
        try:
            with BaseParser.lock:
                # 设置一些公共信息
                self.setup()
                # 第一步：将json格式的数据转换为字符串
                body_info = not self.send_datas == None and json.dumps(self.send_datas) or ''
                # 第二步：对数据body_info进行编码为二进制数据
                body_pkg = body_info.encode('utf-8')
                if(self.send_datas != None and self.enable_zip):
                    logger.debug("ungzip size:%d",len(body_pkg))
                    logger.debug(body_pkg)
                    body_pkg = gzip.compress(body_pkg)
                    logger.debug("gzip size:%d",len(body_pkg))
                # 第三步：使用python中struct模块对数据的长度进行编码为固定长度的数据，这是struct模块的特点，能将任何长度的数据编码为固定长度的数据
                send_size = len(body_pkg)
                # 头包
                header_pkg = struct.pack(config.PACK_TYPE, send_size)
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
        except Exception as ex:
            logger.error(ex)
        # logger.debug("_send:"+self.send_result.__str__())
        # logger.debug(self.send_pkg)

    def _call_api(self):

        if self.send_result != len(self.send_pkg):
            logger.debug("send bytes error")
            raise SendRequestPkgFails("send fails")
        else:
            try:
                # 接收客户端发送过来的数据，因为使用了struct模块中"i"模式，它对任何长度的数据加密出来的长度为固定4字节，所以接收这里使用4
                head_buf = self.client.recv(self.rsp_header_len)
                if len(head_buf) == self.rsp_header_len:
                    # 解包头部长度
                    header_size = struct.unpack(config.PACK_TYPE, head_buf)
                    body_buf = bytearray()
                    body_buf = self.client.recv(header_size[0])
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


