from datetime import datetime,timedelta
from typing import Any,Union
import models
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2566c818166b7a9563b93f7099f8f0f4caa6cf63b88e8d4e7"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 10
REFRESH_EXPIRE_MINUTES = 60 * 7


def get_role_info(db:Session):
    roles=db.query(models.Role.role_name).all()
    print(list(zip(*roles))[0])
    return list(zip(*roles))[0]

def get_email(db:Session,email:str):
    return db.query(models.User).filter(models.User.email==email).first()

def verify_password(password,hash_password):
    return pwd_context.verify(password,hash_password)

def hash_password(password):
    return pwd_context.hash(password)

def get_rolename(db:Session,role_name):
    return db.query(models.Role).filter(models.Role.role_name==role_name).first()

def access_token(subject: Union[str, Any], expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY, ALGORITHM)
    return encoded_jwt

def refresh_token(subject: Union[str, Any], expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY, ALGORITHM)
    return encoded_jwt