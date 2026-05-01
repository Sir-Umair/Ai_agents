'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [cachedUrl, setCachedUrl] = useState('');

  // Pre-fetch the auth URL so the redirect is instant when clicked
  useEffect(() => {
    const prefetch = async () => {
      try {
        const data = await api.login();
        if (data.auth_url) setCachedUrl(data.auth_url);
      } catch (err) {
        console.warn('Url prefetch failed', err);
      }
    };
    prefetch();
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    
    // Redirect instantly if url is cached
    if (cachedUrl) {
      window.location.href = cachedUrl;
      return;
    }

    try {
      const data = await api.login();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        throw new Error('Could not get authorization URL');
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please refresh the page.');
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
    }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%', textAlign: 'center', padding: '2.5rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: 'var(--primary)' }}>U-Marketer</h1>
        <p style={{ color: 'var(--muted-foreground)', marginBottom: '2rem' }}>
          Connect your Gmail to start sending professional AI-powered email campaigns.
        </p>

        {error && (
          <div style={{ 
            padding: '0.75rem', 
            background: '#fee2e2', 
            color: '#991b1b', 
            borderRadius: '6px', 
            marginBottom: '1.5rem',
            fontSize: '0.875rem' 
          }}>
            {error}
          </div>
        )}

        <button 
          className="btn" 
          onClick={handleLogin} 
          disabled={loading}
          style={{ 
            width: '100%', 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            gap: '0.75rem', 
            height: '48px' 
          }}
        >
          {loading ? (
            <div style={{ 
              width: '20px', 
              height: '20px', 
              border: '2px solid rgba(255,255,255,0.3)', 
              borderTopColor: '#fff', 
              borderRadius: '50%',
              animation: 'spin 0.6s linear infinite'
            }}></div>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </>
          )}
        </button>

        <p style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>
          By continuing, you authorize U-Marketer to send emails on your behalf.
        </p>
      </div>
    </div>
  );
}
