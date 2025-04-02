'use client';

import React from 'react';
import { respondToMeetingRequest, MeetingRequest } from '@/lib/api';

interface MeetingRequestResponseProps {
  request: MeetingRequest;
  onResponse?: () => void;
}

export default function MeetingRequestResponse({ request, onResponse }: MeetingRequestResponseProps) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedTime, setSelectedTime] = React.useState<string | null>(null);
  const [localStatus, setLocalStatus] = React.useState<'PENDING' | 'ACCEPTED' | 'DECLINED'>(request.status);
  const [showConfirm, setShowConfirm] = React.useState<{ show: boolean; accept: boolean } | null>(null);

  const handleConfirmDialog = (accept: boolean) => {
    // 먼저 확인 다이얼로그 표시
    setShowConfirm({ show: true, accept });
  };

  const handleResponse = async (accept: boolean) => {
    if (accept && !selectedTime) {
      setError('시간을 선택해주세요.');
      setShowConfirm(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const selectedTimeObj = request.available_times.find(
        time => time.start_time === selectedTime
      );

      await respondToMeetingRequest(request.request_id, {
        accept,
        selected_time: accept ? selectedTimeObj : undefined,
      });

      // 로컬 상태 업데이트
      setLocalStatus(accept ? 'ACCEPTED' : 'DECLINED');
      setShowConfirm(null);
      onResponse?.();
    } catch (err) {
      setError('응답 처리에 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (localStatus !== 'PENDING') {
    return (
      <div className="py-2 px-4 rounded-md bg-gray-100 mt-2">
        <div className={`text-sm font-medium ${localStatus === 'ACCEPTED' ? 'text-green-600' : 'text-red-600'}`}>
          이 회의 요청을 {localStatus === 'ACCEPTED' ? '수락했습니다.' : '거절했습니다.'}
        </div>
        {localStatus === 'ACCEPTED' && selectedTime && (
          <div className="text-xs text-gray-500 mt-1">
            선택한 시간: {new Date(selectedTime).toLocaleString()}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {request.available_times.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            시간 선택
          </label>
          <select
            value={selectedTime || ''}
            onChange={(e) => setSelectedTime(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">시간을 선택하세요</option>
            {request.available_times.map((time, index) => (
              <option key={index} value={time.start_time}>
                {new Date(time.start_time).toLocaleString()} - {new Date(time.end_time).toLocaleString()}
              </option>
            ))}
          </select>
        </div>
      )}

      {error && (
        <div className="text-sm text-red-500">{error}</div>
      )}

      <div className="flex space-x-2">
        <button
          onClick={() => handleConfirmDialog(true)}
          disabled={loading}
          className={`flex-1 rounded-md bg-blue-600 px-4 py-2 text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
            loading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          수락
        </button>
        <button
          onClick={() => handleConfirmDialog(false)}
          disabled={loading}
          className={`flex-1 rounded-md bg-red-600 px-4 py-2 text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 ${
            loading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          거절
        </button>
      </div>

      {/* 확인 팝업 */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {showConfirm.accept ? '회의 요청 수락' : '회의 요청 거절'}
            </h3>
            <p className="text-gray-600 mb-6">
              {request.title} 회의 요청을 {showConfirm.accept ? '수락' : '거절'}하시겠습니까?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowConfirm(null)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                취소
              </button>
              <button
                onClick={() => handleResponse(showConfirm.accept)}
                disabled={loading}
                className={`px-4 py-2 ${
                  showConfirm.accept ? 'bg-blue-600 hover:bg-blue-700' : 'bg-red-600 hover:bg-red-700'
                } text-white rounded ${
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading ? '처리 중...' : showConfirm.accept ? '수락하기' : '거절하기'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 