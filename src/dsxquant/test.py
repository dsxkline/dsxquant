import time
from config.logconfig import logger
from dsx.dsx_api  import DsxApi
from config.config import MARKET 

# 获取股票实时行情
def quotes_callback(response):
    logger.debug(response)

def kline_callback(response):
    logger.debug(response)
    
if __name__=="__main__":
    # 注册
    # DsxApi.reg("192.168.1.1",8080,"dangfm@qq.com")
    # 连接服务器
    app_id = "123333"
    app_secret = "xkljlkdjfoeiofjeiof"
    # 同步模式
    # dsx = DsxApi("192.168.1.1",8080,app_id,app_secret)
    # if dsx.connect():
    #     quote = dsx.get_quotes(("000001",MARKET.SH))
    #     logger.debug(quote)
    #     time.sleep(10)

    # 异步订阅模式
    dsx_async = DsxApi("192.168.1.1",8080,app_id,app_secret,sync=False)
    if dsx_async.connect():
        # 异步请求实时行情接口，服务器会主动推送实时行情
        q = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        logger.debug(q)
        
        q = dsx_async.get_klines("000001",MARKET.SZ,callback=kline_callback)
        logger.debug(q)
   