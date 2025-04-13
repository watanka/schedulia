from src.db.base import DatabaseInterface
from src.db.db_model import MeetingStatus
from src.models.meeting import MeetingRequest, MeetingSchedule
from src.models.time import Time
from typing import List, Optional

class MeetingService:
    def __init__(self, db: DatabaseInterface):
        self.db = db


    

    def create_meeting_request(self, request):
        pass

    def get_meeting_requests_by_email(self, user_email: str) -> List[MeetingRequest]:
        requests = self.db.get_user_received_requests(user_email)

        return [
                MeetingRequest(
                    request_id=rm.id,
                    sender=self.db._convert_user_model(rm.sender),
                    receiver_email=rm.receiver_email,
                    available_times=[self.db._convert_time_model(t) for t in rm.available_times],
                    status=rm.status,
                    title=rm.title,
                    description=rm.description,
                    selected_time=self.db._convert_time_model(rm.selected_time) if rm.selected_time else None
                ) for rm in requests
            ]
        
    def confirm_meeting_request(self, 
                              request_id: int, 
                              selected_time: Optional[Time] = None) -> MeetingRequest:

        # find the meeting request
        meeting_request = self.db.get_meeting_request(request_id)
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
            status=MeetingStatus.CONFIRMED
        ) # pydantic model

        self.db.create_schedule(schedule) # pydantic model -> db model
    
        return schedule

