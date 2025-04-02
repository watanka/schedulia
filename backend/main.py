import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Cookie, Response
from typing import List, Optional, Annotated
from datetime import datetime, date
import jwt


from pydantic import BaseModel
import uvicorn
from fastapi import Header, Depends
from fastapi.middleware.cors import CORSMiddleware


from src.models import User, Time, MeetingSchedule, MeetingRequest, RequestStatus, APIKey
from src.email_service import email_service
from src.db.factory import DatabaseFactory
from config import DB_CONFIG


app = FastAPI(title="Meeting Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://frontend:3000"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseFactory.create_database(DB_CONFIG)

JWT_SECRET = os.getenv('NEXTAUTH_SECRET', '')

# Request/Response 모델
class CreateUserRequest(BaseModel):
    name: str
    email: str

class CreateUserResponse(BaseModel):
    id: int
    name: str
    email: str
    api_key: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    api_key: Optional[str] = None

# 사용자 조회
@app.get("/users/find", response_model=UserResponse)
async def find_user(email: str):
    print(f"Finding user with email: {email}")
    user = db.get_user_by_email(email)
    if not user:
        print(f"User not found with email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # API 키 조회
    api_key = db.get_active_api_key(user.id)
    print(f"Found user: {user}, API key: {api_key}")
    
    if not api_key:
        # API 키가 없으면 새로 발급
        api_key = db.create_api_key(user.id)
        print(f"Created new API key: {api_key}")
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        api_key=api_key.key if api_key else None
    )

# 사용자 생성 및 API 키 발급
@app.post("/users/", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):
    # 1. 기존 사용자 확인
    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        # 기존 사용자의 API 키 확인
        api_key = db.get_active_api_key(existing_user.id)
        if not api_key:
            # API 키가 없으면 새로 발급
            api_key = db.create_api_key(existing_user.id)
            print('새로운 api key 발급')
        return CreateUserResponse(
            id=existing_user.id,
            name=existing_user.name,
            email=existing_user.email,
            api_key=api_key.key
        )

    # 2. 새 사용자 생성
    user = db.create_user(name=request.name, email=request.email)
    # 3. API 키 발급
    api_key = db.create_api_key(user.id)
    
    return CreateUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        api_key=api_key.key
    )

# 인증 미들웨어
async def get_current_user(x_api_key: Annotated[str | None, Header()] = None) -> User:
    print(f"요청 헤더의 API 키: {x_api_key}")
    
    if not x_api_key:
        print("API 키가 제공되지 않음 - 401 Unauthorized 응답")
        raise HTTPException(
            status_code=401,
            detail={"error": "인증 실패", "reason": "API 키가 제공되지 않음"}
        )
    
    # API 키로 시도
    user = db.get_user_by_api_key(x_api_key)
    if user:
        print(f"API 키로 사용자 찾음: {user.email}")
        return user
    
    print(f"API 키에 해당하는 사용자를 찾을 수 없음: {x_api_key} - 401 Unauthorized 응답")
    raise HTTPException(
        status_code=401,
        detail={"error": "인증 실패", "reason": "잘못된 API 키"}
    )

# Request/Response 모델
class CreateMeetingRequest(BaseModel):
    receiver_email: str
    available_times: List[Time]
    title: str
    description: str | None = None

class RespondToMeetingRequest(BaseModel):
    accept: bool
    selected_time: Time | None = None  # accept=True인 경우 필수

# 엔드포인트 구현

# API 키 관련 엔드포인트
@app.post("/users/{user_id}/api-keys", response_model=APIKey)
async def create_api_key(user_id: int):
    try:
        return db.create_api_key(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api-keys/{api_key}")
async def deactivate_api_key(api_key: str):
    if not db.deactivate_api_key(api_key):
        raise HTTPException(status_code=404, detail="API 키를 찾을 수 없습니다")
    return {"message": "API 키가 비활성화되었습니다"}

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    # API 키 조회
    api_key = db.get_active_api_key(current_user.id)
    
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        api_key=api_key.key if api_key else None
    )

@app.get("/schedules/", response_model=List[MeetingSchedule])
async def view_meeting_schedules(
    date: date | None = None,
    current_user: User = Depends(get_current_user)
):
    schedules = db.get_user_schedules(current_user.id)
    if date:
        schedules = [
            schedule for schedule in schedules
            if schedule.time.start_time.date() == date
        ]
    return schedules

@app.get("/requests/", response_model=List[MeetingRequest])
async def view_meeting_requests(current_user: User = Depends(get_current_user)):
    try:
        print(f"회의 요청 조회 시작: 사용자 = {current_user.email}")
        requests = db.get_user_received_requests(current_user.email)
        print(f"조회된 회의 요청 수: {len(requests)}")
        return requests
    except Exception as e:
        print(f"회의 요청 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "서버 오류", "reason": str(e)}
        )

@app.post("/requests/", response_model=MeetingRequest)
async def send_meeting_request(
    request: CreateMeetingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    meeting_request = MeetingRequest(
        request_id=0,  # will be set by database
        sender=current_user,
        receiver_email=request.receiver_email,
        available_times=request.available_times,
        title=request.title,
        description=request.description
    )

    # 데이터베이스에 미팅 요청 저장
    created_request = db.create_request(meeting_request)
    
    # 백그라운드에서 이메일 발송
    await email_service.send_meeting_request_email(created_request, background_tasks)
    
    return created_request

@app.post("/requests/{request_id}/respond", response_model=MeetingRequest)
async def respond_to_meeting_request(
    request_id: int,
    response: RespondToMeetingRequest,
    current_user: User = Depends(get_current_user)
):
    meeting_request: MeetingRequest = db.get_request(request_id)
    if not meeting_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 요청 수신자만 응답할 수 있음
    if meeting_request.receiver_email != current_user.email:
        raise HTTPException(status_code=403, detail="이 미팅 요청에 대한 응답 권한이 없습니다")
    
    if meeting_request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    if response.accept:
        if response.selected_time is None:
            raise HTTPException(
                status_code=400,
                detail="시간을 선택해야합니다"
            )
        
        # 선택된 시간이 유효한지 확인
        if response.selected_time not in meeting_request.available_times:
            raise HTTPException(
                status_code=400,
                detail="미팅 요청에 유효한 시간이 아닙니다. 세부조정 기능은 아직 구현되지 않았습니다."
            )
        
        # 미팅 요청 수락 및 스케줄 생성
        meeting_request.status = RequestStatus.ACCEPTED
        meeting_request.selected_time = response.selected_time

        schedule = MeetingSchedule(
            id=0,  # will be set by database
            host=meeting_request.sender,
            participants=[meeting_request.sender, current_user],
            time=meeting_request.selected_time,
            title=meeting_request.title,
            description=meeting_request.description
        )
        db.create_schedule(schedule)
    else:
        meeting_request.status = RequestStatus.DECLINED
    
    return meeting_request

@app.get("/health-check")
async def health_check():
    """시스템 상태 확인용 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 모든 인터페이스에서 요청 수신
        port=8000,
    ) 

