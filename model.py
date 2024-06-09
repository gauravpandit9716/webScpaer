from fastapi import FastAPI
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
import databases
from typing import List

#Database credentials
username = 'root'
password = 'Gaurav#9716'
host = 'localhost'
port = '3306'  # Default MySQL port
database = 'scraper'

DATABASE_URL = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

Base = declarative_base()

class ScrapeStatus(Base):
    __tablename__ = "scrape_status"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), index=True)
    created_at = Column(DateTime, default=func.now(), index=True)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    points = Column(Integer)
    author = Column(String(50))
    posted_time = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    text = Column(String(1024))
    post = relationship("Post", back_populates="comments")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class PostCreate(BaseModel):
    title: str
    points: int
    author: str
    posted_time: str
    comments: List[str]

class PostResponse(BaseModel):
    id: int
    title: str
    points: int
    author: str
    posted_time: str
    comments: dict

    class Config:
        orm_mode = True

class StatusResponse(BaseModel):
    status: str
    created_at: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_status(db: Session, status: str):
    db_status = ScrapeStatus(status=status)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

def update_status(db: Session, db_status: ScrapeStatus, status: str):
    db_status.status = status
    db.commit()
    db.refresh(db_status)
