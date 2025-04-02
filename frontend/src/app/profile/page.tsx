'use client';

import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import Calendar from '@/components/Calendar';

export default function ProfilePage() {
  const { data: session } = useSession();
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);

  const generateApiKey = async () => {
    try {
      // TODO: API 연동
      // const response = await fetch('/api/generate-api-key', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      // });
      // const data = await response.json();
      // setApiKey(data.apiKey);
      
      // 임시로 랜덤 키 생성
      const tempKey = 'mk_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
      setApiKey(tempKey);
      setShowApiKey(true);
    } catch (error) {
      console.error('Error generating API key:', error);
    }
  };

  const copyApiKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      alert('API 키가 클립보드에 복사되었습니다.');
    }
  };

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-600">로그인이 필요합니다.</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-gray-800">내 프로필</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">기본 정보</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">이름</label>
                  <p className="mt-1 text-lg">{session.user?.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">이메일</label>
                  <p className="mt-1 text-lg">{session.user?.email}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">API 키 관리</h2>
              <div className="space-y-4">
                {apiKey ? (
                  <>
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">현재 API 키</label>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 p-2 bg-gray-100 rounded font-mono text-sm break-all">
                          {showApiKey ? apiKey : '••••••••••••••••'}
                        </code>
                        <button
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="p-2 text-gray-600 hover:text-gray-900"
                        >
                          {showApiKey ? '숨기기' : '보기'}
                        </button>
                        <button
                          onClick={copyApiKey}
                          className="p-2 text-blue-600 hover:text-blue-800"
                        >
                          복사
                        </button>
                      </div>
                    </div>
                    <button
                      onClick={generateApiKey}
                      className="w-full px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                    >
                      API 키 재발급
                    </button>
                  </>
                ) : (
                  <button
                    onClick={generateApiKey}
                    className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    API 키 발급
                  </button>
                )}
                <p className="text-sm text-gray-500 mt-2">
                  API 키는 외부 서비스와의 연동에 사용됩니다. 키를 안전하게 보관하세요.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">내 일정</h2>
            <Calendar />
          </div>
        </div>
      </div>
    </main>
  );
} 