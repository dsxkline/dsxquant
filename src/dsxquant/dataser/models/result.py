
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
        
    