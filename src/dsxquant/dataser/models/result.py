
import json


class ResultModel(object):
    def __init__(self) -> None:
        self.msg:str = None
        self.success:bool = False
        self.data:any = None
        self.error_code:int = None
        self.request_id:int = None
        self.act:str = None
    
    def show_error(self,msg:str,error_code:int=0):
        self.msg = msg
        self.error_code = error_code
        return self
    
    def show(self,msg:str,success:bool,error_code:int,data:any,request_id:int,act:str):
        self.msg = msg
        self.error_code = error_code
        self.success = success
        self.data = data
        self.request_id = request_id
        self.act = act
        return self

    def json(self):
        jsonstr = self.__repr__().replace("\n","").replace("\r","").replace("\\","").replace("'","\"")
        #print(jsonstr)
        return json.loads(jsonstr)

    def __repr__(self) -> str:
        return """{"msg":"%s",
            "error_code":%s,
            "success":"%s",
            "data":%s,
            "request_id":%s,
            "act":"%s"}""" % (self.msg,self.error_code,self.success,self.data,self.request_id,self.act)
        
    