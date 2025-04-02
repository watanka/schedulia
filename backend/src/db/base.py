from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from src.models import User, MeetingSchedule, MeetingRequest, APIKey, Time

class DatabaseInterface(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        pass
    
    @abstractmethod
    def create_user(self, name: str, email: str) -> User:
        """새로운 사용자 생성"""
        pass
    
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        pass
    
    @abstractmethod
    def create_schedule(self, schedule: MeetingSchedule) -> MeetingSchedule:
        """새로운 미팅 스케줄 생성"""
        pass
    
    @abstractmethod
    def get_schedule(self, schedule_id: int) -> Optional[MeetingSchedule]:
        """ID로 미팅 스케줄 조회"""
        pass
    
    @abstractmethod
    def get_user_schedules(self, user_id: int) -> List[MeetingSchedule]:
        """사용자의 모든 미팅 스케줄 조회"""
        pass
    
    @abstractmethod
    def create_request(self, request: MeetingRequest) -> MeetingRequest:
        """새로운 미팅 요청 생성"""
        pass
    
    @abstractmethod
    def get_request(self, request_id: int) -> Optional[MeetingRequest]:
        """ID로 미팅 요청 조회"""
        pass
    
    @abstractmethod
    def get_user_received_requests(self, user_email: str) -> List[MeetingRequest]:
        """사용자가 받은 모든 미팅 요청 조회"""
        pass
    
    @abstractmethod
    def create_api_key(self, user_id: int) -> APIKey:
        """새로운 API 키 생성"""
        pass
    
    @abstractmethod
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """API 키로 사용자 조회"""
        pass
    
    @abstractmethod
    def deactivate_api_key(self, api_key: str) -> bool:
        """API 키 비활성화"""
        pass

    @abstractmethod
    def update_request_status(self, request_id: int, status: str, selected_time: Optional[Time] = None) -> MeetingRequest:
        """미팅 요청 상태 업데이트"""
        pass

    @abstractmethod
    def get_active_api_key(self, user_id: int) -> Optional[APIKey]:
        """사용자의 활성화된 API 키를 반환합니다."""
        pass
