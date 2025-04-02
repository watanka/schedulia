'use server';

import { revalidatePath } from 'next/cache';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

// 타입 정의
export interface Time {
  start_time: string;
  end_time: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
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

// 스케줄 인터페이스 추가
export interface Schedule {
  id: number;
  title: string;
  description?: string;
  host: User;
  participants: User[];
  time: Time;
}

// 백엔드 URL (내부 Docker 네트워크)
const BACKEND_URL = 'http://backend:8000';

// 인증 헤더 추가 함수
async function getAuthHeaders() {
  // 세션 가져오기 (NextAuth 설정을 전달)
  const session = await getServerSession(authOptions);
  
  console.log('[ServerAction] 세션 정보:', {
    exists: !!session,
    user: session?.user?.email,
    hasApiKey: !!session?.user?.apiKey
  });
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  if (session?.user?.apiKey) {
    headers['x-api-key'] = session.user.apiKey;
    console.log('[ServerAction] API 키를 사용하여 인증 헤더 추가:', `${session.user.apiKey.substring(0, 8)}...`);
  } else {
    console.log('[ServerAction] 세션에 API 키가 없음, 인증되지 않은 요청이 될 수 있음');
  }

  return headers;
}

// 회의 요청 목록 조회
export async function getMeetingRequests(): Promise<MeetingRequest[]> {
  try {
    console.log('[ServerAction] 회의 요청 목록 조회 시작');
    const headers = await getAuthHeaders();
    const response = await fetch(`${BACKEND_URL}/requests/`, { 
      headers,
      cache: 'no-store'
    });

    if (!response.ok) {
      console.error(`[ServerAction] 회의 요청 조회 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`회의 요청 조회 실패: ${response.status}`);
    }

    const data = await response.json();
    console.log(`[ServerAction] 회의 요청 ${data.length}개 조회 성공`);
    return data;
  } catch (error) {
    console.error('[ServerAction] 회의 요청 조회 중 오류 발생:', error);
    throw error;
  }
}

// 회의 요청 생성
export async function createMeetingRequest(data: {
  receiver_email: string;
  available_times: Time[];
  title: string;
  description?: string;
}): Promise<MeetingRequest> {
  try {
    console.log('[ServerAction] 회의 요청 생성 시작:', data.title);
    const headers = await getAuthHeaders();
    const response = await fetch(`${BACKEND_URL}/requests/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      console.error(`[ServerAction] 회의 요청 생성 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`회의 요청 생성 실패: ${response.status}`);
    }

    const result = await response.json();
    console.log('[ServerAction] 회의 요청 생성 성공:', result.request_id);

    // 캐시 무효화로 최신 데이터 보장
    revalidatePath('/dashboard');
    return result;
  } catch (error) {
    console.error('[ServerAction] 회의 요청 생성 중 오류 발생:', error);
    throw error;
  }
}

// 회의 요청 응답 (수락/거절)
export async function respondToMeetingRequest(
  requestId: number,
  data: {
    accept: boolean;
    selected_time?: Time;
  }
): Promise<MeetingRequest> {
  try {
    console.log(`[ServerAction] 회의 요청 #${requestId}에 대한 응답 처리: ${data.accept ? '수락' : '거절'}`);
    const headers = await getAuthHeaders();
    const response = await fetch(`${BACKEND_URL}/requests/${requestId}/respond`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      console.error(`[ServerAction] 회의 요청 응답 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`회의 요청 응답 실패: ${response.status}`);
    }

    const result = await response.json();
    console.log(`[ServerAction] 회의 요청 #${requestId} 응답 처리 성공`);

    // 캐시 무효화로 최신 데이터 보장
    revalidatePath('/dashboard');
    return result;
  } catch (error) {
    console.error('[ServerAction] 회의 요청 응답 중 오류 발생:', error);
    throw error;
  }
}

// 스케줄 조회
export async function getSchedules(date?: string): Promise<Schedule[]> {
  try {
    console.log(`[ServerAction] 스케줄 조회 시작${date ? ': ' + date : ''}`);
    const headers = await getAuthHeaders();
    const url = date ? `${BACKEND_URL}/schedules/?date=${date}` : `${BACKEND_URL}/schedules/`;
    
    const response = await fetch(url, {
      headers,
      cache: 'no-store'
    });

    if (!response.ok) {
      console.error(`[ServerAction] 스케줄 조회 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`스케줄 조회 실패: ${response.status}`);
    }

    const data = await response.json();
    console.log(`[ServerAction] 스케줄 ${data.length}개 조회 성공`);
    
    // 백엔드 응답 구조를 Schedule 인터페이스에 맞게 변환
    return data.map((item: { 
      id: number; 
      title: string; 
      description: string | null; 
      host: User;
      participants: User[];
      time: Time;
    }) => ({
      id: item.id,
      title: item.title,
      description: item.description,
      host: item.host,
      participants: item.participants,
      time: item.time
    }));
  } catch (error) {
    console.error('[ServerAction] 스케줄 조회 중 오류 발생:', error);
    throw error;
  }
}

// 현재 사용자 정보 조회
export async function getCurrentUser(): Promise<User> {
  try {
    console.log('[ServerAction] 현재 사용자 정보 조회 시작');
    const headers = await getAuthHeaders();
    const response = await fetch(`${BACKEND_URL}/users/me`, {
      headers,
      cache: 'no-store'
    });

    if (!response.ok) {
      console.error(`[ServerAction] 사용자 정보 조회 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`사용자 정보 조회 실패: ${response.status}`);
    }

    const data = await response.json();
    console.log('[ServerAction] 사용자 정보 조회 성공:', data.email);
    return data;
  } catch (error) {
    console.error('[ServerAction] 사용자 정보 조회 중 오류 발생:', error);
    throw error;
  }
}

// API 키 생성
export async function createApiKey(userId: number): Promise<{ key: string }> {
  try {
    console.log(`[ServerAction] API 키 생성 시작: 사용자 ID = ${userId}`);
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${BACKEND_URL}/users/${userId}/api-keys`, {
      method: 'POST',
      headers,
      cache: 'no-store'
    });

    if (!response.ok) {
      console.error(`[ServerAction] API 키 생성 실패: 상태 코드 ${response.status}`);
      const errorText = await response.text();
      console.error('[ServerAction] 에러 응답:', errorText);
      throw new Error(`API 키 생성 실패: ${response.status}`);
    }

    const data = await response.json();
    console.log('[ServerAction] API 키 생성 성공');
    return { key: data.key };
  } catch (error) {
    console.error('[ServerAction] API 키 생성 중 오류 발생:', error);
    throw error;
  }
}