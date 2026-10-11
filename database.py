import os

from django.db.backends import postgresql
from fastapi import FastAPI,Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Annotated

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

Sessionlocal = sessionmaker(autoflush = False, autocommit = False, bind = engine)


