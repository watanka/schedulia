'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import { getMeetingRequests, MeetingRequest } from '@/lib/api';
import MeetingRequestResponse from './MeetingRequestResponse';

export default function MeetingList() {
  const { data: session } = useSession();
  const [meetings, setMeetings] = useState<MeetingRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMeetings = useCallback(async () => {
    if (!session) return;
    
    try {
      const data = await getMeetingRequests();
      setMeetings(data);
    } catch (err) {
      setError('회의 요청을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [session]);

  useEffect(() => {
    fetchMeetings();
  }, [fetchMeetings]);

  if (!session) {
    return <div className="text-center p-4">로그인이 필요합니다.</div>;
  }

  if (loading) {
    return <div className="text-center p-4">로딩 중...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500 p-4">{error}</div>;
  }

  if (meetings.length === 0) {
    return <div className="text-center p-4">예정된 회의가 없습니다.</div>;
  }

  return (
    <div className="space-y-4">
      {meetings.map((meeting) => (
        <div
          key={meeting.request_id}
          className="border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="text-lg font-semibold">{meeting.title}</h3>
          {meeting.description && (
            <p className="text-gray-600 mt-1">{meeting.description}</p>
          )}
          <div className="mt-2 text-sm text-gray-500">
            <p>보낸 사람: {meeting.sender.email}</p>
            <p>받는 사람: {meeting.receiver_email}</p>
            <p>상태: {
              meeting.status === 'PENDING' ? '대기 중' :
              meeting.status === 'ACCEPTED' ? '수락됨' :
              'DECLINED'
            }</p>
            {meeting.selected_time && (
              <p>
                선택된 시간: {new Date(meeting.selected_time.start_time).toLocaleString()} - {new Date(meeting.selected_time.end_time).toLocaleString()}
              </p>
            )}
          </div>
          <div className="mt-2">
            <h4 className="font-medium">가능한 시간:</h4>
            <ul className="list-disc list-inside">
              {meeting.available_times.map((time, index) => (
                <li key={index}>
                  {new Date(time.start_time).toLocaleString()} - {new Date(time.end_time).toLocaleString()}
                </li>
              ))}
            </ul>
          </div>
          {meeting.receiver_email === session.user?.email && (
            <div className="mt-4">
              <MeetingRequestResponse
                request={meeting}
                onResponse={fetchMeetings}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
} 