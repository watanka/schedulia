import 'next-auth';
import { DefaultSession } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id?: string;
      apiKey?: string;
    } & DefaultSession['user']
  }

  interface User {
    id?: string;
    apiKey?: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    apiKey?: string;
  }
} 