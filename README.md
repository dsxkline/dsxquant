# Dsxquant 开源量化工具箱

Dsxquant 是一个基于python语言开发的的量化工具箱，主要特征是其工具属性，专为上层策略应用提供服务。

<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/dsxquant"> <img alt="PyPI" src="https://img.shields.io/pypi/v/dsxquant?label=dsxquant"> <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/dsxkline/dsxquant"> <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/dsxquant"> <img alt="Libraries.io dependency status for GitHub repo" src="https://img.shields.io/librariesio/github/dsxkline/dsxquant"> <img alt="GitHub" src="https://img.shields.io/github/license/dsxkline/dsxquant"> <img alt="GitHub search hit counter" src="https://img.shields.io/github/search/dsxkline/dsxquant/dsxquant"> <img alt="Website" src="https://img.shields.io/website?label=dsxquant%20website&up_message=online&url=https%3A%2F%2Fwww.dsxquant.com"> <img alt="Lines of code" src="https://img.shields.io/tokei/lines/github/dsxkline/dsxquant">

## 一、简介
Dsxquant 采用模块化设计思想，框架集成了数据、回测、策略、因子、仿真、资管、交易等模块。

技术架构

<img src="https://www.dsxquant.com/wp-content/uploads/2023/03/Dsxquant-Main-Engine-2-1024x985.png" width="300" />

## 二、数据结构

文档数据结构描述主要基于Pandas的 Series 和DataFrame，框架接口都支持返回Json数据，Series、DataFrame，支持 csv 文件转换等。

## 三、安装
Dsxquant 托管在 Github,Gitee,PyPi，默认采用PyPi包安装方式

### 1、PyPi 安装

```
pip install dsxquant
```

### 2、Git 源码安装导入

```
git clone https://github.com/dsxkline/dsxquant.git
```

### 3、安装依赖
直接通过依赖文件安装即可，也可以手动一个一个安装

```
pip install -r requirements.txt

Deprecated==1.2.13
dsxindexer==1.0.0
Flask==2.3.2
numpy==1.23.4
pandas==1.5.1
prettytable==3.7.0
progressbar33==2.4

```

## 四、快速上手

安装后直接导入包即可使用

``` python
import dsxquant
# dsxquant 默认维护了一个连接
# 可直接读取实时行情
# result = dsxquant.get_quotes("sh000001,sh600000").series()
result = dsxquant.get_price("sh000001,sh600000").series()
print(result)
```

## 五、连接

连接方式：
同步连接 （默认）connect()
异步连接 syncconnect()
### 示例：

``` python
# 默认采用同步连接
dd = dsxquant.dataser()
if dd.connect():
   # 读取行业分类
   result = dd.get_hangye().series()
   print(result)
```

### 框架支持with语法

```python
# with语法框架设计了自动连接，如果连接不成功会返回None，所以这里判断一下即可
with dsxquant.dataser() as dd:
    # 连接成功可调用
    if dd:
       result = dd.get_quotes("sh000001").datas()
       print(result.data)
```

### 异步订阅模式

```python
# 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
dd_async = dsxquant.dataser.asyncconnect()
if dd_async:
    # 异步请求实时行情接口，服务器会主动推送实时行情
    def quotes_callback(response:dsxquant.parser):
        # logger.debug(response.get("msg"))
        result = response.dataframe()
        logger.debug(result)
        pass
    
    result = dd_async.sub_quotes("sh000001,sh600000,sz000001,bj430047,bj430090",quotes_callback)
    logger.debug(result)
```

## 六、订阅

Dsxquant 提供实时行情订阅功能，可批量订阅，也可以全量订阅。订阅功能需要启用异步连接 asyncconnect()，批量订阅最多支持50个股票代码，全量订阅默认全市场变动数据推送。

```python
# 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
dd_async = dsxquant.dataser.asyncconnect()
if dd_async:
    # 异步请求实时行情接口，服务器会主动推送实时行情
    def quotes_callback(response:dsxquant.parser):
        # print(response.get("msg"))
        result = response.dataframe()
        print(result)
    # 批量订阅股票代码,批量订阅最多支持50个股票代码
    result = dd_async.sub_quotes("sh000001,sh600000,sz000001,bj430047,bj430090",quotes_callback)
    print(result)
        
    def quotes_all_callback(response:dsxquant.parser):
        dd = response.dataframe()
        # 第一行默认是字段名称数组 ["amount","close",.....]
        names:list = list(dd.values[0])
        # 第二行开始是数据
        quote = dd.loc[1,:]
        code = quote[names.index("code")]
        t = quote[names.index("lasttime")]
        d = quote[names.index("lastdate")]
        t = datetime.datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S")
        s = datetime.datetime.now() - t
        print("%s 笔 %s 时间 %s 当前时间 %s 延时 %s s" % (dd.__len__(),code,t,datetime.datetime.now(),s.seconds))
    # 全量订阅全市场所有股票实时行情
    dd_async.sub_all_quotes(quotes_all_callback)
```

### 取消订阅

```python
success = dd_async.cancel(quote)
if success!=None:
    print("cancel success:"+quote.api_name)
```

## 七、读取市场股票

目前市场仅支持上交所、深交所、北交所。

### 市场枚举值：

```python
# 市场代码
class MARKET:
    SH=0                            # 上交所
    SZ=1                            # 深交所
    BJ=2                            # 北交所
    HK=3                            # 港交所
    US=4                            # 美国
```

### 读取某个市场的所有股票列表

```python
# 读取某个市场的所有股票代码列表
result = dd.get_stocks(dsxquant.market.SZ).series()
print(result)
```

## 八、读取分类列表

主要是读取行业、概念、地域分类的股票代码

### 读取行业分类
```python
# 读取行业分类
result = dd.get_hangye().series()
print(result)
```

输出格式

```

       0
0     煤炭
1   石油石化
2   美容护理
3     环保
4   电力设备
...
25    汽车
26    电子
27  有色金属
28    钢铁
29  农林牧渔
30    综合
```

### 读取概念分类
```python
# 读取概念分类
result = dd.get_gainian().series()
print(result)
```

输出格式

```
         0
0      血氧仪
1    毫米波雷达
2     eSIM
3     AI训练
4     数字哨兵
..     ...
619     举牌
620   军民融合
621    京津冀
622   抗癌药物
623   昨日涨停
```

### 读取地域分类

```python
# 读取地域分类
result = dd.get_diyu().series()
print(result)
```

输出格式

```
           0
0   新疆维吾尔自治区
1    宁夏回族自治区
2        青海省
3        甘肃省
25       辽宁省
...
29       天津市
30       北京市
```

## 九、读取实时行情

目前仅支持A股实时行情，行情来自于网络公开数据，延时10秒以上，供个人量化开发者测试所用，请勿用于商业用途。

```python
 # 读取实时行情并导出csv文件
result = dd.get_quotes([("000002",dsxquant.MARKET.SZ),("600000",dsxquant.MARKET.SH)]).csv("quotes.csv")
print(result)

# 读取实时行情
result = dd.get_quotes([("000002",dsxquant.MARKET.SZ),("600000",dsxquant.MARKET.SH)]).dataframe()
print(result)

# 读取实时行情，批量字符串
result = dd.get_quotes("sh000001,sz000001,sh600000").datas()
print(result.data)

# 读取实时行情，字符串
result = dd.get_quotes("sh000001").datas()
if result.success:
    print(result.data)
```

## 十、读取历史K线

读取上市以来所有的历史K线数据，前后复权数据等。支持读取日K、周K、月K、年K等数据

### 读取日K历史数据

```python
# 读取历史K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.DAY).dataframe()
print(result)
```

输出格式 [日期,开,高,低,收,成交量,成交额]

```
                                                     0
0    20230227,621462.0,13.88,13.68,13.86,621462.0,8...
1    20230224,14.02,14.03,13.80,13.86,729989,101265...
2    20230223,14.00,14.32,13.98,14.05,824491,116553...
3    20230222,14.00,14.12,13.94,14.02,638922,895742...
4    20230221,14.06,14.20,13.92,14.10,990495,139315...
..                                                 ...
315  20211109,17.48,17.65,17.26,17.53,1240573,21631...
316  20211108,17.62,17.81,17.36,17.42,1376815,24064...
317  20211105,17.85,18.00,17.57,17.64,1096040,19424...
318  20211104,18.08,18.10,17.80,17.87,983411,176067...
319  20211103,18.10,18.24,17.85,18.03,1114972,20093...
```

### 读取周K历史数据

```python
# 读取周K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.WEEK).dataframe()
print(result)
```

### 读取月K历史数据

```python
# 读取月K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.MONTH).dataframe()
print(result)
```

### 读取年K历史数据

```python
# 读取年K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.YEAR).dataframe()
print(result)
```

## 十一、读取分钟K线

支持读取30天内的历史分钟K线数据，1分钟、5分钟、15分钟、30分钟、60分钟等。

### 读取1分钟历史数据

```python
# 读取1分钟K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M1,page_size=1000).dataframe()
print(result)
```

返回数据格式
```
                                                     0
0    202302240931,14.02,14.03,13.94,13.96,26062,364...
1    202302240932,13.96,13.96,13.92,13.96,10384,144...
2    202302240933,13.96,13.96,13.93,13.94,6386,8908...
3    202302240934,13.93,13.94,13.92,13.93,10046,139...
4    202302240935,13.93,13.93,13.92,13.93,4432,6172...
..                                                 ...
475  202302031456,14.35,14.36,14.34,14.35,3920,5624...
476  202302031457,14.36,14.36,14.34,14.34,5109,7332...
477  202302031458,14.35,14.35,14.35,14.35,585,84005...
478        202302031459,14.35,14.35,14.35,14.35,0,0.00
479  202302031500,14.32,14.32,14.32,14.32,21701,310...
```

### 读取5分钟历史数据

```python
# 读取5分钟K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M5,page_size=1000).dataframe()
print(result)
```

### 读取15分钟历史数据

```python
# 读取15分钟K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M15,page_size=1000).dataframe()
print(result)
```

### 读取30分钟历史数据
```python
# 读取30分钟K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M30,page_size=1000).dataframe()
print(result)
```

### 读取60分钟历史数据

```python
# 读取60分钟K线数据
result = dd.get_klines("000001",dsxquant.MARKET.SZ,cycle=dsxquant.config.CYCLE.M60,page_size=1000).dataframe()
print(result)
```

## 十二、复权因子

框架复权因子采用的是涨跌幅复权算法，算法已开源，主要采用分红配股和股改数据进行计算，详细算法介绍可参考文章《量化基础算法:K线涨跌幅复权算法揭秘和实现》

### 获取复权因子

```python
# 请求复权因子
result = dd.get_factors("000001",dsxquant.MARKET.SZ).dataframe()
print(result)
```

输出格式，除权日的复权因子列表 {日期:[前复权因子,后复权因子]}
```

20220722    0.982475,60.840279
20210514    0.974809,59.774055
20200528    0.958463,59.307677
20190626    0.948114,58.313133
20180712    0.933428,57.683542
20170721    0.919984,56.790039
20160616    0.755418,55.972096
20150413    0.623983,45.959846
20140612    0.512923,37.963297
20130620    0.317744,31.206389
20121019    0.315393,19.331661
20081031    0.241891,19.188569
20070618    0.219832,14.716718
20030929    0.216301,13.374637
20020723    0.214064,13.159841
20001106    0.186992,13.023705
19991018    0.182043,11.376639
19970825    0.120593,11.075537
19960527     0.060297,7.336915
19950925      0.04872,3.668457
19940711     0.031303,2.964128
19930524     0.016436,1.904488
```

得到复权因子后，根据对应的日期即可计算出前后复权数据,计算方法参考 《量化基础算法:K线涨跌幅复权算法揭秘和实现》

## 十三、分红配股

获取上市以来所有的分红配股信息，此信息来源于网络公开数据，由Dsxquant整理清洗。

### 获取分红配股

```python
# 请求分红配股信息
result = dd.get_sharebonus("000001",dsxquant.MARKET.SZ).dataframe()
print(result)
```

返回数据格式，参数名称可参考 接口文档

```
code              sz000001
per_ten_allo              
allo_price                
anno_day        2022-07-15
per_ten_send             0
per_ten_incr             0
per_cash_div          2.28
share_day       2022-07-22
reg_day         2022-07-21
list_day              
```

## 十四、财务报表

财务报表数据来源于网络公开数据，由Dsxquant收集整理，提供财务指标、资产负债表、利润表、现金流量表等报表查询。

### 获取财务指标

```python
# 财务指标
result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.DEFAULT).dataframe()
print(result)
```

返回数据格式

```
CODE                 sz000002
DATE               2022-09-30
ZZC      1832624105913.530029
LDZC     1482234397741.830078
GDZC       14951487488.129999
ZFZ      1426655627128.919922
LDFZ     1168326002698.350098
JZC       405968478784.610107
MGJZC                19.73719
YYSR      337673241644.890015
YYLR       37447020773.470001
LRZE       37731123134.410004
JLR            27244596166.41
MGSY                   1.4697
```

### 获取资产负债表

```python
# 资产负债表
result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.BALANCESHEET).dataframe()
print(result)
```
返回数据格式
```
report_date               2022-09-30
zc_1                                
zc_2                                
zc_3                                
zc_20                               
                        ...         
fzgdqy_2                        None
fzgdqy_total    1832624105913.530029
op_1                            None
op_2                            None
code                        sz000002
```

### 获取现金流量表

```python
# 现金流量表
result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.CASHFLOW).dataframe()
print(result)
```

返回数据格式

```
report_date    2022-09-30
jy_in_1                  
jy_in_2                  
jy_in_3                  
jy_in_4              None
                  ...    
je_11                    
fbcce_add                
op_1                 None
op_2                 None
code             sz000002
```

### 获取利润表

```python
# 利润表
result = dd.get_finance("000002",dsxquant.MARKET.SZ,report_type=dsxquant.config.REPORT_TYPE.PROFIT).dataframe()
print(result)
```

返回数据格式

```
report_date             2022-09-30
yyzsr          337673241644.890015
sr_1           337673241644.890015
sr_2                          None
sr_3                          None
                      ...         
zhsy_3          26123838848.540001
zhsy_4          15412047995.690001
zhsy_5              10711790852.85
zhsy_6                        None
code                      sz000002
```

## 十五、分时线
仅支持查询30天内分时线历史数据

```python
# 请求分时图信息，默认是最新一个交易日的信息
result = dd.get_timeshring("000001",dsxquant.MARKET.SZ).datas()
if result.success:
    print(result.data)
```

返回数据格式

```
[
['0925', 13.85, 659700.0, 9136845.0, 13.85], 
['0930', 13.85, 3384822.0, 46903478.453999996, 13.857], 
['0931', 13.82, 1444600.0, 20009154.6, 13.851], 
['0932', 13.85, 1255300.0, 17382139.099999998, 13.847], 
['0933', 13.88, 2193900.0, 30396484.5, 13.855], 
['0934', 13.86, 913600.0, 12658841.6, 13.856], 
...
['1454', 13.95, 404100.0, 5612949.0, 13.89], 
['1455', 13.95, 670000.0, 9306970.0, 13.891], 
['1456', 13.95, 300500.0, 4174245.5, 13.891], 
['1500', 13.96, 993594.0, 13803007.848, 13.892]
]
```

## 十六、逐笔交易

只支持查询30天内的历史逐笔交易信息

### 获取逐笔交易信息

```python
# 请求逐笔交易
result = dd.get_translist("000001",dsxquant.MARKET.SZ).dataframe()
print(result)
```

返回数据格式

```
      0      1         2             3       4
0  1500  13.96  993594.0  1.380301e+07  13.892
1  1456  13.95  300500.0  4.174246e+06  13.891
2  1455  13.95  670000.0  9.306970e+06  13.891
3  1454  13.95  404100.0  5.612949e+06  13.890
4  1453  13.94  537500.0  7.465875e+06  13.890
5  1452  13.96  356300.0  4.949007e+06  13.890
6  1451  13.96  246100.0  3.418083e+06  13.889
7  1450  13.95  671800.0  9.330630e+06  13.889
8  1449  13.96  253800.0  3.525028e+06  13.889
9  1448  13.96  423200.0  5.877402e+06  13.888
```

## 十七、回测

目前支持简单回测功能，支持日线和分钟线级别的历史数据回测


```python
from dsxquant.engins.engin import Engin
from dsxquant.backtest.back_test import BackTest
from dsxquant import StrategyEngin,EmulationEngin,DataFeed,EventType
from dsxquant.strategy.common.macross_strategy import MACrossStrategy
import dsxquant
# 先启动系统引擎
engin = Engin().start()
# 安装模块
engin.install(StrategyEngin,EmulationEngin,DataFeed)
# 调用回测,这个例子是日线回测
backtest = BackTest(MACrossStrategy,"sz000001",start="20200412",end="20230427",data=EventType.DAYLINE)
engin.install(backtest)
# 等待回测完成并显示回测结果  
backtest.show()
engin.shutdown()

```

## 十八、RESTful Api 接口
采用Flask框架设计了一套RESTful API，支持一键启动，支持Nginx部署等

```python
import dsxquant
# 这里用于本地测试，生产部署请用Nginx等服务
dsxquant.restfulapi.run()

```
启动后通过浏览器进行访问 http://127.0.0.1:5000/price?symbols=sh000001,sz000001

### Nginx 配置
Nginx 只需要做反向代理配置即可
```
server {
    listen 80;
    server_name example.com;

    location / {
        uwsgi_pass 127.0.0.1:5001;
        include uwsgi_params;
    }
}
```

### uwsgi 配置ini文件即可

这里的端口号要跟Nginx反向代理配置的端口一致，其中 module 为执行的python文件，dsxquant.restful.app, callable为Flask项目的app对象，其他参数可以参考Flask文档

```
[uwsgi]
socket = 127.0.0.1:5001
module = dsxquant.restful.app
callable = app
processes = 4
threads = 2
stats = 127.0.0.1:5000

```

### 启动uwsgi服务

配置好Nginx和uwsgi配置文件后，需要启动uwsgi服务，只需运行如下uwsgi命令即可，安装uwsgi可参考uwsgi官网


```
uwsgi app.ini

```
启动后即可在浏览器访问API接口

