import datetime
import json
import os
from dsxquant import MARKET,MARKET_VAL,config
import dsxquant
class CacheHelper:

    encoding = "utf-8"

    @staticmethod
    def clear():
        try:
            path = config.CACHE_PATH
            os.rmdir(path)
        except Exception as e:
            dsxquant.logger.error(e)

    @staticmethod
    def get_db_path(dir1,dir2,db):
        path = config.CACHE_PATH+"/"+db+"/"
        if dir1: path += dir1+"/"
        if dir2: path += dir2+"/"
            
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    @staticmethod
    def today_is_cache_date(path,update=False):
        filename = path+"/last_date.txt"
        if os.path.exists(filename):
            with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                content = f.read()
                if content==datetime.datetime.now().strftime("%Y%m%d"):return True
    @staticmethod
    def save_cache_date(path):
        filename = path+"/last_date.txt"
        with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(datetime.datetime.now().strftime("%Y%m%d"))
    
    @staticmethod
    def get_db_filename(symbol:str,market:MARKET,dir1,dir2,db):
        code = symbol
        if symbol[:2] not in MARKET_VAL:
            code = MARKET_VAL[market]+symbol
        path = CacheHelper.get_db_path(dir1,dir2,db)
        filename = path+code+".txt"
        # with open(filename,mode="a",encoding=CacheHelper.encoding) as f:
        #     pass
        return filename
        
    @staticmethod
    def save_klines(symbol:str,market:MARKET,cycle,fq,datas:list):
        db = "klines"
        if not fq: fq = "data"
        code = symbol
        if symbol[:2] not in MARKET_VAL:
            code = MARKET_VAL[market]+symbol
        fq = fq+"/"+code
        filename = CacheHelper.get_db_filename(symbol,market,cycle,fq,db)
        content = ""
        if os.path.exists(filename):
            with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                content = f.read()

        with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
            if content:
                content = json.loads(content)
                if isinstance(content,dict):
                    dates = content.keys()
                    for item in datas:
                        obj = item.split(",")
                        date = obj[0]
                        if date not in dates:
                            content[date] = item
                f.write(json.dumps(content))
            else:
                content = {}
                for item in datas:
                    obj = item.split(",")
                    date = obj[0]
                    content[date] = item
                f.write(json.dumps(content))
        CacheHelper.save_cache_date(CacheHelper.get_db_path(cycle,fq,db))
        
                    
    @staticmethod
    def get_klines(symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,start:str=None,end:str=None):
        db = "klines"
        if not fq: fq = "data"
        code = symbol
        if symbol[:2] not in MARKET_VAL:
            code = MARKET_VAL[market]+symbol
        fq = fq+"/"+code
        filename = CacheHelper.get_db_filename(symbol,market,cycle,fq,db)
        if not os.path.exists(filename): return
        # 如果今天没有缓存过，就不使用缓存
        if not end and not CacheHelper.today_is_cache_date(CacheHelper.get_db_path(cycle,fq,db)):return
        
        with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
            content = f.read()
            if content:
                content = json.loads(content)
                if isinstance(content,dict):
                    content = dict(sorted(content.items(), key=lambda x: x[0]))
                    datas = list(content.values())
                    # 分页
                    s = (page-1)*page_size
                    e = page * page_size
                    # 时间倒序
                    datas.reverse()
                    if e >=datas.__len__(): e = datas.__len__()
                    
                    if start and not end:
                        end = datetime.datetime.strftime("%Y%m%d")
                    
                    if start and end:
                        s = -1
                        e = -1
                        for i in range(len(datas)):
                            item = datas[i]
                            if isinstance(item,list):
                                d = item[0][:8]
                            else:
                                d = item.split(",")[0][:8]
                            if int(d)==int(end):
                                s = i
                                break
                            if int(d)<int(end):
                                break 

                        for i in range(len(datas)-1,0,-1):
                            item = datas[i]
                            if isinstance(item,list):
                                d = item[0][:8]
                            else:
                                d = item.split(",")[0][:8]
                            if int(d)>=int(start):
                                e = i
                                break
                        if s>=0 and e>=0:
                            datas = datas[s:e]
                        else:
                            datas = []
                    else:
                        datas = datas[s:e]
                    return datas
                
    @staticmethod
    def save_finance(symbol:str,market:MARKET,report_type:str,date:str,datas:any):
        if datas:
            db = "finance"
            if not date:
                print(date)
                pass
            dir2 = date.replace("-","")
            if report_type:
                dir2 = report_type+"/"+date.replace("-","")
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(json.dumps(datas))
            CacheHelper.save_cache_date(CacheHelper.get_db_path(symbol,report_type,db))
    
    @staticmethod
    def get_finance(symbol:str,market:int,report_type:config.REPORT_TYPE=config.REPORT_TYPE.DEFAULT,report_date="",start:str=None,end:str=None):
        db = "finance"
        path = CacheHelper.get_db_path(symbol,report_type,db)
        # 如果今天没有缓存过，就不使用缓存
        if not report_date and not CacheHelper.today_is_cache_date(path):return
        dir_list:list = os.listdir(path)
        if not dir_list: return []
        if "last_date.txt" in dir_list: dir_list.remove("last_date.txt")
        dir_list.sort()
        if report_date=="":report_date = dir_list[-1]
        if not report_date : return []
        report_date = report_date.replace("-","")
        dir2 = report_date
        if report_type:
            dir2 = report_type+"/"+report_date
        if not start and not end:
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            if not os.path.exists(filename): return
            with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                content = f.read()
                if content:
                    content = json.loads(content)
                    return content
        else:
            result = []
            if start==None: return result
            if end==None:end = datetime.datetime.strftime("%Y%m%d")
            start = start.replace("-","")
            end = end.replace("-","")
            for date in dir_list:
                if int(date)>=int(start) and int(date)<=int(end):
                    filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
                    if not os.path.exists(filename): return
                    with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                        content = f.read()
                        if content:
                            content = json.loads(content)
                            result.append(content)
            return result
    
    @staticmethod
    def save_structure(symbol:str,market:MARKET,date:str,datas:any):
        if datas:
            db = "structure"
            dir2 = date.replace("-","")
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(json.dumps(datas))
            CacheHelper.save_cache_date(CacheHelper.get_db_path(symbol,None,db))
    
    @staticmethod
    def get_structure(symbol:str,market:int,start:str=None,end:str=None):
        db = "structure"
        path = CacheHelper.get_db_path(symbol,None,db)
        # 如果今天没有缓存过，就不使用缓存
        if not end and not CacheHelper.today_is_cache_date(path):return
        dir_list:list = os.listdir(path)
        if not dir_list: return []
        if "last_date.txt" in dir_list: dir_list.remove("last_date.txt")
        dir_list.sort()
        date = ""
        if date=="":date = dir_list[-1]
        if not date : return []
        date = date.replace("-","")
        dir2 = date
        if not start and not end:
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            if not os.path.exists(filename): return
            with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                content = f.read()
                if content:
                    content = json.loads(content)
                    return content
        else:
            result = []
            if start==None: return result
            if end==None:end = datetime.datetime.strftime("%Y%m%d")
            start = start.replace("-","")
            end = end.replace("-","")
            for date in dir_list:
                if int(date)>=int(start) and int(date)<=int(end):
                    filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
                    if not os.path.exists(filename): return
                    with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                        content = f.read()
                        if content:
                            content = json.loads(content)
                            result.append(content)
            return result
    
    @staticmethod
    def save_sharebonus(symbol:str,market:MARKET,date:str,datas:any):
        if datas:
            db = "sharebonus"
            dir2 = date.replace("-","")
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(json.dumps(datas))
            CacheHelper.save_cache_date(CacheHelper.get_db_path(symbol,None,db))
    
    @staticmethod
    def get_sharebonus(symbol:str,market:int,start:str=None,end:str=None):
        db = "sharebonus"
        path = CacheHelper.get_db_path(symbol,None,db)
        # 如果今天没有缓存过，就不使用缓存
        if not date and not CacheHelper.today_is_cache_date(path):return

        dir_list:list = os.listdir(path)
        if not dir_list: return []
        if "last_date.txt" in dir_list: dir_list.remove("last_date.txt")
        dir_list.sort()
        date = ""
        if date=="":date = dir_list[-1]
        if not date : return []
        date = date.replace("-","")
        dir2 = date
        if not start and not end:
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            if not os.path.exists(filename): return
            with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                content = f.read()
                if content:
                    content = json.loads(content)
                    return content
        else:
            result = []
            if start==None: return result
            if end==None:end = datetime.datetime.strftime("%Y%m%d")
            start = start.replace("-","")
            end = end.replace("-","")
            for date in dir_list:
                if int(date)>=int(start) and int(date)<=int(end):
                    filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
                    if not os.path.exists(filename): return
                    with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
                        content = f.read()
                        if content:
                            content = json.loads(content)
                            result.append(content)
            return result
    
    @staticmethod
    def save_timesharing(symbol:str,market:MARKET,date:str,datas:any):
        if datas:
            db = "timesharing"
            dir2 = date.replace("-","")
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(json.dumps(datas))
            CacheHelper.save_cache_date(CacheHelper.get_db_path(symbol,None,db))
    
    @staticmethod
    def get_timesharing(symbol:str,market:int,date:str=None):
        db = "timesharing"
        path = CacheHelper.get_db_path(symbol,None,db)
        # 如果今天没有缓存过，就不使用缓存
        if not date and not CacheHelper.today_is_cache_date(path):return

        dir_list:list = os.listdir(path)
        if not dir_list: return []
        if "last_date.txt" in dir_list: dir_list.remove("last_date.txt")
        dir_list.sort()
        if not date:date = dir_list[-1]
        if not date : return []
        date = date.replace("-","")
        dir2 = date
        filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
        if not os.path.exists(filename): return
        with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
            content = f.read()
            if content:
                content = json.loads(content)
                return content
    
    @staticmethod
    def save_translist(symbol:str,market:MARKET,date:str,datas:any,page:int=1,page_size:int=10):
        if datas:
            db = "translist"
            dir2 = date.replace("-","")
            dir2 += "/%s-%s" % (page,page_size)
            filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
            with open(filename,mode="w",encoding=CacheHelper.encoding) as f:
                f.write(json.dumps(datas))
            CacheHelper.save_cache_date(os.path.dirname(filename))
    
    @staticmethod
    def get_translist(symbol:str,market:int,date:str=None,page:int=1,page_size:int=10):
        db = "translist"
        path = CacheHelper.get_db_path(symbol,None,db)
        dir_list:list = os.listdir(path)
        if not dir_list: return []
        dir_list.sort()
        if not date:date = dir_list[-1]
        if not date : return []
        date = date.replace("-","")
        dir2 = date
        dir2 += "/%s-%s" % (page,page_size)
        filename = CacheHelper.get_db_filename(symbol,market,symbol,dir2,db)
        # 如果今天没有缓存过，就不使用缓存
        if not date and not CacheHelper.today_is_cache_date(os.path.dirname(filename)):return

        if not os.path.exists(filename): return
        with open(filename,mode="r",encoding=CacheHelper.encoding) as f:
            content = f.read()
            if content:
                datas:list = json.loads(content)
                # datas.reverse()
                # start = (page-1) * page_size
                # end = page * page_size
                # datas = datas[start:end]
                return datas