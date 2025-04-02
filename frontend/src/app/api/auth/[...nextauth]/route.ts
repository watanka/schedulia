import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

// Docker 컨테이너 간 통신에는 컨테이너 이름 사용
const BACKEND_URL = 'http://backend:8000';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  pages: {
    signIn: '/'
  },
  callbacks: {
    async signIn({ user }) {
      try {
        console.log(`백엔드 URL: ${BACKEND_URL}, 요청 URL: ${BACKEND_URL}/users/find?email=${encodeURIComponent(user.email!)}`);
        
        // 사용자가 존재하는지 확인
        let response;
        try {
          response = await fetch(`${BACKEND_URL}/users/find?email=${encodeURIComponent(user.email!)}`);
          console.log('백엔드 응답 상태:', response.status);
        } catch (networkError) {
          console.error('백엔드 연결 실패 (네트워크 에러):', networkError);
          // 연결 실패 시 기본 동작: 로그인은 허용하되 API 키는 저장하지 않음
          return true;
        }
        
        if (response.status === 404) {
          console.log('사용자를 찾을 수 없음 (404) - 회원가입 진행');
          // 신규 사용자: 자동으로 회원가입 처리
          try {
            const createResponse = await fetch(`${BACKEND_URL}/users/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email: user.email,
                name: user.name,
              }),
            });
            
            if (createResponse.ok) {
              const data = await createResponse.json();
              user.apiKey = data.api_key;
              console.log('회원가입 성공, API 키 저장:', data.api_key);
              return true;
            } else {
              console.error('회원가입 실패:', createResponse.status, await createResponse.text());
              return true; // 실패해도 로그인은 허용
            }
          } catch (signupError) {
            console.error('회원가입 과정에서 네트워크 에러:', signupError);
            return true; // 네트워크 에러가 발생해도 로그인은 허용
          }
        }

        if (response.ok) {
          try {
            const data = await response.json();
            user.apiKey = data.api_key;
            console.log('기존 사용자, API 키 저장:', data.api_key);
            return true;
          } catch (parseError) {
            console.error('응답 파싱 에러:', parseError);
            return true; // 파싱 에러가 발생해도 로그인은 허용
          }
        }

        console.log('백엔드 응답이 OK가 아님:', response.status);
        return true; // 기타 에러가 발생해도 로그인은 허용
      } catch (error) {
        console.error('signIn 콜백에서 최상위 에러 발생:', error);
        return true; // 어떤 에러가 발생해도 로그인은 허용
      }
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.apiKey = token.apiKey as string;
      }
      console.log('세션 업데이트 완료:', {
        hasApiKey: !!session.user?.apiKey,
        apiKey: session.user?.apiKey?.substring(0, 8) + '...'
      });
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.apiKey = user.apiKey;
      }
      console.log('JWT 업데이트 완료:', {
        hasApiKey: !!token.apiKey,
        apiKey: token?.apiKey ? token.apiKey.substring(0, 8) + '...' : undefined
      });
      return token;
    }
  }
});

export { handler as GET, handler as POST }; 