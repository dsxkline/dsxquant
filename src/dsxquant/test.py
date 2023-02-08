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
                model = Json2Model(item).trans_model(QuoteModel)
                result.append(model)
                
                logger.debug(model.__dict__)

    pass

# 获得历史K线数据
def kline_callback(response:dict):
    logger.debug(response.get("msg"))
    
if __name__=="__main__":
    # 注册邮箱
    email = "dangfm@qq.com"
    # 服务器地址
    server_ip = "43.137.50.28"
    # 服务器端口
    port = 8085
    # 应用ID
    app_id = "4719942393120423937"
    # 应用密码
    app_secret = "yiLxSA4P0C0HltAuQb9NjjYehWXYcgCm"

    # server_ip = "127.0.0.1"
    # app_id = "4719939614565990401"
    # app_secret = "Hew6bf18I7O71ihZ5CPMdCBgZzXuHRwt"

    debug = True

    DsxApi.set_debug(debug)
    # 注册
    success = DsxApi.reg(server_ip,port,email)
    if success:
        logger.info("register success")
        logger.debug(success)

    # 同步模式
    dsx = DsxApi(server_ip,port,app_id,app_secret)
    if dsx.connect():
        quote = dsx.get_quotes([("000001",MARKET.SH),("600000",MARKET.SH)])
        if quote:
            if quote["success"]:
                data = quote["data"]
                result = []
                # 转成model
                model = Json2Model(data).trans_model(QuoteModel)
                result.append(model)

        logger.debug(quote)

        quote = dsx.get_finance("000001",MARKET.SH)
        # logger.debug(quote)

        # quote = dsx.get_stocks("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dsx.get_klines("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dsx.get_factors("000001",MARKET.SZ)
        # logger.debug(quote)

        quote = dsx.get_sharebonus("000001",MARKET.SZ)
        logger.debug(quote)

        quote = dsx.get_translist("000001",MARKET.SZ)
        logger.debug(quote)

        quote = dsx.get_timeshring("000001",MARKET.SZ)
        logger.debug(quote)

        # time.sleep(10)
        dsx.close()

    # logger.debug("开启异步订阅模式")
    # 异步订阅模式
    dsx_async = DsxApi.asyncconnect(server_ip,port,app_id,app_secret)
    if dsx_async:
        # # 异步请求实时行情接口，服务器会主动推送实时行情
        quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
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
        
        # quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        # time.sleep(5)
        # dsx_async.close() 
        pass