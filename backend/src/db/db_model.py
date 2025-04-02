from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 다대다 관계를 위한 연결 테이블
meeting_participants = Table(
    'meeting_participants',
    Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meeting_schedules.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    api_keys = relationship("APIKeyModel", back_populates="user")
    hosted_meetings = relationship("MeetingScheduleModel", back_populates="host")
    participated_meetings = relationship("MeetingScheduleModel", secondary=meeting_participants)
    sent_requests = relationship("MeetingRequestModel", back_populates="sender")

class APIKeyModel(Base):
    __tablename__ = 'api_keys'
    
    key = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user = relationship("UserModel", back_populates="api_keys")

class TimeModel(Base):
    __tablename__ = 'times'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    meeting_request_id = Column(Integer, ForeignKey('meeting_requests.id'), nullable=True)
    is_selected = Column(Boolean, default=False)  # 미팅 요청에서 선택된 시간인지 여부
    meeting_schedule = relationship("MeetingScheduleModel", back_populates="time", uselist=False)
    meeting_request = relationship("MeetingRequestModel", back_populates="available_times", foreign_keys=[meeting_request_id])

class MeetingScheduleModel(Base):
    __tablename__ = 'meeting_schedules'
    
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('users.id'))
    time_id = Column(Integer, ForeignKey('times.id'))
    title = Column(String, nullable=False)
    description = Column(String)
    
    host = relationship("UserModel", back_populates="hosted_meetings")
    participants = relationship("UserModel", secondary=meeting_participants)
    time = relationship("TimeModel", back_populates="meeting_schedule", foreign_keys=[time_id])

class MeetingRequestModel(Base):
    __tablename__ = 'meeting_requests'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_email = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="PENDING")
    
    sender = relationship("UserModel", back_populates="sent_requests")
    available_times = relationship("TimeModel", back_populates="meeting_request", foreign_keys=[TimeModel.meeting_request_id])
    selected_time_id = Column(Integer, ForeignKey('times.id'), nullable=True)
    selected_time = relationship("TimeModel", foreign_keys=[selected_time_id], overlaps="available_times")

