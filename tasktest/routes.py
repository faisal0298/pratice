from collections import UserString
from dataclasses import dataclass
from datetime import date, datetime
from urllib import response
from fastapi import APIRouter,Response, status, Header, Depends
import tasktest.models as models
import tasktest.serializer as serializer
from tasktest.serializer import Rolecreate, Usercreate,Userupdate, passwordupdate,CreateOTP, verifyOTP
import tasktest.helpers as helpers
from sqlalchemy.orm import Session
from tasktest.database import get_db,engine
from fastapi import FastAPI, HTTPException
from typing import Optional,Union
from fastapi.security import HTTPBasicCredentials,HTTPBearer
from jose import JWTError, jwt
from tasktest.helpers import SECRET_KEY, ALGORITHM, access_token
from tasktest.logger import console_logger
import pyotp 
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os


# file_path= "/home/diycam/Desktop/task/workspac/"         
file_path=os.path.join(os.getcwd(),"workspace")         #always use his method to give path

otp={}

models.Base.metadata.create_all(bind=engine)

router = FastAPI()

# automatically add roles when started when nothing is present in database
@router.on_event("startup")
def add_role():
    db=get_db()
    if not db.query(models.Role).count()>=3:
        role=[models.Role(role_name="superadmin"),
          models.Role(role_name="admin"),
          models.Role(role_name="member")
          ]

        db.add_all(role)
        db.commit()
        return 


# @router.post("/add_role")
# def get_role(response:Response,role=Rolecreate,db:Session=Depends(get_db)):
#     rolename=helpers.get_rolename(db,role.role_name)
#     if rolename:
#         response.status_code=409
#         return "User Exits"

#     _role=models.Role(role_name=role.role_name)

#     db.add(_role)
#     db.commit()
#     return "success"


@router.get("/role")
def get_role(db:Session=Depends(get_db)):
    roles=db.query(models.Role).all()
    return roles


@router.get("/user")
def get_user(response:Response,email:Optional[str]=None,db:Session=Depends(get_db)):

    if email:
        _user=helpers.get_email(db,email)
        if _user:
            return _user.payload()
        else:
            response.status_code=404
            return "Not Found"
    else:
        users=db.query(models.User).all()
        
        all_users=[]

        for data in users:
            all_users.append(data.payload())
        return all_users


@router.post("/user/signup")
def signup(response:Response, user:Usercreate, db:Session = Depends(get_db)):
    _user=helpers.get_email(db,user.email)
    rolename=helpers.get_rolename(db,user.role)
    console_logger.debug(user.dict(exclude_none=True))

    if _user:
        response.status_code=409
        return "User Exits"
    _user=models.User(username=user.username,email=user.email,phone=user.phone,
                      password=helpers.hash_password(user.password),role_id=rolename.id)
    
    db.add(_user)
    db.commit()    
    return _user.payload()


@router.post("/user/signin")
def signin(response:Response,email:str=Header(...),password:str=Header(...),db:Session=Depends(get_db)):
    user=helpers.get_email(db,email)

    if not user:
        response.status_code=404
        return "User not found"

    _password=helpers.verify_password(password,user.password)

    if not _password:
        response.status_code=401
        return "Incorrect Password"

    access=helpers.access_token(user.email)
    refresh=helpers.refresh_token(user.email)
    db_user = models.Usersession(
                                access_token=access,
                                refresh_token=refresh,
                                user_id=user.id
                                 )
    db.add(db_user)     
    db.commit()
    return {
        "access_token":access,
        "refresh_token":refresh,
        "user_data":user.payload()
    }

# def token_validate(token=Depends(HTTPBearer())):
#     console_logger.debug(token)
#     return token

@router.post("/token/validate")
def validate_token(response:Response ,credentials:HTTPBasicCredentials = Depends(HTTPBearer()),
                   db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    token = credentials.credentials
    
    check=db.query(models.Usersession).filter(models.Usersession.access_token == token).first()

    if check==None:
        response.status_code = 401
        return "Invalid"

    usercheck=db.query(models.User).filter(models.User.id == check.user_id).first()

    try:
        Payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if Payload is None:
            raise credentials_exception
        return usercheck.payload()
    except JWTError:
        raise credentials_exception


@router.post("/Authorize/refresh")
def Authorize_refresh(response:Response ,credentials:HTTPBasicCredentials = Depends(HTTPBearer()),
                   db: Session = Depends(get_db)):
    
    token = credentials.credentials

    check=db.query(models.Usersession).filter(models.Usersession.refresh_token==token).first()

    if not check:
        response.status_code = 401
        return "Invalid"

    usercheck=db.query(models.User).filter(models.User.id == check.user_id).first()
    new_access_token = access_token(usercheck.email)
    console_logger.debug(new_access_token)
    check.access_token=new_access_token
    db.commit()
    return new_access_token


@router.post("/logout")
def logout(response:Response,credentials:HTTPBasicCredentials = Depends(HTTPBearer()),
                    db:Session=Depends(get_db)):

    token=credentials.credentials

    user=db.query(models.Usersession).filter(models.Usersession.access_token == token).first()
    console_logger.debug(user)
    if not user:
        response.status_code = 403
        return "user doesnt exist"
    db.delete(user)
    db.commit()
    return "logout successfully"

@router.patch("/forgot")
def forgot_password(response:Response, user:passwordupdate, db:Session=Depends(get_db)):
    _user=db.query(models.User).filter(models.User.email==user.email).first()

    if not _user:
        response.status_code=404
        return "Invalid Email"
    
    _user.password=helpers.hash_password(user.password)
    db.commit()
    return user.email


@router.put("/update")
def update(response:Response,user:Userupdate,db:Session=Depends(get_db)):

    _user=db.query(models.User).filter(models.User.email==user.email).first()

    if not _user:
        response.status_code=404
        return "user not found"
    
    _user.username=user.username
    _user.phone=user.phone
    _user.updated_at=datetime.utcnow()

    db.commit()
    return user


@router.get("/datacollect")
def created(response:Response, createdAt:Optional[str]=None, end:Optional[str]=None, db:Session=Depends(get_db)):

    # end=datetime.utcnow()
    created=db.query(models.User).filter(models.User.created_at.between(createdAt,end)).all()
    all_users=[]

    if created:
        for data in created:
            all_users.append(data.payload())
        console_logger.debug(created)
        return all_users
    else:
        response.status_code=404
        return all_users
    

@router.post("/otp/send")
def send_otp(response:Response, email:CreateOTP,db:Session=Depends(get_db)):
    global otp

    user=db.query(models.User).filter(models.User.email==email.email).first()

    if not user:
        response.status_code=404
        return "user not found"

    # totp = pyotp.TOTP(OTP_Secret)
    totp=helpers.OTP().generatetotp()
    # code=totp.now()

    otp[email.email]={"OTP":totp,"created":datetime.utcnow()}
    console_logger.debug(otp)
    return totp

  
@router.post("/check/otp")
def verify_otp(response:Response,verify:verifyOTP):
    global otp 

    code=helpers.OTP().verifyotp(verify.otp_code)
    if not code: 
        response.status_code=404
        return "invalid"
    return "success"


@router.post("/uploadfile")
def create_upload_file(file: UploadFile = File(...)):
    print(file.filename,file.file)
    with open(f'{file_path}/{file.filename}',"wb",buffering=0) as buffer:
        shutil.copyfileobj(file.file,buffer)
    return {"filename":file.filename}


@router.post('/chat/send')
def send_message(msg: str):
    with open(f'{file_path}/faisal.txt', "a") as file_object:
        file_object.write(f"{msg} \n")
    return "success"

@router.get("/chat/read")
def read_message():
    with open(f'{file_path}/faisal.txt', "r") as f:
        msg=f.readlines()
    return msg
