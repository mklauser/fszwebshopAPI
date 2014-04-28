__author__ = 'michi'
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from fszwebshopAPI import metadata


class Customer(Base):
    __table__ = Table('oc_customer', metadata, autoload=True)








