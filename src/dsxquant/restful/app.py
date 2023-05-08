# save this as app.py
from functools import wraps
import hashlib
from flask import Flask, abort,request
import dsxquant

app = Flask(__name__)
# MD5签名密钥
app_secret = 'your_app_secret'
# 是否开启签名验证
open_verify = False
# MD5签名验证
@app.before_request
def verify_request():
    if not open_verify or not app_secret:return
    args = request.args
    sign = args.get("sign")
    if not sign:
        abort(400, 'Missing sign')

    data = ''.join(sorted([k + str(args[k]) for k in args.keys() if k != 'sign']))
    expected_sign = hashlib.md5((data + app_secret).encode()).hexdigest()
    print(expected_sign)
    if expected_sign != sign:
        abort(401, 'Invalid sign')

# dsxquant 开关
def connclose(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        dsxquant.conn.connect()
        result = func(*args,**kwargs)
        dsxquant.close()
        return result
    return wrapper

@app.route("/price")
@app.route("/quotes")
@connclose
def get_quotes():
    args = request.args
    symbols = args.get("symbols")
    result = dsxquant.get_quotes(symbols).datas()
    result = result.__dict__
    return result

@app.route("/stocks")
@connclose
def get_stocks():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)
    hangye = args.get("hangye")
    gainian = args.get("gainian")
    diyu = args.get("diyu")
    listing_date = args.get("listing_date")
    category = args.get("category",0,type=int)
    result = dsxquant.get_stocks(market,symbol,hangye,gainian,diyu,listing_date,category).datas()
    result = result.__dict__
    return result

@app.route("/category")
@connclose
def get_category():
    args = request.args
    category_id = args.get("category_id")
    result = dsxquant.get_category(category_id).datas()
    result = result.__dict__
    return result

@app.route("/factors")
@connclose
def get_factors():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)
    result = dsxquant.get_factors(symbol,market).datas()
    result = result.__dict__
    return result

@app.route("/finance")
@connclose
def get_finance():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    report_type = args.get("report_type",dsxquant.report_type.DEFAULT)
    report_date = args.get("report_date")
    start = args.get("start")
    end = args.get("end")

    result = dsxquant.get_finance(symbol,market,report_type,report_date,start,end).datas()
    result = result.__dict__
    return result

@app.route("/klines")
@connclose
def get_klines():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    page = args.get("page",1,type=int)
    page_size = args.get("page_size",300,type=int)
    fq = args.get("fq",dsxquant.Fq.DEFAULT)
    cycle = args.get("fq",dsxquant.cycle.DAY)
    start = args.get("start")
    end = args.get("end")

    result = dsxquant.get_klines(symbol,market,page,page_size,fq,cycle,start,end).datas()
    result = result.__dict__
    return result

@app.route("/sharebonus")
@connclose
def get_sharebonus():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    start = args.get("start")
    end = args.get("end")

    result = dsxquant.get_sharebonus(symbol,market,start,end).datas()
    result = result.__dict__
    return result

@app.route("/structure")
@connclose
def get_structure():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    start = args.get("start")
    end = args.get("end")

    result = dsxquant.get_structure(symbol,market,start,end).datas()
    result = result.__dict__
    return result


@app.route("/timesharing")
@connclose
def get_timesharing():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    trade_date = args.get("trade_date")

    result = dsxquant.get_timeshring(symbol,market,trade_date).datas()
    result = result.__dict__
    return result

@app.route("/translist")
@connclose
def get_translist():
    args = request.args
    symbol = args.get("symbol",type=str)
    market = dsxquant.market.SZ
    if symbol and symbol.__len__()>2:
        two = symbol[:2]
        if two in dsxquant.MARKET_VAL:
            market = dsxquant.MARKET_VAL.index(two)
            symbol = symbol[2:]
    else:
        market = args.get("market",0,type=int)

    trade_date = args.get("trade_date")
    page = args.get("page",1,type=int)
    page_size = args.get("page_size",10,type=int)

    result = dsxquant.get_translist(symbol,market,trade_date,page,page_size).datas()
    result = result.__dict__
    return result

def run(host: str = None,
        port: int = None,
        debug: bool = None,
        load_dotenv: bool = True,
        verify:bool = False,
        secret:str = None,
        **options):
    
    global open_verify
    open_verify = verify
    global app_secret
    app_secret = secret
    app.run(host,port,debug,load_dotenv,**options)

if __name__ == '__main__':
    run(debug=True)