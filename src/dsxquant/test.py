import time
from config import config
from config.logconfig import logger
from dsx.dsx_api  import DsxApi
from config.config import MARKET 

# 获取股票实时行情
def quotes_callback(response):
    logger.debug(response)

# 获得历史K线数据
def kline_callback(response):
    logger.debug(response)
    
if __name__=="__main__":
    # 注册
    success = DsxApi.reg(config.email)
    if success:
        logger.info("register success")
        logger.debug(success)

    # 同步模式
    dsx = DsxApi()
    if dsx.connect():
        quote = dsx.get_quotes(("000001",MARKET.SH))
        logger.debug(quote)
        # time.sleep(10)
        dsx.close()

    # logger.debug("开启异步订阅模式")
    # 异步订阅模式
    dsx_async = DsxApi.asyncconnect()
    if dsx_async:
        # 异步请求实时行情接口，服务器会主动推送实时行情
        quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        # logger.debug(quote)
        
        kline = dsx_async.get_klines("000001",MARKET.SZ,callback=kline_callback)
        # logger.debug(kline)

        time.sleep(5)

        success = dsx_async.cancel(quote)
        if success!=None:
            logger.debug("cancel success:"+quote.api_name)
        else:
            logger.debug("cancel fail:"+quote.api_name)

        success = dsx_async.cancel(kline)
        if success!=None:
            logger.debug("cancel success:"+kline.api_name)
        else:
            logger.debug("cancel fail:"+kline.api_name)
        
        time.sleep(10)
        dsx_async.close()
   