
# 市场代码
import struct


class MARKET:
    SH=0                            # 上交所
    SZ=1                            # 深交所
    BJ=2                            # 北交所
    HK=3                            # 港交所
    US=4                            # 美国

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

# 注册邮箱
email = "dangfm@qq.com"
# 服务器地址
server_ip = "127.0.0.1" #"171.38.105.119"
# 服务器端口
port = 8085
# 应用ID
app_id = "4718473628448980993"
# 应用密码
app_secret = "bta8BrexS2IEcPBtMv6Pdn5Xp7GIFXPh"
# 是否开启解压缩
enable_zip = False
