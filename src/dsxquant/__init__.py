from dsxquant.config import config
# 默认服务器
config.DEFAULT_SERVER_IP = "129.211.209.104"
config.DEFAULT_PORT = 8085
from dsxquant.config.config import MARKET
from dsxquant.dataser.dsx_dataser import DsxDataser
from dsxquant.dataser.parser.base import BaseParser
# 市场编号
market = MARKET
# 数据采集器
dataser = DsxDataser
# 解析器
parser = BaseParser