from typing import Optional
from pydantic import BaseModel,validator
import models


class Usercreate(BaseModel):
    username:str 
    email:str
    phone:int
    password:str
    role:str

    @validator('role')
    def role_name(cls, v):
        from helpers import get_role_info
        if v in get_role_info():
            return v
        raise "error"


class Rolecreate(BaseModel):
    role_name:str

class Userupdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[int] = None
    email:str

