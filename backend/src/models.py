from pydantic import BaseModel, Field, EmailStr
from typing import List, Union
from datetime import datetime
from enum import Enum

class APIKey(BaseModel):
    key: str
    user_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    api_keys: List[APIKey] = []

class Time(BaseModel):
    start_time: datetime
    end_time: datetime

    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)

class MeetingSchedule(BaseModel):
    id: int
    host: User
    participants: List[User]
    time: Time
    title: str
    description: str | None = None

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

class MeetingRequest(BaseModel):
    request_id: int
    sender: User
    receiver_email: EmailStr
    available_times: List[Time]
    status: RequestStatus = RequestStatus.PENDING
    title: str
    description: str | None = None
    selected_time: Time | None = None  # 수락된 경우 선택된 시간 