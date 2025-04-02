'use client';

import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import koLocale from '@fullcalendar/core/locales/ko';
import { EventClickArg } from '@fullcalendar/core';
import { getSchedules, Schedule } from '@/actions/meetings';

export default function Calendar() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSchedules() {
      try {
        setLoading(true);
        setError(null);
        const data = await getSchedules();
        setSchedules(data);
      } catch (err) {
        console.error('일정 불러오기 실패:', err);
        setError('일정을 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    }

    fetchSchedules();
  }, []);

  const events = schedules.map(schedule => ({
    id: schedule.id.toString(),
    title: schedule.title,
    start: schedule.time.start_time,
    end: schedule.time.end_time,
    extendedProps: {
      description: schedule.description || '',
      host: schedule.host.name,
      hostEmail: schedule.host.email,
      participants: schedule.participants?.map(p => p.email) || []
    }
  }));

  const handleEventClick = (arg: EventClickArg) => {
    const event = arg.event;
    const props = event.extendedProps;
    
    alert(`
      ${event.title}
      시간: ${new Date(event.start!).toLocaleString('ko-KR')} ~ ${new Date(event.end!).toLocaleString('ko-KR')}
      설명: ${props.description}
      주최자: ${props.host} (${props.hostEmail})
      참석자: ${props.participants.join(', ')}
    `);
  };

  if (loading) {
    return <div className="h-[600px] flex items-center justify-center">로딩 중...</div>;
  }

  if (error) {
    return <div className="h-[600px] flex items-center justify-center text-red-500">{error}</div>;
  }

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
