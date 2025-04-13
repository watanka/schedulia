from typing import Dict, Optional, List
from src.models import User, MeetingSchedule, MeetingRequest, APIKey, Time, RequestStatus
from src.db.base import DatabaseInterface
import secrets
from datetime import datetime

class MemoryDatabase(DatabaseInterface):
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.schedules: Dict[int, MeetingSchedule] = {}
        self.requests: Dict[int, MeetingRequest] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.next_user_id: int = 1
        self.next_schedule_id: int = 1
        self.next_request_id: int = 1
        
        # 테스트용 초기 데이터 (선택적)
        self._init_test_data()
    
    def _init_test_data(self):
        # 기존의 테스트 데이터 초기화 코드
        self.users = {
            1: User(id=1, name="John Doe", email="john.doe@example.com"),
            2: User(id=2, name="Jane Smith", email="jane.smith@example.com"),
            3: User(id=3, name="Alice Johnson", email="alice.johnson@example.com"),
        }
        # ... (나머지 테스트 데이터)

    # DatabaseInterface 구현
    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def create_user(self, name: str, email: str) -> User:
        # 이메일 중복 체크
        for user in self.users.values():
            if user.email == email:
                return user
        
        user_id = self.next_user_id
        self.next_user_id += 1
        
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
    
    def create_schedule(self, schedule: MeetingSchedule) -> MeetingSchedule:
        schedule_id = self.next_schedule_id
        self.next_schedule_id += 1
        
        # id 할당 및 저장
        new_schedule = MeetingSchedule(
            id=schedule_id,
            host=schedule.host,
            participants=schedule.participants,
            time=schedule.time,
            title=schedule.title,
            description=schedule.description
        )
        
        self.schedules[schedule_id] = new_schedule
        return new_schedule
    
    def get_schedule(self, schedule_id: int) -> Optional[MeetingSchedule]:
        return self.schedules.get(schedule_id)
    
    def get_user_schedules(self, user_id: int) -> List[MeetingSchedule]:
        return [
            schedule for schedule in self.schedules.values()
            if schedule.host.id == user_id or any(p.id == user_id for p in schedule.participants)
        ]
    
    def create_request(self, request: MeetingRequest) -> MeetingRequest:
        request_id = self.next_request_id
        self.next_request_id += 1
        
        # id 할당 및 저장
        new_request = MeetingRequest(
            request_id=request_id,
            sender=request.sender,
            receiver_email=request.receiver_email,
            available_times=request.available_times,
            status=request.status,
            title=request.title,
            description=request.description,
            selected_time=request.selected_time
        )
        
        self.requests[request_id] = new_request
        return new_request
    
    def get_meeting_request(self, request_id: int) -> Optional[MeetingRequest]:
        return self.requests.get(request_id)
    
    def get_user_received_requests(self, user_email: str) -> List[MeetingRequest]:
        return [
            request for request in self.requests.values()
            if request.receiver_email == user_email
        ]
    
    def create_api_key(self, user_id: int) -> APIKey:
        # 사용자 존재 여부 확인
        if user_id not in self.users:
            raise ValueError(f"User with id {user_id} not found")
        
        # 기존 API 키 비활성화
        for key in self.api_keys.values():
            if key.user_id == user_id and key.is_active:
                key.is_active = False
        
        # 새 API 키 생성
        api_key = APIKey(
            key=f"mcp_{secrets.token_urlsafe(32)}",
            user_id=user_id,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.api_keys[api_key.key] = api_key
        return api_key
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        if api_key not in self.api_keys or not self.api_keys[api_key].is_active:
            return None
        
        user_id = self.api_keys[api_key].user_id
        return self.users.get(user_id)
    
    def deactivate_api_key(self, api_key: str) -> bool:
        if api_key not in self.api_keys:
            return False
        
        self.api_keys[api_key].is_active = False
        return True
    
    def update_request_status(self, request_id: int, status: str, selected_time: Optional[Time] = None) -> MeetingRequest:
        if request_id not in self.requests:
            raise ValueError(f"Request with id {request_id} not found")
        
        request = self.requests[request_id]
        request.status = status
        
        if selected_time:
            request.selected_time = selected_time
        
        return request
    
    def get_active_api_key(self, user_id: int) -> Optional[APIKey]:
        for key in self.api_keys.values():
            if key.user_id == user_id and key.is_active:
                return key
        return None