
# 市场代码
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
# 头部长度
RSP_HEADER_LEN = 0x4
# 调试模式
DSXDEBUG = True

# 注册邮箱
email = "dangfm@qq.com"
# 服务器地址
server_ip = "127.0.0.1"
# 服务器端口
port = 8085
# 应用ID
app_id = "12345678"
# 应用密码
app_secret = "xxssxxddeedddd"
# 是否开启解压缩
enable_zip = False
