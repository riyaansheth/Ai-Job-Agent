from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("JobApplication", back_populates="user")

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    job_id = Column(Integer, nullable=False)
    job_title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(20), default='applied')  # applied, interviewed, rejected, accepted
    applied_date = Column(DateTime, default=datetime.utcnow)
    cover_letter = Column(Text)
    resume_path = Column(String(200))
    notes = Column(Text)
    
    user = relationship("User", back_populates="applications")

class JobSearch(Base):
    __tablename__ = 'job_searches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    query = Column(String(200))
    location = Column(String(100))
    search_date = Column(DateTime, default=datetime.utcnow)
    results_count = Column(Integer)
    
    user = relationship("User") 