import json
from typing import Callable, TypeVar

T = TypeVar("T")

class Json2Model:
    def __init__(self,jsonstr):
        try:
            if type(jsonstr)==str:
                self.json = json.loads(jsonstr)
            else:
                self.json = jsonstr
        except Exception as ex:
            print(ex)
    
    def trans_model(self,model:Callable[..., T]):
        self.model = model
        def trans() -> T:
            return self.__trans()
        return trans()
        
    def __trans(self):
        if type(self.json)==dict:
            return self.__transObj(self.json)
        
        if type(self.json)==list:
            result = []
            for o in list(self.json):
                obj = self.__transObj(o)
                result.append(obj)
            return result

    def __transObj(self,json):
        if type(json)==dict:
            obj = self.model()
            for k,v in dict(json).items():
                if hasattr(obj,k):
                    obj.__setattr__(k,v)
            return obj

