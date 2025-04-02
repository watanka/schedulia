from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from datetime import datetime
from src.models import MeetingRequest, Time
import os

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME = os.getenv("GMAIL_USERNAME", "noreply@schedulia.org"),  # Gmail 주소
            MAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "kprjxjpojwnjdehr"),  # Gmail 앱 비밀번호
            MAIL_FROM = os.getenv("GMAIL_USERNAME", "noreply@schedulia.org"),  # Gmail 주소와 동일하게
            MAIL_PORT = 587,
            MAIL_SERVER = "smtp.gmail.com",
            MAIL_FROM_NAME = "Schedulia",
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True
        )
        self.fastmail = FastMail(self.conf)

    def _format_time(self, time: Time) -> str:
        return f"{time.start_time.strftime('%Y-%m-%d %H:%M')} - {time.end_time.strftime('%H:%M')}"

    def _format_available_times(self, times: List[Time]) -> str:
        return "\n".join([f"- {self._format_time(time)}" for time in times])

    async def send_meeting_request_email(self, meeting_request: MeetingRequest, background_tasks: BackgroundTasks):
        # 이메일 본문 생성
         # TODO: 실제 회원가입 URL로 변경 필요
        body = f"""
Hi!

{meeting_request.sender.name} has requested a meeting.

Title: {meeting_request.title}
{f'Description: {meeting_request.description}' if meeting_request.description else ''}

Suggested time:
{self._format_available_times(meeting_request.available_times)}

To respond to the meeting request, please sign up through the following link:
http://schedulia.org/signup 

Thank you.
Schedulia Team
"""

        message = MessageSchema(
            subject=f"[Schedulia]<Meeting Request> {meeting_request.title}",
            recipients=[meeting_request.receiver_email],
            body=body,
            subtype="plain"
        )

        # 백그라운드에서 이메일 전송
        background_tasks.add_task(
            self.fastmail.send_message,
            message
        )

email_service = EmailService() 