# -*- encoding: utf-8 -*-


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import StaleDataError

Base = declarative_base()

class Record(Base):
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True)
    data = Column(String)
    version = Column(Integer)