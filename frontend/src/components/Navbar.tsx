'use client';

import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';

export default function Navbar() {
  const { data: session } = useSession();

  if (!session) {
    return null;  // 로그인하지 않은 경우 네비게이션 바를 표시하지 않음
  }

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/dashboard" className="flex items-center">
              <span className="text-xl font-bold">회의 스케줄러</span>
            </Link>
          </div>

          <div className="flex items-center">
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">{session.user?.name}</span>
              <Link
                href="/profile"
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                내 프로필
              </Link>
              <button
                onClick={() => signOut({ callbackUrl: '/' })}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
} 