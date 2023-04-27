
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
        obj = self.__repr__()
        #print(jsonstr)
        return json.dumps(obj)
    
    def dict(self):
        return self.__repr__()

    def __repr__(self) -> str:
        return {"msg":self.msg,"error_code":self.error_code,"success":self.success,"data":self.data,"request_id":self.request_id,"act":self.act}
        
    