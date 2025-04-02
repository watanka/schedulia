import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSession } from 'next-auth/react';
import { createApiKey, getCurrentUser, type User } from '@/actions/meetings';

interface ApiKeyContextType {
  apiKey: string | null;
  isLoadingKey: boolean;
  setApiKey: (key: string | null) => void;
}

const ApiKeyContext = createContext<ApiKeyContextType | undefined>(undefined);

export function ApiKeyProvider({ children }: { children: ReactNode }) {
  const { data: session, status } = useSession();
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [isLoadingKey, setIsLoadingKey] = useState(false);

  useEffect(() => {
    // 세션 스토리지에서 API 키 복구
    const storedKey = sessionStorage.getItem('apiKey');
    if (storedKey) {
      setApiKey(storedKey);
    }
  }, []);

  useEffect(() => {
    const initializeApiKey = async () => {
      if (session?.user && !apiKey && status === 'authenticated') {
        try {
          setIsLoadingKey(true);
          
          // 현재 사용자 정보 가져오기 (서버 액션 사용)
          const user: User = await getCurrentUser();
          console.log('사용자 정보 가져옴:', user.email);
          
          if (user.id) {
            // API 키 발급 (서버 액션 사용)
            const response = await createApiKey(user.id);
            console.log('API 키 생성 응답:', response);
            
            if (response && response.key) {
              const newApiKey = response.key;
              console.log('새 API 키 설정:', newApiKey.substring(0, 8) + '...');
              setApiKey(newApiKey);
              sessionStorage.setItem('apiKey', newApiKey);
            } else {
              console.error('API 키가 응답에 없음');
            }
          } else {
            console.error('사용자 ID가 없음');
          }
        } catch (error) {
          console.error('API 키 초기화 실패:', error);
        } finally {
          setIsLoadingKey(false);
        }
      } else if (!session?.user && apiKey) {
        // 로그아웃 시 API 키 제거
        console.log('로그아웃으로 API 키 제거');
        setApiKey(null);
        sessionStorage.removeItem('apiKey');
      }
    };

    initializeApiKey();
  }, [session, status, apiKey]);

  return (
    <ApiKeyContext.Provider value={{ apiKey, isLoadingKey, setApiKey }}>
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