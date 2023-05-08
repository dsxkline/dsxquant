from typing import Union
from deprecated import deprecated
from dsxquant.config import config
# 默认服务器
config.DEFAULT_SERVER_IP = "129.211.209.104"
config.DEFAULT_PORT = 8085
from dsxquant.config.config import MARKET,EventType,PositionStatus,BaseSymbol,FQ,MARKET_VAL
from dsxquant.dataser.dsx_dataser import DsxDataser
from dsxquant.dataser.parser.base import BaseParser
from dsxquant.config.logconfig import logger
from dsxquant.engins.engin import Engin
from dsxquant.engins.event_bus import EventBus
from dsxquant.engins.event_model import EventModel
from dsxquant.engins.engin import Engin
from dsxquant.engins.emultion_engin import EmulationEngin
from dsxquant.engins.trade_engin import TradeEngin
from dsxquant.engins.strategy_engin import StrategyEngin
from dsxquant.backtest.back_test import BackTest
from dsxquant.engins.data_feed import DataFeed
from dsxquant.orders.orders import Orders
from dsxindexer.processors.sindexer_processor import SindexerProcessor as sindexer
from dsxindexer.sindexer.models.kline_model import KlineModel
from dsxquant.strategy.base import BaseStrategy
from dsxquant.restful import app as restfulapi
# 市场编号
market = MARKET
# 周期
cycle = config.CYCLE
# 复权
Fq = config.FQ
# 报表类型
report_type = config.REPORT_TYPE
# 数据采集器
dataser = DsxDataser
# 解析器
parser = BaseParser
# 默认维护一个连接
conn:DsxDataser = DsxDataser()
def close():
    conn.close()
def connect():
    if not conn.connected:conn.connect()
    return True
# 下面重新封装一下
def get_category(category_id:int=0) -> Union[BaseParser,None]:
    if connect():  return conn.get_category(category_id)

def get_hangye() -> Union[BaseParser,None]:
    if connect():  return conn.get_hangye()

def get_gainian() -> Union[BaseParser,None]:
    if connect():  return conn.get_gainian()

def get_diyu() -> Union[BaseParser,None]:
    if connect():  return conn.get_diyu()

def get_stocks(market:int=None,symbol:str=None,hangye:str=None,gainian:str=None,diyu:str=None,listing_date:str=None,category:int=0) -> Union[BaseParser,None]:
    if connect():  return conn.get_stocks(market,symbol,hangye,gainian,diyu,listing_date,category)

def get_quotes(symbols:Union[list,str,tuple]) -> Union[BaseParser,None]:
    if connect():  return conn.get_quotes(symbols)

def get_price(symbols:Union[list,str,tuple]) -> Union[BaseParser,None]:
    if connect():  return conn.get_quotes(symbols)

def get_klines(symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,start:str=None,end:str=None,enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_klines(symbol,market,page,page_size,fq,cycle,start,end,enable_cache)

def get_finance(symbol,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date="",start:str=None,end:str=None,enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_finance(symbol,market,report_type,report_date,start,end,enable_cache)

def get_sharebonus(symbol:str,market:int,start:str=None,end:str=None,enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_sharebonus(symbol,market,start,end,enable_cache)

def get_structure(symbol:str,market:int,start:str=None,end:str=None,enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_structure(symbol,market,start,end,enable_cache)

def get_factors(symbol:str,market:int) -> Union[BaseParser,None]:
    if connect():  return conn.get_factors(symbol,market)
@deprecated
def get_timeshring(symbol:str,market:int,trade_date:str="",enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_timeshring(symbol,market,trade_date,enable_cache)

def get_timesharing(symbol:str,market:int,trade_date:str="",enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_timesharing(symbol,market,trade_date,enable_cache)

def get_translist(symbol:str,market:int,trade_date:str="",page:int=1,page_size:int=10,enable_cache:bool=True) -> Union[BaseParser,None]:
    if connect():  return conn.get_translist(symbol,market,trade_date,page,page_size,enable_cache)