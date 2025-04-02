'use client';

import { signOut } from 'next-auth/react';

export default function LogoutButton() {
  const handleLogout = async () => {
    // 로그아웃 시 쿠키 제거를 위해 callbackUrl 지정
    await signOut({ 
      callbackUrl: '/',
      redirect: true 
    });
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
    >
      로그아웃
    </button>
  );
} 