
import os
import struct
# 调试模式
DSXDEBUG = True
# 默认服务器地址
DEFAULT_SERVER_IP = None
# 默认服务器端口号
DEFAULT_PORT = None
# 周期
class CYCLE:
    T='t'                           # 分时线
    T5='t5'                         # 五日分时线
    DAY="day"                       # 日K
    WEEK="week"                     # 周K
    MONTH="month"                   # 月K
    YEAR="year"                     # 年K
    M1="m1"                         # 1分钟K
    M5="m5"                         # 5分钟K
    M15="m15"                       # 15分钟K
    M30="m30"                       # 30分钟K
    M60="m60"                       # 60分钟K
# 市场代码
class MARKET:
    SH=0                            # 上交所
    SZ=1                            # 深交所
    BJ=2                            # 北交所
    HK=3                            # 港交所
    US=4                            # 美国
MARKET_VAL:list=["sh","sz","bj","hk","us"]
# 复权类型
class FQ:
    DEFAULT=''                      # 默认不复权
    QFQ="qfq"                       # 前复权
    HFQ="hfq"                       # 后复权
# 财务报表类型
class REPORT_TYPE:
    DEFAULT=''                      # 财务简报
    INDEX='index'                   # 财务指标
    PROFIT="profit"                 # 利润表
    CASHFLOW="cashflow"             # 现金流量表
    BALANCESHEET="balancesheet"     # 资产负债表

# 交易类型
class TRADE_TYPE:
    BUY="buy"
    SELL="sell"
    CANCEL="cancel"
    QUICKBUY="quickbuy"
    QUICKSELL="quicksell"
    CANCELALL="cancelall"

# 事件类型
class EventType:
    # 默认类型None
    NONE="None"
    # 结束
    THEEND = "theend"
    # 数据集
    DAYLINE="dayline"
    WEEKLINE="weekline"
    MONTHLINE="monthline"
    YEARLINE="yearline"
    MIN1LINE="min1line"
    MIN5LINE="min5line"
    MIN15LINE="min15line"
    MIN30LINE="min30line"
    MIN60LINE="min60line"

    FINANCE="finance"
    STRUCTURE="structure"
    # 帧数据
    DAYBAR="daybar"
    WEEKBAR="weekbar"
    MONTHBAR="monthbar"
    YEARBAR="yearbar"
    MINBAR="minbar"
    TICK="tick"
    # 交易信号
    BUY="buy"
    SELL="sell"
    CANCEL="cancel"

class PositionStatus:
    DEFAULT = "开仓"
    HOLDING = "持仓中"
    CLOSED = "已平仓"

class BaseSymbol:
    # 沪深300
    HS300="sz399300"
    # 恒生指数
    HK80M="hk800000"
    # 标普500
    USSPX="usspx"

# socket 连接超时
CONNECT_TIMEOUT = 30
# 打包格式符 b 0=不压缩 1=压缩 i 为包大小
PACK_TYPE = 'bi'
# 消息协议头部长度，根据打包格式符自动计算
HEADER_LEN = struct.calcsize(PACK_TYPE)
# 是压缩传输数据
ENABLE_GZIP = True
# 缓存地址
CACHE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/caches"
# 回测数据导出目录
EXPORT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/export"

