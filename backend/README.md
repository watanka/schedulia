
[Schedule Server]: 사용자의 스케쥴 정보를 저장해놓는 서버

데이터 스키마

Time
- start_time
- end_time

MeetingSchedule
- host: User
- participants: List[User]
- Time


MeetingRequest
- request_id: int
- sender: User
- receiver: User
- available_times: List[Time]
- status: [PENDING, DECLINED, ACCEPTED]
