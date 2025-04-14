
## Schedulia
schedulia is 

### TODO
25/04/03 서버 배포 완료
CI/CD 손봐야함
비회원 초대 링크에 대한 로직 구현 필요

## 미팅 스케쥴 로직
- 호스트가 미팅 요청 생성
- 미팅 요청 이메일로 전송
- 참석자가 미팅 요청에 대한 응답. 응답을 위해서 회원가입 필요.
- 호스트가 참석자 응답에 반응하여 미팅 확정.
    - 참석자가 모두 응답했을 경우
    - 참석자가 전부 응답하지 않았지만, 시간이 일정기간 지난 경우.


meeting_service
repository

TODO: 예외 처리

view_meeting_schedules(time, user_id)
- meeting_service.get_meeting_by_time(user_id, time)
    - repository.get_meeting(user_id, status = CONFIRMED, time = time)

view_meeting_requests(user_id)
- meeting_requests = meeting_service.get_meeting_requests_by_user_id(user_id)
    - repository.get_meeting_requests(user_id, status = PENDING)

send_meeting_request(user_id)
- meeting_request = meeting_service.create_meeting_request(
    sender_id,
    receiver_emails = List[email],
    title , 
    description,
    available_times = List[Time],
    selected_time = None
)
- repository.save_meeting_request(meeting_request)

respond_to_meeting_request
- meeting_request = meeting_service.get_meeting_request_by_id(request_id)
- validation: [해당 요청이 아직 유효한지, 응답이 '참석'인 경우, 하나 이상의 가능 시간대를 선택했는지]
- repository.update_meeting_request(meeting_request, is_attending, selected_times)

- 미팅 호스트에게 알림 전송
- 응답자에게 알림 전송


confirm_meeting(request_id, selected_time)
- meeting_request = meeting_service.get_meeting_request_by_id(request_id)
- validation: [미팅 요청 대기기간이 지났는지, 모든 참석자가 응답했는지]
- repository.create_meeting_schedule(meeting_request, status = CONFIRMED, selected_time)