import time
from config import config
from config.logconfig import logger
from datas.dsx_datas  import DsxDatas
from config.config import MARKET
from common.json2model import Json2Model
from datas.models.quotes import QuoteModel

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
    # 开启debug
    DsxDatas.set_debug(True)
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

    server_ip = "127.0.0.1"
    app_id = "4719939614565990401"
    app_secret = "Hew6bf18I7O71ihZ5CPMdCBgZzXuHRwt"

    # app_id = None
    # app_secret = None

    # 邮箱注册，注册成功会发送邮件到您的邮箱，请查阅邮箱获得开通的应用信息 app_id app_secret
    success = DsxDatas.reg(server_ip,port,email)
    if success:
        logger.info("register success")
        logger.debug(success)

    # 同步请求模式
    dd = DsxDatas(server_ip,port,app_id,app_secret)
    if dd.connect():
        quote = dd.get_quotes([("000001",MARKET.SH),("600000",MARKET.SH)])
        if quote:
            if quote["success"]:
                data = quote["data"]
                result = []
                # 转成model
                model = Json2Model(data).trans_model(QuoteModel)
                result.append(model)

        logger.debug(quote)

        # quote = dd.get_finance("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dd.get_stocks("000001",MARKET.SZ)
        # logger.debug(quote)

        quote = dd.get_klines("000001",MARKET.SZ,cycle=config.CYCLE.M60,page_size=1000)
        logger.debug(quote)

        # quote = dd.get_factors("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dd.get_sharebonus("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dd.get_translist("000001",MARKET.SZ)
        # logger.debug(quote)

        # quote = dd.get_timeshring("000001",MARKET.SZ)
        # logger.debug(quote)

        # time.sleep(10)
        dd.close()

    # logger.debug("开启异步订阅模式")
    # 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
    dsx_async = DsxDatas.asyncconnect(server_ip,port,app_id,app_secret)
    if dsx_async:
        # # 异步请求实时行情接口，服务器会主动推送实时行情
        quote = dsx_async.get_quotes((("000001",MARKET.SH),("000001",MARKET.SZ)),quotes_callback)
        # logger.debug(quote)
        
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