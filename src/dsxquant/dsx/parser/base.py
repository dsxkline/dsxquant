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
    def __init__(self, client:socket.socket,sync:bool=True,callback:callable=None):
        self.client = client
        # 发送数据字符串
        self.send_datas = None
        # 发送包
        self.send_pkg = None
        # 包头子节长度
        self.rsp_header_len = config.RSP_HEADER_LEN
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
        
        logger.debug("base parser init ...")

    def setParams(self, *args, **xargs):
        """
        构建请求
        :return:
        """
        pass
    def transdata(self,api_name,datas):
        td = {
            "act":api_name,
            "sync":self.sync,
            "request_id":self.request_id,
            "params":datas
        }
        return td

    def parseResponse(self, datas):
        pass

    def setup(self):
        pass

    def call_api(self):
        logger.debug("执行base统一发送方法")
        result = True
        try:
            self._send()
            if self.sync:
                result = self._call_api()

        except SocketClientNotReady as ex:
            result = ex
            logger.debug(ex)
        except SendRequestPkgFails as ex:
            result = ex
            logger.debug(ex)
        except ResponseRecvFails as ex:
            result = ex
            logger.debug(ex)
        except ResponseHeaderRecvFails as ex:
            result = ex
            logger.debug(ex)
        except json.JSONDecodeError as ex:
            result = ex
            logger.debug(ex)

        return result
    def _send(self):
        # 设置一些公共信息
        self.setup()
        # 第一步：将json格式的数据转换为字符串
        body_info = not self.send_datas == None and json.dumps(self.send_datas) or ''
        # 第二步：对数据body_info进行编码为二进制数据
        body_pkg = body_info.encode('utf-8')
        if(self.send_datas != None):
            logger.debug("压缩前大小:%d",len(body_pkg))
            logger.debug(body_pkg)
            body_pkg = gzip.compress(body_pkg)
            logger.debug("压缩后大小:%d",len(body_pkg))
        # 第三步：使用python中struct模块对数据的长度进行编码为固定长度的数据，这是struct模块的特点，能将任何长度的数据编码为固定长度的数据
        send_size = len(body_pkg)
        # 头包
        header_pkg = struct.pack('i', send_size)
        # 总包
        self.send_pkg = bytearray()
        # 组装完成
        self.send_pkg.extend(header_pkg)
        self.send_pkg.extend(body_pkg)
        logger.debug(self.send_pkg)
        if self.client==None:
            return SocketClientNotReady("client is none")
        # 发送包成功返回包大小
        self.send_result = self.client.send(self.send_pkg)
        logger.debug("发送数据:"+self.send_result.__str__())
        logger.debug(self.send_pkg)

    def _call_api(self):

        if self.send_result != len(self.send_pkg):
            logger.debug("send bytes error")
            raise SendRequestPkgFails("send fails")
        else:
            try:
                # 第一步：接收客户端发送过来的数据，因为使用了struct模块中"i"模式，它对任何长度的数据加密出来的长度为固定4字节，所以接收这里使用4
                head_buf = self.client.recv(self.rsp_header_len)
                if len(head_buf) == self.rsp_header_len:
                    # 第二步：解包头部长度
                    header_size = struct.unpack("i", head_buf)
                    body_buf = bytearray()
                    body_buf = self.client.recv(header_size[0])
                    # 第四步：解码字符串
                    body_info = body_buf.decode('utf-8')
                    logger.debug(body_info)
                    # 第五步：还原json字典信息
                    body_info = json.loads(body_info)
                    return self.parseResponse(body_info)
                else:
                    logger.debug("head_buf is not 0x10")
                    raise ResponseHeaderRecvFails("head_buf is not 0x10")

            except socket.timeout as ex:
                raise ResponseRecvFails("socket timeout")
            except json.JSONDecodeError as ex:
                raise ex


