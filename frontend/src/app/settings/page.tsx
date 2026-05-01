'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const [personalDetails, setPersonalDetails] = useState({
    fullName: 'Sir Umair',
    email: 'umair@u-marketer.ai'
  });
  const [policies, setPolicies] = useState({
    auto_reply_enabled: true,
    duplicate_prevention_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingPolicy, setSavingPolicy] = useState(false);
  const [toast, setToast] = useState<{ message: string, type: 'success' | 'error' } | null>(null);

  function showToast(message: string, type: 'success' | 'error' = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  }

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await api.getSettings();
        setPersonalDetails({
          fullName: data.full_name || 'Sir Umair',
          email: data.email_user || 'umair@u-marketer.ai'
        });
        setPolicies({
          auto_reply_enabled: data.auto_reply_enabled ?? true,
          duplicate_prevention_enabled: data.duplicate_prevention_enabled ?? true
        });
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleSaveProfile = async () => {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!personalDetails.email || !emailRegex.test(personalDetails.email)) {
      showToast('Please enter a valid email address.', 'error');
      return;
    }

    try {
      setSaving(true);
      await api.updateSettings(personalDetails);
      showToast('Profile saved successfully!');
    } catch (err) {
      showToast('Failed to save profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleApplyStrategy = async () => {
    try {
      setSavingPolicy(true);
      await api.updateSettings(policies);
      showToast('Marketing policies applied successfully!');
    } catch (err) {
      showToast('Failed to apply marketing policies', 'error');
    } finally {
      setSavingPolicy(false);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          background: toast.type === 'error' ? '#ef4444' : '#10b981',
          color: 'white',
          padding: '1rem 1.5rem',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 9999,
          animation: 'slideIn 0.3s ease-out',
          whiteSpace: 'pre-wrap'
        }}>
          {toast.message}
        </div>
      )}
      <div style={{ marginBottom: '2rem' }}>
        <h1>Settings & Configuration</h1>
        <p>Manage your account, API integrations, and email preferences.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div className="card">
          <h3>Personal Details</h3>
          {loading ? (
            <p>Loading settings...</p>
          ) : (
            <>
              <div className="form-group">
                <label className="label">Full Name</label>
                <input 
                  className="input" 
                  value={personalDetails.fullName} 
                  onChange={(e) => setPersonalDetails({ ...personalDetails, fullName: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="label">Email Address</label>
                <input 
                  className="input" 
                  value={personalDetails.email} 
                  onChange={(e) => setPersonalDetails({ ...personalDetails, email: e.target.value })}
                  placeholder="name@example.com"
                />
                <p style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', marginTop: '0.25rem' }}>
                  This is the email address used for sending campaigns.
                </p>
              </div>
              <button 
                className="btn" 
                onClick={handleSaveProfile}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Profiles'}
              </button>
            </>
          )}
        </div>

        <div className="card">
          <h3>Connection Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border)' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.875rem' }}>Claude AI Engine</strong>
                <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Powered by claude-3-5-sonnet</span>
              </div>
              <span style={{ padding: '0.25rem 0.5rem', background: '#dcfce7', color: '#166534', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>Connected</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.875rem' }}>SMTP Server</strong>
                <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Gmail Marketing Gateway</span>
              </div>
              <span style={{ padding: '0.25rem 0.5rem', background: '#dcfce7', color: '#166534', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>Active</span>
            </div>
          </div>
        </div>

        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3>Marketing Policies</h3>
          <p style={{ marginBottom: '1rem' }}>Define how your AI agent handles replies and follow-ups.</p>
          
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={policies.auto_reply_enabled} 
              onChange={(e) => setPolicies({ ...policies, auto_reply_enabled: e.target.checked })}
              style={{ marginRight: '0.75rem', width: '20px', height: '20px' }} 
            />
            <div>
              <strong>Auto-Reply to Unread Emails</strong>
              <div style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>Automatically generate and send responses using AI when unread replies are found.</div>
            </div>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={policies.duplicate_prevention_enabled} 
              onChange={(e) => setPolicies({ ...policies, duplicate_prevention_enabled: e.target.checked })}
              style={{ marginRight: '0.75rem', width: '20px', height: '20px' }} 
            />
            <div>
              <strong>Duplicate Prevention</strong>
              <div style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>Prevent adding leads with email addresses that already exist in your database.</div>
            </div>
          </label>

          <button 
            className="btn" 
            onClick={handleApplyStrategy}
            disabled={savingPolicy}
          >
            {savingPolicy ? 'Applying...' : 'Apply Strategy'}
          </button>
        </div>
      </div>
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(-8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </div>
  );
}
