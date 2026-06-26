from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column,String,Integer,DateTime,JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import uuid4
class Base(DeclarativeBase):
    pass

class TaskModel(Base):
    __tablename__="tasks"
    id= Column( PGUUID,primary_key=True,default=uuid4)
    title= Column(String,nullable=False)
    status= Column(String,nullable=False)
    user_id= Column(PGUUID)
    retry_count= Column(Integer,default=0)
    created_at= Column(DateTime(timezone=True))
    payload=Column(JSON)


class UserModel(Base):
    __tablename__ = "users"
    id = Column(PGUUID, primary_key=True, default=uuid4)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    
    
    