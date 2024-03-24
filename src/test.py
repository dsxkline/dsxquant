import datetime
import time
import dsxquant

if __name__=="__main__":
    # 开启debug
    # dsxquant.dataser.set_debug(True)
    # 注册邮箱
    # email = "dangfm@qq.com"
    # 服务器地址
    server_ip = "43.137.50.28"
    # 服务器端口
    port = 8085
    # 应用ID
    app_id = "4719942393120423937"
    # 应用密钥
    app_secret = "yiLxSA4P0C0HltAuQb9NjjYehWXYcgCm"

    # server_ip = dsxquant.config.DEFAULT_SERVER_IP
    # server_ip = "127.0.0.1"
    # port = 8085
    # app_id = 4719939614565990401"
    # app_secret = "Hew6bf18I7O71ihZ5CPMdCBgZzXuHRwt"

    # # app_id = None
    # app_secret = None

    result = dsxquant.get_quotes("sh000001").dataframe()
    print(result)
    # dsxquant.close()
    # 邮箱注册，注册成功会发送邮件到您的邮箱，请查阅邮箱获得开通的应用信息 app_id app_secret
    result = dsxquant.dataser.reg(email="dangfm@qq.com")
    if result.success:
        print("register success")

    # 同步请求模式
    dd = dsxquant.dataser(server_ip,port,app_id,app_secret)
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
        result = dd.get_price("sh000001").datas()
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
        result = dd.get_klines("000031",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.DAY,start="20220101",end="20230501",fq=dsxquant.config.FQ.QFQ).dataframe()
        print(result)
        # 读取历史K线复权数据
        result = dd.get_klines("000031",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.DAY,fq=dsxquant.config.FQ.QFQ).dataframe()
        print(result)
        # 读取月K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.MONTH).dataframe()
        print(result)
        # 读取周K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.WEEK).dataframe()
        print(result)
        # 读取60分钟K线数据
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=1,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=2,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=3,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=4,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=5,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=6,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page=7,page_size=300,enable_cache=False).dataframe()
        print(result)
        result = dd.get_minklines("600000",dsxquant.MARKET.SH,cycle=dsxquant.config.CYCLE.M1,page=1,page_size=30).dataframe()
        print(result)
        result = dd.get_minklines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,fq=dsxquant.config.FQ.QFQ,page=1,page_size=300).dataframe()
        print(result)
        result = dd.get_minklines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,fq=dsxquant.config.FQ.HFQ,page=1,page_size=300).dataframe()
        print(result)
        # 请求复权因子
        result = dd.get_factors("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求分红配股信息
        result = dd.get_sharebonus("000001",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求股本结构信息
        result = dd.get_structure("000007",dsxquant.MARKET.SZ).dataframe()
        print(result)
        # 请求逐笔交易
        result = dd.get_translist("000001",dsxquant.MARKET.SZ,page=2).dataframe()
        print(result)
        # 请求分时图信息，默认是最新一个交易日的信息
        result = dd.get_timesharing("000001",dsxquant.MARKET).datas()
        if result.success:
            print(result.data) 
        result = dd.get_timesharing("000001",dsxquant.MARKET.SZ,day=2).datas()
        if result.success:
            print(result.data)

        # time.sleep(10)
        dd.close()
    
    # with语法框架设计了自动连接，如果连接不成功会返回None，所以这里判断一下即可
    with dsxquant.dataser(server_ip,port,app_id,app_secret) as dd:
        # 连接成功可调用
        if dd:
            result = dd.get_quotes("sh000001").datas()
            print(result.data)

    # print("开启异步订阅模式")
    # 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
    def closecallback(need_connect):
        print("是否需要重连 %s" % need_connect)
        # 断线后重新连接
        asyncdemo()
        
    def asyncdemo():
        # 异步订阅模式
        dd_async = dsxquant.dataser.asyncconnect(server_ip,port,app_id,app_secret)
        if dd_async:
            # 实现断线重连
            dd_async.close_callback(closecallback)
            # # 异步请求实时行情接口，服务器会主动推送实时行情
            def quotes_callback(response:dsxquant.parser):
                # print(response.get("msg"))
                result = response.dataframe()
                print(result)
                pass
            # 订阅多个股票实时行情
            result = dd_async.sub_quotes("sh000001,sh600000,sz000001,bj430047,bj430090",quotes_callback)
            # print(result)
            
            # 全量推送回调
            def quotes_all_callback(response:dsxquant.parser):
                dd = response.dataframe()
                names:list = list(dd.values[0])
                quote = dd.loc[1]
                code = quote[names.index("code")]
                t = quote[names.index("lasttime")]
                d = quote[names.index("lastdate")]
                t = datetime.datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S")
                s = datetime.datetime.now() - t
                print("%s 笔 %s 时间 %s 当前时间 %s 延时 %s s" % (dd.__len__(),code,t,datetime.datetime.now(),s.seconds))
            # 订阅全市场所有股票实时行情
            quote = dd_async.sub_all_price(quotes_all_callback)
            # time.sleep(10)

            # success = dd_async.cancel(quote)
            # if success!=None:
            #     print("cancel success:"+quote.api_name)
    
            # dd_async.close() 
            pass
    asyncdemo()