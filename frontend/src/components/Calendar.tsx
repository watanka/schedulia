'use client';

import React from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import koLocale from '@fullcalendar/core/locales/ko';
import { EventClickArg } from '@fullcalendar/core';

interface Meeting {
  id: number;
  title: string;
  description: string;
  date: string;
  attendees: string[];
}

export default function Calendar() {
  const [meetings, setMeetings] = React.useState<Meeting[]>([]);

  React.useEffect(() => {
    // TODO: API 연동
    // 임시 데이터
    setMeetings([
      {
        id: 1,
        title: '팀 주간 회의',
        description: '이번 주 진행 상황 공유',
        date: '2024-04-01T10:00:00',
        attendees: ['user1@example.com', 'user2@example.com']
      },
      {
        id: 2,
        title: '프로젝트 리뷰',
        description: '프로젝트 진행 상황 검토',
        date: '2024-04-02T14:00:00',
        attendees: ['user1@example.com', 'user3@example.com']
      }
    ]);
  }, []);

  const events = meetings.map(meeting => ({
    id: meeting.id.toString(),
    title: meeting.title,
    start: meeting.date,
    extendedProps: {
      description: meeting.description,
      attendees: meeting.attendees
    }
  }));

  const handleEventClick = (arg: EventClickArg) => {
    const event = arg.event;
    alert(`
      ${event.title}
      시간: ${new Date(event.start!).toLocaleString('ko-KR')}
      설명: ${event.extendedProps.description}
      참석자: ${event.extendedProps.attendees.join(', ')}
    `);
  };

  return (
    <div className="h-[600px]">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        locale={koLocale}
        events={events}
        eventClick={handleEventClick}
        height="100%"
      />
    </div>
  );
}
