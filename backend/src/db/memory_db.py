from typing import Dict, Optional
from src.models import User, MeetingSchedule, MeetingRequest, APIKey, Time
from src.db.base import DatabaseInterface

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
        user = next((user for user in self.users.values() if user.email == email), None)
        if user is None:
            raise ValueError(f"User with email {email} not found")
        return user
    
    # ... (나머지 메서드 구현)