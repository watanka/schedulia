import { SessionProvider } from 'next-auth/react';
import type { AppProps } from 'next/app';
import { ApiKeyProvider } from '@/contexts/ApiKeyContext';

export default function App({ Component, pageProps: { session, ...pageProps } }: AppProps) {
  return (
    <SessionProvider session={session}>
      <ApiKeyProvider>
        <Component {...pageProps} />
      </ApiKeyProvider>
    </SessionProvider>
  );
} 