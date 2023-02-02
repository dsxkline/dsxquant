import time
from config import config
from config.logconfig import logger
from dsx.dsx_api  import DsxApi
from config.config import MARKET
from common.json2model import Json2Model
from dsx.models.quotes import QuoteModel 

# 获取股票实时行情
def quotes_callback(response:dict):

    # logger.debug(response.get("msg"))
    if response:
        if response["success"]:
            data = response["data"]
            result = []
            # 转成model
            for item in data:
                model = Json2Model(item,QuoteModel).trans_model()
                result.append(model)
                # logger.debug(model.code)

    pass

# 获得历史K线数据
def kline_callback(response:dict):
    logger.debug(response.get("msg"))
    
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
        if quote:
            if quote["success"]:
                data = quote["data"]
                result = []
                # 转成model
                for item in data:
                    model = Json2Model(item,QuoteModel).trans_model()
                    result.append(model)

        logger.debug(quote)

        quote = dsx.get_finance("000001",MARKET.SH)
        logger.debug(quote)

        # time.sleep(10)
        dsx.close()

    # logger.debug("开启异步订阅模式")
    # 异步订阅模式
    dsx_async = DsxApi.asyncconnect()
    if dsx_async:
        # # 异步请求实时行情接口，服务器会主动推送实时行情
        # quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        # # logger.debug(quote)
        
        # kline = dsx_async.get_klines("000001",MARKET.SZ,callback=kline_callback)
        # # logger.debug(kline)

        # time.sleep(10)

        # success = dsx_async.cancel(quote)
        # if success!=None:
        #     logger.debug("cancel success:"+quote.api_name)
        # else:
        #     logger.debug("cancel fail:"+quote.api_name)

        # success = dsx_async.cancel(kline)
        # if success!=None:
        #     logger.debug("cancel success:"+kline.api_name)
        # else:
        #     logger.debug("cancel fail:"+kline.api_name)
        
        quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        # time.sleep(5)
        # dsx_async.close()