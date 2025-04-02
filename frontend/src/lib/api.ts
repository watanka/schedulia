import axios from 'axios';

export interface Time {
  start_time: string;
  end_time: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface MeetingSchedule {
  id: number;
  host: User;
  participants: User[];
  time: Time;
  title: string;
  description: string | null;
}

export interface MeetingRequest {
  request_id: number;
  sender: User;
  receiver_email: string;
  available_times: Time[];
  title: string;
  description: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED';
  selected_time?: Time;
}

// 항상 내부 Docker 네트워크 주소 사용 (서버 사이드 렌더링용)
const API_BASE_URL = 'http://backend:8000';

// 서버 사이드에서만 사용할 API 클라이언트
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 로깅 기능 추가
console.log('서버 전용 API 클라이언트 초기화: URL =', API_BASE_URL);

// 이 API 클라이언트는 서버 사이드 actions에서만 사용해야 함
export default api; 