from django.db.backends import postgresql
from fastapi import FastAPI,Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Annotated

Base = declarative_base()

DATABASE_URL = "postgresql://postgres.caidvnxutiuhemnlmawr:Passcoderakibdeactive24@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
engine = create_engine(DATABASE_URL)

Sessionlocal = sessionmaker(autoflush = False, autocommit = False, bind = engine)


