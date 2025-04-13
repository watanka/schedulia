# tests/conftest.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# 테스트 환경 변수 설정
os.environ["TESTING"] = "true"
os.environ['GMAIL_USERNAME'] = 'test@test.com'
os.environ['GMAIL_APP_PASSWORD'] = 'test'

# 경로 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# DatabaseFactory 패치 준비 - main 모듈 임포트 전에 적용
from src.db.factory import DatabaseFactory
# 이미 구현된 MemoryDatabase 사용
from src.db.memory_db import MemoryDatabase

# 이메일 서비스 모킹
mock_email_service = MagicMock()
mock_email_service.send_meeting_request_email = AsyncMock()

# 이메일 서비스 모듈 패치
sys.modules['src.email_service'] = MagicMock()
sys.modules['src.email_service'].email_service = mock_email_service

# DB_CONFIG를 메모리 DB를 사용하도록 패치
import config
original_db_config = config.DB_CONFIG
config.DB_CONFIG = {"type": "memory"}

# DatabaseFactory를 패치하여 이미 준비된 MemoryDB 인스턴스 반환
memory_db = MemoryDatabase()
original_create_database = DatabaseFactory.create_database
DatabaseFactory.create_database = MagicMock(return_value=memory_db)

# 이제 main과 모델 임포트
from src.models import User, Time, MeetingRequest
from main import app, get_current_user

# 테스트용 사용자 생성
test_user = User(id=1, name="John Doe", email="john.doe@example.com")

# 테스트 데이터 초기화
memory_db.create_user(name=test_user.name, email=test_user.email)

# 사용자 인증 오버라이드
async def override_get_current_user():
    return test_user

app.dependency_overrides[get_current_user] = override_get_current_user

# 픽스처들
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return test_user

@pytest.fixture
def email_service():
    mock_email_service.send_meeting_request_email.reset_mock()
    return mock_email_service

# 테스트 종료 후 원래 설정 복원
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    DatabaseFactory.create_database = original_create_database
    config.DB_CONFIG = original_db_config
    app.dependency_overrides.clear()