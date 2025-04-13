import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.models import User, Time, MeetingRequest
from main import CreateMeetingRequest

def test_create_meeting_request(client, mock_user, email_service):
    # 테스트용 시간 객체 생성
    now = datetime.now()
    
    # 직접 JSON 데이터 구성
    request_data = {
        "receiver_email": "jane.doe@example.com",
        "available_times": [
            {
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(hours=1)).isoformat()
            }
        ],
        "title": "Test Meeting",
        "description": "Test Description"
    }

    # 요청 전송 및 검증
    response = client.post("/requests/", json=request_data)
    assert response.status_code == 200
    
    # 이메일 전송 함수가 호출되었는지 확인
    assert email_service.send_meeting_request_email.called
    
    # 응답 데이터 검증
    response_data = response.json()
    assert response_data["sender"]["id"] == mock_user.id
    assert response_data["receiver_email"] == "jane.doe@example.com"
    assert len(response_data["available_times"]) > 0
