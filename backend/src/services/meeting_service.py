from src.db.base import DatabaseInterface
from src.db.db_model import MeetingRequestStatus
from src.models.meeting import MeetingRequest, MeetingSchedule
from src.models.time import Time
from typing import List, Optional

class MeetingService:
    def __init__(self, repository: DatabaseInterface):
        self.repository = repository

    # 각 기능에는 pydantic model <-> db model 변환이 필요

    def get_meeting_requests_by_user_id(self, user_id) -> List[MeetingRequest]:
        requests = self.repository.get_meeting_requests(user_id, status = MeetingRequestStatus.PENDING)

        
    

    def create_meeting_request(self, request):
        pass

    def get_meeting_requests(self, user_id: int) -> List[MeetingRequest]:
        requests = self.repository.get_received_requests(user_id)

        return [
                MeetingRequest(
                    request_id=rm.id,
                    sender=self.repository._convert_user_model(rm.sender),
                    receiver_email=rm.receiver_email,
                    available_times=[self.repository._convert_time_model(t) for t in rm.available_times],
                    status=rm.status,
                    title=rm.title,
                    description=rm.description,
                    selected_time=self.repository._convert_time_model(rm.selected_time) if rm.selected_time else None
                ) for rm in requests
            ]
        
    def confirm_meeting_request(self, 
                              request_id: int, 
                              selected_time: Optional[Time] = None) -> MeetingRequest:

        # find the meeting request
        meeting_request = self.repository.get_meeting_request(request_id)
        if not meeting_request:
            raise ValueError(f"Meeting request with id {request_id} not found")
        
        # check if selected_time is in the available_times
        if selected_time not in meeting_request.available_times:
            raise ValueError(f"Selected time {selected_time} is not in the available times")

        schedule = MeetingSchedule(
            host=meeting_request.sender,
            participants=[meeting_request.receiver],
            time=selected_time,
            title=meeting_request.title,
            description=meeting_request.description,
            status=MeetingRequestStatus.CONFIRMED
        ) # pydantic model

        self.repository.create_schedule(schedule) # pydantic model -> db model
    
        return schedule

