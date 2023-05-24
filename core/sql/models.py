from sqlalchemy import Column, Integer, String, Boolean, Identity
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, autoincrement=True, )
    email = Column(String, unique=True)
    hashed_password = Column(String)
    confirmed = Column(Boolean)
    session_str = Column(String)

class Files(Base):
    __tablename__ = "Files"
    id = Column(String, primary_key=True)
    owner = Column(Integer)
    name = Column(String)
    size = Column(Integer)
    holder = Column(Integer)

class Deletes(Base):
    __tablename__ = "deletes",
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, autoincrement=True, )
    name = Column(String)
    owner = Column(Integer)

class Folders(Base):
    __tablename__ = "Folders"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, autoincrement=True, )
    name = Column(String)
    owner = Column(Integer)
    holder = Column(Integer)
