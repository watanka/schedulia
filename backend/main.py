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


# CORS 설정을 환경에 따라 다르게 적용
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = {
    "development": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    "production": [
        "https://schedulia.org",
        "https://api.schedulia.org",
        "https://mcp.schedulia.org"
    ]
}

app = FastAPI(
    title="Meeting Scheduler API",
    root_path="",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://schedulia.org", "http://schedulia.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseFactory.create_database(DB_CONFIG)

JWT_SECRET = os.getenv('NEXTAUTH_SECRET', '')


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


class CreateMeetingRequest(BaseModel):
    receiver_email: str
    available_times: List[Time]
    title: str
    description: str | None = None

class RespondToMeetingRequest(BaseModel):
    accept: bool
    selected_time: Time | None = None


@app.get("/users/find", response_model=UserResponse)
async def find_user(email: str):
    print(f"Finding user with email: {email}")
    user = db.get_user_by_email(email)
    if not user:
        print(f"User not found with email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    

    api_key = db.get_active_api_key(user.id)
    print(f"Found user: {user}, API key: {api_key}")
    
    if not api_key:
        api_key = db.create_api_key(user.id)
        print(f"Created new API key: {api_key}")
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        api_key=api_key.key if api_key else None
    )

@app.post("/users/", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):

    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        api_key = db.get_active_api_key(existing_user.id)
        if not api_key:
            api_key = db.create_api_key(existing_user.id)
        return CreateUserResponse(
            id=existing_user.id,
            name=existing_user.name,
            email=existing_user.email,
            api_key=api_key.key
        )

    user = db.create_user(name=request.name, email=request.email)
    api_key = db.create_api_key(user.id)
    
    return CreateUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        api_key=api_key.key
    )

async def get_current_user(x_api_key: Annotated[str | None, Header()] = None) -> User:
    print(f"API key in request header: {x_api_key}")
    
    if not x_api_key:
        print("API key is not provided - 401 Unauthorized response")
        raise HTTPException(
            status_code=401,
            detail={"error": "Authentication failed", "reason": "API key is not provided"}
        )

    user = db.get_user_by_api_key(x_api_key)
    if user:
        print(f"Found user with API key: {user.email}")
        return user
    
    print(f"User not found with API key: {x_api_key} - 401 Unauthorized response")
    raise HTTPException(
        status_code=401,
        detail={"error": "Authentication failed", "reason": "Invalid API key"}
    )




@app.post("/users/{user_id}/api-keys", response_model=APIKey)
async def create_api_key(user_id: int):
    try:
        return db.create_api_key(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api-keys/{api_key}")
async def deactivate_api_key(api_key: str):
    if not db.deactivate_api_key(api_key):
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key deactivated"}

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
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
        print(f"Viewing meeting requests for user: {current_user.email}")
        requests = db.get_user_received_requests(current_user.email)
        print(f"Found {len(requests)} meeting requests")
        return requests
    except Exception as e:
        print(f"Error occurred while viewing meeting requests: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Server error", "reason": str(e)}
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

    created_request = db.create_request(meeting_request)
    
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
    
    if meeting_request.receiver_email != current_user.email:
        raise HTTPException(status_code=403, detail="You do not have permission to respond to this meeting request")
    
    if meeting_request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    if response.accept:
        if response.selected_time is None:
            raise HTTPException(
                status_code=400,
                detail="You must select a time"
            )
        
        if response.selected_time not in meeting_request.available_times:
            raise HTTPException(
                status_code=400,
                detail="The selected time is not valid. The detailed adjustment feature is not implemented yet."
            )
        
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

@app.post("/meetings/{meeting_id}/confirm", response_model = MeetingSchedule)
async def confirm_meeting(meeting_id: int, current_user: User = Depends(get_current_user)):

    # 현재 사용자가 호스트인지 확인
    # 참석자들이 전부 응답했는지 확인
    


@app.get("/health-check")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 모든 IP에서 접근 가능하도록 설정
        port=8000,
        reload=True  # 개발 중 코드 변경 시 자동 재시작
    ) 

