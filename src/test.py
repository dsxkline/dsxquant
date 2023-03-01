import datetime
import time
import dsxquant

if __name__=="__main__":
    # 开启debug
    dsxquant.dataser.set_debug(True)
    # 注册邮箱
    # email = "dangfm@qq.com"
    # 服务器地址
    # server_ip = "129.211.209.104"
    # 服务器端口
    # port = 8085
    # 应用ID
    # app_id = "4719942393120423937"
    # 应用密钥
    # app_secret = "yiLxSA4P0C0HltAuQb9NjjYehWXYcgCm"

    # server_ip = "127.0.0.1"
    # app_id = "4719939614565990401"
    # app_secret = "Hew6bf18I7O71ihZ5CPMdCBgZzXuHRwt"

    # # app_id = None
    # app_secret = None

    # 邮箱注册，注册成功会发送邮件到您的邮箱，请查阅邮箱获得开通的应用信息 app_id app_secret
    result = dsxquant.dataser.reg(email="dangfm@qq.com")
    if result.success:
        print("register success")

    # 同步请求模式
    dd = dsxquant.dataser()
    if dd.connect():
        # 读取行业分类
        result = dd.get_hangye().series()
        print(result)
        # 读取概念
        result = dd.get_gainian().series()
        print(result)
        # 读取地域
        result = dd.get_diyu().series()
        print(result)
        # 读取某个市场的所有股票代码列表
        result = dd.get_stocks(dsxquant.market.SZ).series()
        print(result)
        # 读取某个行业的所有股票代码列表
        result = dd.get_stocks(hangye="交通运输").series()
        print(result)
        # 读取某个省份的所有股票代码列表
        result = dd.get_stocks(diyu="北京").series()
        print(result)
        # 读取某个上市日期以来的所有股票代码列表
        result = dd.get_stocks(listing_date="2021-01-01").series()
        print(result)
        # 读取实时行情并导出csv文件
        result = dd.get_quotes([("000002",dsxquant.MARKET.SZ),("600000",dsxquant.MARKET.SH)]).csv("quotes.csv")
        print(result)
        # 读取实时行情
        result = dd.get_quotes([("000002",dsxquant.MARKET.SZ),("600000",dsxquant.MARKET.SH)]).dataframe()
        print(result)
        # 读取实时行情，字符串
        result = dd.get_quotes("sh000001,sz000001,sh600000").datas()
        print(result.data)
        # 读取实时行情，字符串
        result = dd.get_quotes("sh000001").datas()
        if result.success:
            print(result.data)
        # 读取某个股票的财务信息，默认返回财务指标信息
        result = dd.get_finance("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 财务指标
        result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.DEFAULT).dataframe()
        print(result)
        # 资产负债表
        result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.BALANCESHEET).dataframe()
        print(result)
        # 现金流量表
        result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.CASHFLOW).dataframe()
        print(result)
        # 利润表
        result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.PROFIT).dataframe()
        print(result)
        # 读取单个股票的详情信息
        result = dd.get_stocks(dsxquant.MARKET.SH,"600000").dataframe()
        print(result)
        
        # 读取历史K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.DAY).dataframe()
        print(result)
        # 读取历史K线复权数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.DAY,fq=dsxquant.config.FQ.QFQ).dataframe()
        print(result)
        # 读取月K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.MONTH).dataframe()
        print(result)
        # 读取周K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.WEEK).dataframe()
        print(result)
        # 读取60分钟K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page_size=1000).dataframe()
        print(result)
        # 请求复权因子
        result = dd.get_factors("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求分红配股信息
        result = dd.get_sharebonus("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求逐笔交易
        result = dd.get_translist("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求分时图信息，默认是最新一个交易日的信息
        result = dd.get_timeshring("000001",dsxquant.MARKET.SZ).datas()
        if result.success:
            print(result.data)

        # time.sleep(10)
        dd.close()
    
    # with语法框架设计了自动连接，如果连接不成功会返回None，所以这里判断一下即可
    with dsxquant.dataser() as dd:
        # 连接成功可调用
        if dd:
            result = dd.get_quotes("sh000001").datas()
            print(result.data)

    # print("开启异步订阅模式")
    # 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
    dd_async = dsxquant.dataser.asyncconnect()
    if dd_async:
        # # 异步请求实时行情接口，服务器会主动推送实时行情
        def quotes_callback(response:dsxquant.parser):
            # print(response.get("msg"))
            result = response.dataframe()
            print(result)
            pass

        result = dd_async.sub_quotes("sh000001,sh600000,sz000001,bj430047,bj430090",quotes_callback)
        print(result)
        
        def quotes_all_callback(response:dsxquant.parser):
            dd = response.dataframe()
            names:list = list(dd.values[0])
            quote = dd.loc[1,:]
            code = quote[names.index("code")]
            t = quote[names.index("lasttime")]
            d = quote[names.index("lastdate")]
            t = datetime.datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S")
            s = datetime.datetime.now() - t
            print("%s 笔 %s 时间 %s 当前时间 %s 延时 %s s" % (dd.__len__(),code,t,datetime.datetime.now(),s.seconds))
        # 订阅全市场所有股票实时行情
        quote = dd_async.sub_all_quotes(quotes_all_callback)
        # time.sleep(10)

        # success = dd_async.cancel(quote)
        # if success!=None:
        #     print("cancel success:"+quote.api_name)
   
        # dd_async.close() 
        pass