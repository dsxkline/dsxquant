from dsxquant.engins.base import BaseEngin
import dsxquant
from dsxquant import config,logger,EventModel,Engin
from dsxquant.config.config import EventType
from progressbar import ProgressBar

class DataFeed(BaseEngin):
    __name__ = "数据响应"

    def __init__(self):
        super().__init__()

    @property
    def engin_cache(self):
        return Engin.get_instance().cachespace
    
    def run(self):
        while(not self.exit):
            if self.event and self.event.target==self.__class__:
                # if self.event.type==EventType.DAYLINE:
                args = self.event.data
                self.downall(self.event.type,args)
            if self.event:
                if self.event.type==EventType.THEEND:
                    pass
                    # break
            # 处理后销毁
            self.destroy()
            self.next()
    
    def downall(self,etype:EventType,*args):
        
        # 下载数据
        cycle = None
        if etype==EventType.DAYLINE:cycle=config.CYCLE.DAY
        if etype==EventType.WEEKLINE:cycle=config.CYCLE.WEEK
        if etype==EventType.MONTHLINE:cycle=config.CYCLE.MONTH
        if etype==EventType.YEARLINE:cycle=config.CYCLE.YEAR
        if etype==EventType.MIN1LINE:cycle=config.CYCLE.M1
        if etype==EventType.MIN5LINE:cycle=config.CYCLE.M5
        if etype==EventType.MIN15LINE:cycle=config.CYCLE.M15
        if etype==EventType.MIN30LINE:cycle=config.CYCLE.M30
        if etype==EventType.MIN60LINE:cycle=config.CYCLE.M60
        if cycle==None:return
        pbar = ProgressBar(100)
        pbar.start()
        symbol,market,fq,start_date,end_date,base_symbol = args[0]
        klines = self.dayline(symbol,market,fq=fq,cycle=cycle,start=start_date,end=end_date)
        if not klines:
            pbar.update(100)
            logger.error("无法获取K线数据")
            self.sendevent(EventType.THEEND,klines,self.event.source,source=self)
            return
        pbar.update(25)
        base_klines = self.dayline(base_symbol,market,fq=fq,cycle=cycle,start=start_date,end=end_date)
        pbar.update(50)
        self.finance(symbol,market,start_date,end_date)
        pbar.update(75)
        self.structure(symbol,market,start_date,end_date)
        pbar.update(100)
        # 给回测
        self.sendevent(etype,klines,self.event.source,source=self)
        # self.sendevent(etype,base_klines,dsxquant.BackTest,source=self.event.source)
    
    def dayline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def weekline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.WEEK,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def monthline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.MONTH,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def yearline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.YEAR,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def min1line(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M1,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def min5line(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M5,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def min15line(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M15,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def min30line(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M30,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    def min60line(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.M60,start:str=None,end:str=None):
        return self.barline(symbol,market,page,page_size,fq,cycle,start,end)
    
    def barline(self,symbol:str,market:int,page:int=1,page_size:int=320,fq:str=config.FQ.DEFAULT,cycle:config.CYCLE=config.CYCLE.DAY,start:str=None,end:str=None):
        try:
            result = dsxquant.get_klines(symbol,market,page,page_size,fq,cycle,start,end).datas()
            if result.success:
                data:list = result.data
                data.reverse()
                self.engin_cache.set_klines(symbol,market,data)
                data = (symbol,market,data)
                return data
            else:
                logger.info(result.msg)
        except Exception as e:
            logger.error(e)

    def finance(self,symbol:str,market:int,start:str,end:str):
        try:
            if start.__len__()==8:
                start = start[:4]+"-"+start[4:6]+"-"+start[6:8]
            if end.__len__()==8:
                end = end[:4]+"-"+end[4:6]+"-"+end[6:8]
            result = dsxquant.get_finance(symbol,market,start=start,end=end).datas()
            if result.success:
                data:list = result.data
                self.engin_cache.set_finance(symbol,market,data)
                data = (symbol,market,data)
                return data
            else:
                logger.info(result.msg)
        except Exception as e:
            logger.error(e)
    
    def structure(self,symbol:str,market:int,start:str,end:str):
        try:
            if start.__len__()==8:
                start = start[:4]+"-"+start[4:6]+"-"+start[6:8]
            if end.__len__()==8:
                end = end[:4]+"-"+end[4:6]+"-"+end[6:8]
            result = dsxquant.get_structure(symbol,market,start,end).datas()
            if result.success:
                data:list = result.data
                self.engin_cache.set_structure(symbol,market,data)
                data = (symbol,market,data)
                return data
            else:
                logger.info(result.msg)
        except Exception as e:
            logger.error(e)
    



    
   