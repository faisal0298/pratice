from email.headerregistry import DateHeader
from typing import Optional
from pydantic import BaseModel,validator
import tasktest.models as models
import datetime



class Usercreate(BaseModel):
    username:str 
    email:str
    phone:int
    password:str
    role:str

    @validator('role')
    def role_name(cls, v):
        from tasktest.helpers import get_role_info
        from tasktest.database import get_db
        if v in get_role_info(db=get_db()):
            return v
        raise "error"


class Rolecreate(BaseModel):
    role_name:str

class Userupdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[int] = None
    email:str

class passwordupdate(BaseModel):
    password: str
    email : str

class CreateOTP(BaseModel):
    email: str

class verifyOTP(BaseModel):
    otp_code: str

class reqcreate(BaseModel):
    name:str
    gender:str
    email:str 
    status:Optional[str]= None

