from email.policy import default
from enum import unique
from sqlalchemy import Column,Integer,ForeignKey,String,DateTime
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy.types import DateTime
from database import Base



class Role(Base):
    __tablename__ = "role"
    id = Column (Integer,primary_key=True,index=True,autoincrement=True)
    role_name = Column(String(100), index=True, unique=True, default=None)
    created_on=Column(DateTime,default=datetime.datetime.utcnow)


class User(Base):
    __tablename__= "user"
    id = Column(Integer,primary_key=True)
    username = Column(String(200),index=True,default=None)
    email = Column(String(200),unique=True)
    phone = Column(String(10),default=None)
    password = Column(String(240),nullable=False)
    created_at= Column(DateTime,default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=None)
    role_id = Column(Integer, ForeignKey('role.id', ondelete='SET NULL'))
    role = relationship('Role',foreign_keys='User.role_id')
    usersession=relationship("Usersession", back_populates="user")

    def payload(self):
        return {
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "role":self.role.role_name,
            "created_at":self.created_at
        }
        

class Usersession(Base):
    __tablename__ = "usersession"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    access_token = Column(String(200))
    refresh_token = Column(String(200))
    created_at=Column(DateTime,default=datetime.datetime.utcnow)
    user_id=Column(Integer,ForeignKey("user.id",ondelete="CASCADE"))
    user = relationship(
        'User', foreign_keys='Usersession.user_id',back_populates="usersession")