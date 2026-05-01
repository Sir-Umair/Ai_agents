'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function AuthCheck({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const isAuthPage = pathname === '/login' || pathname === '/auth/callback' || pathname?.startsWith('/auth/callback?');

    if (!token && !isAuthPage) {
      router.push('/login');
    } else if (token && isAuthPage) {
      router.push('/');
    } else {
      setIsReady(true);
    }
  }, [pathname, router]);

  // If we are on login or callback, show children immediately to avoid ficker
  const isAuthPage = pathname === '/login' || pathname === '/auth/callback' || pathname?.startsWith('/auth/callback?');
  if (isAuthPage) return <>{children}</>;

  if (!isReady) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'var(--background)'
      }}>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          border: '3px solid var(--border)', 
          borderTopColor: 'var(--primary)', 
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '1rem'
        }}></div>
        <p style={{ fontSize: '0.875rem', fontWeight: 500 }}>Initializing U-Marketer...</p>
        <style dangerouslySetInnerHTML={{ __html: `
          @keyframes spin { to { transform: rotate(360deg); } }
        `}} />
      </div>
    );
  }

  return <>{children}</>;
}
