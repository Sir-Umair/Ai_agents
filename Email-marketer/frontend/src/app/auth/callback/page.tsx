'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    const email = searchParams.get('email');

    if (token) {
      localStorage.setItem('auth_token', token);
      if (email) localStorage.setItem('user_email', email);
      router.push('/');
    } else {
      router.push('/login?error=auth_failed');
    }
  }, [router, searchParams]);

  return (
    <div style={{ textAlign: 'center' }}>
      <h2>Authenticating...</h2>
      <p>Please wait while we complete the secure login process.</p>
      <div className="spinner"></div>
    </div>
  );
}

export default function AuthCallback() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Suspense fallback={
        <div style={{ textAlign: 'center' }}>
          <h2>Loading...</h2>
        </div>
      }>
        <AuthCallbackContent />
      </Suspense>
    </div>
  );
}
