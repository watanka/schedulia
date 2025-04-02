from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import secrets
from datetime import datetime

from src.db.base import DatabaseInterface
from src.db.db_model import (
    Base, UserModel, APIKeyModel, TimeModel, 
    MeetingScheduleModel, MeetingRequestModel
)
from src.models import User, APIKey, Time, MeetingSchedule, MeetingRequest

class PostgresDatabase(DatabaseInterface):
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def _convert_user_model(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            api_keys=[
                APIKey(
                    key=key.key,
                    user_id=key.user_id,
                    created_at=key.created_at,
                    is_active=key.is_active
                ) for key in user_model.api_keys
            ]
        )
    
    def _convert_time_model(self, time_model: TimeModel) -> Time:
        return Time(
            start_time=time_model.start_time,
            end_time=time_model.end_time
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        with self.Session() as session:
            user = session.query(UserModel).filter(UserModel.email == email).first()
            if user:
                return User(
                    id=user.id,
                    name=user.name,
                    email=user.email    
                )
            return None  # 사용자를 찾지 못한 경우 None 반환
    
    def create_user(self, name: str, email: str) -> User:
        with self.Session() as session:
            user_model = UserModel(name=name, email=email)
            session.add(user_model)
            session.commit()
            return self._convert_user_model(user_model)
    
    def get_user(self, user_id: int) -> Optional[User]:
        with self.Session() as session:
            user_model = session.query(UserModel).get(user_id)
            return self._convert_user_model(user_model) if user_model else None
    
    def create_schedule(self, schedule: MeetingSchedule) -> MeetingSchedule:
        with self.Session() as session:
            time_model = TimeModel(
                start_time=schedule.time.start_time,
                end_time=schedule.time.end_time
            )
            
            schedule_model = MeetingScheduleModel(
                host_id=schedule.host.id,
                title=schedule.title,
                description=schedule.description,
                time=time_model
            )
            
            # 참가자 추가
            for participant in schedule.participants:
                participant_model = session.query(UserModel).get(participant.id)
                if participant_model:
                    schedule_model.participants.append(participant_model)
            
            session.add(schedule_model)
            session.commit()
            
            return MeetingSchedule(
                id=schedule_model.id,
                host=self._convert_user_model(schedule_model.host),
                participants=[self._convert_user_model(p) for p in schedule_model.participants],
                time=self._convert_time_model(schedule_model.time),
                title=schedule_model.title,
                description=schedule_model.description
            )
    
    def get_schedule(self, schedule_id: int) -> Optional[MeetingSchedule]:
        with self.Session() as session:
            schedule_model = session.query(MeetingScheduleModel).get(schedule_id)
            if not schedule_model:
                return None
                
            return MeetingSchedule(
                id=schedule_model.id,
                host=self._convert_user_model(schedule_model.host),
                participants=[self._convert_user_model(p) for p in schedule_model.participants],
                time=self._convert_time_model(schedule_model.time),
                title=schedule_model.title,
                description=schedule_model.description
            )
    
    def get_user_schedules(self, user_id: int) -> List[MeetingSchedule]:
        with self.Session() as session:
            schedule_models = session.query(MeetingScheduleModel).filter(
                (MeetingScheduleModel.host_id == user_id) |
                (MeetingScheduleModel.participants.any(id=user_id))
            ).all()
            
            return [
                MeetingSchedule(
                    id=sm.id,
                    host=self._convert_user_model(sm.host),
                    participants=[self._convert_user_model(p) for p in sm.participants],
                    time=self._convert_time_model(sm.time),
                    title=sm.title,
                    description=sm.description
                ) for sm in schedule_models
            ]
    
    def create_request(self, request: MeetingRequest) -> MeetingRequest:
        with self.Session() as session:
            # 가능한 시간들 생성
            time_models = [
                TimeModel(start_time=t.start_time, end_time=t.end_time)
                for t in request.available_times
            ]
            
            request_model = MeetingRequestModel(
                sender_id=request.sender.id,
                receiver_email=request.receiver_email,
                title=request.title,
                description=request.description,
                status=request.status,
                available_times=time_models
            )
            
            session.add(request_model)
            session.commit()
            
            return MeetingRequest(
                request_id=request_model.id,
                sender=self._convert_user_model(request_model.sender),
                receiver_email=request_model.receiver_email,
                available_times=[self._convert_time_model(t) for t in request_model.available_times],
                status=request_model.status,
                title=request_model.title,
                description=request_model.description,
                selected_time=self._convert_time_model(request_model.selected_time) if request_model.selected_time else None
            )
    
    def get_request(self, request_id: int) -> Optional[MeetingRequest]:
        with self.Session() as session:
            request_model = session.query(MeetingRequestModel).get(request_id)
            if not request_model:
                return None
            
            return MeetingRequest(
                request_id=request_model.id,
                sender=self._convert_user_model(request_model.sender),
                receiver_email=request_model.receiver_email,
                available_times=[self._convert_time_model(t) for t in request_model.available_times],
                status=request_model.status,
                title=request_model.title,
                description=request_model.description,
                selected_time=self._convert_time_model(request_model.selected_time) if request_model.selected_time else None
            )
    
    def get_user_received_requests(self, user_email: str) -> List[MeetingRequest]:
        with self.Session() as session:
            request_models = session.query(MeetingRequestModel).filter(
                MeetingRequestModel.receiver_email == user_email
            ).all()
            
            return [
                MeetingRequest(
                    request_id=rm.id,
                    sender=self._convert_user_model(rm.sender),
                    receiver_email=rm.receiver_email,
                    available_times=[self._convert_time_model(t) for t in rm.available_times],
                    status=rm.status,
                    title=rm.title,
                    description=rm.description,
                    selected_time=self._convert_time_model(rm.selected_time) if rm.selected_time else None
                ) for rm in request_models
            ]
    
    def create_api_key(self, user_id: int) -> APIKey:
        with self.Session() as session:
            user_model = session.query(UserModel).get(user_id)
            if not user_model:
                raise ValueError(f"User with id {user_id} not found")
            
            api_key = APIKeyModel(
                key=f"mcp_{secrets.token_urlsafe(32)}",
                user_id=user_id
            )
            
            session.add(api_key)
            session.commit()
            
            return APIKey(
                key=api_key.key,
                user_id=api_key.user_id,
                created_at=api_key.created_at,
                is_active=api_key.is_active
            )
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        with self.Session() as session:
            api_key_model = session.query(APIKeyModel).filter(
                APIKeyModel.key == api_key,
                APIKeyModel.is_active == True
            ).first()
            
            if not api_key_model:
                return None
            
            # 디버깅 로그 추가
            print(f"Found API key: {api_key_model.key}, user_id: {api_key_model.user_id}")
            
            user_model = session.query(UserModel).get(api_key_model.user_id)
            if not user_model:
                print(f"User not found for user_id: {api_key_model.user_id}")
                return None
            
            print(f"Found user: {user_model.email} for API key: {api_key}")
            return self._convert_user_model(user_model)
    
    def deactivate_api_key(self, api_key: str) -> bool:
        with self.Session() as session:
            api_key_model = session.query(APIKeyModel).filter(
                APIKeyModel.key == api_key
            ).first()
            
            if not api_key_model:
                return False
                
            api_key_model.is_active = False
            session.commit()
            return True
    
    def update_request_status(self, request_id: int, status: str, selected_time: Optional[Time] = None) -> MeetingRequest:
        with self.Session() as session:
            request_model = session.query(MeetingRequestModel).get(request_id)
            if not request_model:
                raise ValueError(f"Request with id {request_id} not found")
            
            request_model.status = status
            if selected_time:
                # 선택된 시간이 가능한 시간 중 하나인지 확인
                matching_time = next(
                    (t for t in request_model.available_times 
                     if t.start_time == selected_time.start_time and t.end_time == selected_time.end_time),
                    None
                )
                
                if not matching_time:
                    raise ValueError("Selected time is not in available times")
                
                request_model.selected_time = matching_time
                
            session.commit()
            
            return MeetingRequest(
                request_id=request_model.id,
                sender=self._convert_user_model(request_model.sender),
                receiver_email=request_model.receiver_email,
                available_times=[self._convert_time_model(t) for t in request_model.available_times],
                status=request_model.status,
                title=request_model.title,
                description=request_model.description,
                selected_time=self._convert_time_model(request_model.selected_time) if request_model.selected_time else None
            )

    def get_active_api_key(self, user_id: int) -> Optional[APIKey]:
        """사용자의 활성화된 API 키를 반환합니다."""
        with self.Session() as session:
            api_key_model = session.query(APIKeyModel).filter(
                APIKeyModel.user_id == user_id,
                APIKeyModel.is_active == True
            ).first()
            
            if not api_key_model:
                return None
                
            return APIKey(
                key=api_key_model.key,
                user_id=api_key_model.user_id,
                created_at=api_key_model.created_at,
                is_active=api_key_model.is_active
            )