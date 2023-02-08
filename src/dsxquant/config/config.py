
# 市场代码
import struct

# 周期
class CYCLE:
    T='t'                           # 分时线
    T5='t5'                         # 五日分时线
    DAY="day"                       # 日K
    WEEK="week"                     # 周K
    MONTH="month"                   # 月K
    YEAR="year"                     # 年K
    M1="m1"                         # 1分钟K
    M15="m15"                        # 15分钟K
    M30="m30"                       # 30分钟K
    M60="m60"                       # 60分钟K
# 市场代码
class MARKET:
    SH=0                            # 上交所
    SZ=1                            # 深交所
    BJ=2                            # 北交所
    HK=3                            # 港交所
    US=4                            # 美国
# 复权类型
class FQ:
    DEFAULT=''                      # 默认不复权
    QFQ="qfq"                       # 前复权
    HFQ="hfq"                       # 后复权
# 财务报表类型
class REPORT_TYPE:
    DEFAULT='index'                 # 财务指标
    PROFIT="profit"                 # 利润表
    CASHFLOW="cashflow"             # 现金流量表
    BALANCESHEET="balancesheet"     # 资产负债表

# socket 链接超时
CONNECT_TIMEOUT = 30
# 打包格式符
PACK_TYPE = 'i'
# 消息协议头部长度
HEADER_LEN = struct.calcsize(PACK_TYPE)
# 调试模式
DSXDEBUG = True
