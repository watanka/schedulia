import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSession } from 'next-auth/react';
import { createApiKey, getCurrentUser } from '@/lib/api';

interface ApiKeyContextType {
  apiKey: string | null;
  setApiKey: (key: string | null) => void;
}

const ApiKeyContext = createContext<ApiKeyContextType | undefined>(undefined);

export function ApiKeyProvider({ children }: { children: ReactNode }) {
  const { data: session } = useSession();
  const [apiKey, setApiKey] = useState<string | null>(null);

  useEffect(() => {
    // 세션 스토리지에서 API 키 복구
    const storedKey = sessionStorage.getItem('apiKey');
    if (storedKey) {
      setApiKey(storedKey);
    }
  }, []);

  useEffect(() => {
    const initializeApiKey = async () => {
      if (session?.user && !apiKey) {
        try {
          // 현재 사용자 정보 가져오기
          const user = await getCurrentUser();
          // API 키 발급
          const response = await createApiKey(user.id);
          const newApiKey = response.key;
          setApiKey(newApiKey);
          sessionStorage.setItem('apiKey', newApiKey);
        } catch (error) {
          console.error('API 키 초기화 실패:', error);
        }
      } else if (!session?.user && apiKey) {
        // 로그아웃 시 API 키 제거
        setApiKey(null);
        sessionStorage.removeItem('apiKey');
      }
    };

    initializeApiKey();
  }, [session, apiKey]);

  return (
    <ApiKeyContext.Provider value={{ apiKey, setApiKey }}>
      {children}
    </ApiKeyContext.Provider>
  );
}

export function useApiKey() {
  const context = useContext(ApiKeyContext);
  if (context === undefined) {
    throw new Error('useApiKey must be used within an ApiKeyProvider');
  }
  return context;
} 