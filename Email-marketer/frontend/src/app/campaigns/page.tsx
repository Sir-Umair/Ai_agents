'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function CampaignsPage() {
  const [user, setUser] = useState<any>(null);
  const [leads, setLeads] = useState<any[]>([]);
  const [selectedEmails, setSelectedEmails] = useState<string[]>([]);
  
  // Main Email State
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');
  const [attachment, setAttachment] = useState<File | null>(null);
  
  // Follow-up State
  const [followUpDelay, setFollowUpDelay] = useState(0); // 0 means no follow-up, -1 means custom
  const [customDelayValue, setCustomDelayValue] = useState(2);
  const [customDelayType, setCustomDelayType] = useState('hours');
  const [isCustomFollowUp, setIsCustomFollowUp] = useState(false);
  const [followUpBody, setFollowUpBody] = useState('');
  const [aiFollowUpPrompt, setAiFollowUpPrompt] = useState('');
  
  // Auto-Reply Logic State
  const [autoReplyPrompt, setAutoReplyPrompt] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [fetchingSuggestions, setFetchingSuggestions] = useState(false);

  const [loadingLeads, setLoadingLeads] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatingFollowUp, setGeneratingFollowUp] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        const [userData, leadsData] = await Promise.all([
          api.getMe(),
          api.getLeads()
        ]);
        setUser(userData);
        setLeads(leadsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingLeads(false);
      }
    };
    init();
  }, []);

  const toggleSelectAll = () => {
    if (selectedEmails.length === leads.length) {
      setSelectedEmails([]);
    } else {
      setSelectedEmails(leads.map(l => l.email));
    }
  };

  const toggleSelectLead = (email: string) => {
    if (selectedEmails.includes(email)) {
      setSelectedEmails(selectedEmails.filter(e => e !== email));
    } else {
      setSelectedEmails([...selectedEmails, email]);
    }
  };

  const handleGenerateAI = async () => {
    if (!aiPrompt) return alert('Please enter a prompt for AI generation');
    try {
      setGenerating(true);
      const res = await api.generateEmailContent(aiPrompt);
      setBody(res.generated_content);
    } catch (err: any) {
      alert(err.message || 'Failed to generate AI content');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateFollowUp = async () => {
    if (!subject || !body) return alert('Please construct an original Subject and Body first.');
    try {
      setGeneratingFollowUp(true);
      let res;
      if (aiFollowUpPrompt) {
        res = await api.generateFollowupFromPrompt({
          prompt: aiFollowUpPrompt,
          original_subject: subject,
          original_body: body
        });
      } else {
        res = await api.generateFollowupContent(subject, body);
      }
      setFollowUpBody(res.generated_content);
      setIsCustomFollowUp(true);
    } catch (err: any) {
      alert(err.message || 'Failed to generate AI follow up content');
    } finally {
      setGeneratingFollowUp(false);
    }
  };

  const handleFetchSuggestions = async () => {
    if (!subject || !body) return alert('Please draft the main email first to get relevant suggestions.');
    try {
      setFetchingSuggestions(true);
      const res = await api.getAutoReplySuggestions(subject, body);
      setSuggestions(res.suggestions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setFetchingSuggestions(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (file.type !== "application/pdf") {
        alert("Only PDF files are supported format at this time.");
        e.target.value = '';
        return;
      }
      setAttachment(file);
    }
  };

  const handleSendCampaign = async () => {
    if (selectedEmails.length === 0) return alert('Please select at least one lead');
    if (!subject || !body) return alert('Subject and Body are required');
    
    try {
      setSending(true);
      const finalDelay = followUpDelay === -1 
        ? (customDelayType === 'days' ? customDelayValue * 1440 : customDelayType === 'hours' ? customDelayValue * 60 : customDelayValue) 
        : followUpDelay;

      const result = await api.sendBulkEmails({
        emails: selectedEmails,
        subject,
        body,
        attachment,
        follow_up_delay: finalDelay,
        follow_up_body: isCustomFollowUp ? followUpBody : undefined,
        auto_reply_prompt: autoReplyPrompt || undefined
      });

      if (result.failed === 0) {
        alert(`🚀 Campaign launched! Successfully sent to all ${result.successful} leads.`);
        setSubject('');
        setBody('');
        setFollowUpBody('');
        setFollowUpDelay(0);
        setIsCustomFollowUp(false);
        setAttachment(null);
        setSelectedEmails([]);
      } else {
        alert(`⚠️ Campaign partially sent:\n✅ Successful: ${result.successful}\n❌ Failed: ${result.failed}`);
      }
    } catch (err: any) {
      alert(`❌ Campaign Failed:\n\n${err.message}`);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, #6366f1, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          AI Campaign Architect
        </h1>
        <p style={{ fontSize: '1.1rem' }}>Design high-conversion email sequences with real-time AI assistance.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2.5rem' }}>
        {/* Main Workspace */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Step 1: AI Content Generation */}
          <section className="card" style={{ borderLeft: '4px solid #6366f1' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <span style={{ background: '#6366f1', color: 'white', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 'bold' }}>1</span>
              <h3 style={{ margin: 0 }}>AI Content Assistant</h3>
            </div>
            
            <div className="form-group">
              <label className="label">What are you offering? (AI Prompt)</label>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <input 
                  className="input" 
                  style={{ flex: 1 }}
                  placeholder="Ex: Reach out to tech founders about our new Cloud Security audit..."
                  value={aiPrompt}
                  onChange={e => setAiPrompt(e.target.value)}
                />
                <button 
                  className="btn" 
                  style={{ minWidth: '130px', background: 'linear-gradient(45deg, #6366f1, #4f46e5)' }}
                  onClick={handleGenerateAI}
                  disabled={generating}
                >
                  {generating ? '✨ Magic...' : '✨ Generate'}
                </button>
              </div>
            </div>
          </section>

          {/* Step 2: Main Email Composition */}
          <section className="card" style={{ borderLeft: '4px solid #10b981' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <span style={{ background: '#10b981', color: 'white', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 'bold' }}>2</span>
              <h3 style={{ margin: 0 }}>Main Email Outreach</h3>
            </div>

            <div className="form-group">
              <label className="label">Subject Line</label>
              <input 
                className="input" 
                placeholder="Hook them with a great subject..." 
                value={subject}
                onChange={e => setSubject(e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label className="label">Message Body</label>
              <textarea 
                className="input" 
                rows={10} 
                style={{ resize: 'vertical', fontFamily: 'inherit', lineHeight: '1.6' }}
                placeholder="Draft your main message here..."
                value={body}
                onChange={e => setBody(e.target.value)}
              ></textarea>
            </div>

            <div className="form-group">
              <label className="label">PDF Attachment (Trust Builder)</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', border: '2px dashed var(--border)', borderRadius: 'var(--radius)', background: '#f8fafc' }}>
                <input 
                  type="file" 
                  accept=".pdf" 
                  onChange={handleFileChange} 
                  style={{ fontSize: '0.875rem' }}
                />
                {attachment && <span style={{ color: '#10b981', fontWeight: 500 }}>✓ {attachment.name}</span>}
              </div>
            </div>
          </section>

          {/* Step 3: Follow-up Logic (Professionalized & Separated) */}
          <section className="card" style={{ borderLeft: '4px solid #f59e0b', background: '#fffbeb' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <span style={{ background: '#f59e0b', color: 'white', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 'bold' }}>3</span>
              <h3 style={{ margin: 0 }}>Automated Follow-up Strategy</h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div className="form-group">
                <label className="label">Trigger Condition</label>
                <select 
                  className="input" 
                  value={followUpDelay === -1 && customDelayValue === 0 ? 0 : followUpDelay} 
                  onChange={e => {
                    const val = parseInt(e.target.value);
                    setFollowUpDelay(val);
                    if (val === 0) setIsCustomFollowUp(false);
                  }}
                >
                  <option value={0}>No automatic follow-up</option>
                  <option value={1}>If no reply after 1 minute (Test Mode)</option>
                  <option value={60}>If no reply after 1 hour</option>
                  <option value={1440}>If no reply after 24 hours</option>
                  <option value={2880}>If no reply after 48 hours</option>
                  <option value={4320}>If no reply after 72 hours</option>
                  <option value={-1}>Custom Time Delay...</option>
                </select>

                {followUpDelay === -1 && (
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', animation: 'fadeIn 0.3s' }}>
                    <input 
                      type="number" 
                      className="input" 
                      min="1"
                      placeholder="Amt"
                      value={customDelayValue || ''}
                      onChange={e => setCustomDelayValue(parseInt(e.target.value) || 0)}
                      style={{ width: '80px' }}
                    />
                    <select 
                      className="input" 
                      value={customDelayType}
                      onChange={e => setCustomDelayType(e.target.value)}
                    >
                      <option value="minutes">Minutes</option>
                      <option value="hours">Hours</option>
                      <option value="days">Days</option>
                    </select>
                  </div>
                )}
              </div>

              {(followUpDelay > 0 || followUpDelay === -1) && (
                <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', padding: '0.75rem', background: 'white', borderRadius: 'var(--radius)', border: '1px solid var(--border)', width: '100%' }}>
                    <input 
                      type="checkbox" 
                      checked={isCustomFollowUp}
                      onChange={e => setIsCustomFollowUp(e.target.checked)}
                      style={{ width: '18px', height: '18px' }}
                    />
                    <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Customize follow-up mail?</span>
                  </label>
                </div>
              )}
            </div>

            {isCustomFollowUp && (
              <div style={{ marginTop: '1rem', animation: 'fadeIn 0.3s' }}>
                <div className="form-group">
                  <label className="label">Follow-up AI Assistant (Optional Prompt)</label>
                  <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
                    <input 
                      className="input" 
                      style={{ flex: 1 }}
                      placeholder="Ex: Keep it short, ask if they have 5 mins for a call..."
                      value={aiFollowUpPrompt}
                      onChange={e => setAiFollowUpPrompt(e.target.value)}
                    />
                    <button 
                      className="btn btn-secondary" 
                      style={{ minWidth: '130px' }}
                      onClick={handleGenerateFollowUp}
                      disabled={generatingFollowUp}
                    >
                      {generatingFollowUp ? '✨ Magic...' : '🪄 Generate'}
                    </button>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <label className="label" style={{ margin: 0 }}>Custom Follow-up Content</label>
                  {!aiFollowUpPrompt && (
                    <button 
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                      onClick={handleGenerateFollowUp}
                      disabled={generatingFollowUp}
                    >
                      {generatingFollowUp ? 'Generating...' : '🪄 Auto-Nudge (Based on Original)'}
                    </button>
                  )}
                </div>
                <textarea 
                  className="input" 
                  rows={6} 
                  placeholder="The 'gentle nudge' message..."
                  value={followUpBody}
                  onChange={e => setFollowUpBody(e.target.value)}
                ></textarea>
              </div>
            )}
          </section>

          {/* Step 4: Intelligent Auto-Responder Instructions */}
          <section className="card" style={{ borderLeft: '4px solid #8b5cf6', background: '#f5f3ff' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <span style={{ background: '#8b5cf6', color: 'white', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 'bold' }}>4</span>
              <h3 style={{ margin: 0 }}>Adaptive Auto-Responder</h3>
            </div>

            <div className="form-group">
              <label className="label">Inbound Reply Strategy</label>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1rem' }}>Tell the AI exactly how to respond when a lead replies to this campaign.</p>
              
              <textarea 
                className="input" 
                rows={3} 
                placeholder="Ex: Be very aggressive on booking a call, or 'Answer questions about the free trial but don't give pricing'..."
                value={autoReplyPrompt}
                onChange={e => setAutoReplyPrompt(e.target.value)}
                style={{ marginBottom: '1rem' }}
              ></textarea>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <button 
                  className="btn btn-outline" 
                  style={{ width: 'fit-content', fontSize: '0.875rem' }}
                  onClick={handleFetchSuggestions}
                  disabled={fetchingSuggestions}
                >
                  {fetchingSuggestions ? 'Thinking...' : '💡 Get Strategy Suggestions'}
                </button>

                {suggestions.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                    {suggestions.map((s, i) => (
                      <button 
                        key={i}
                        onClick={() => setAutoReplyPrompt(s)}
                        style={{ padding: '0.4rem 0.8rem', background: 'white', border: '1px solid #ddd6fe', borderRadius: '999px', fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s' }}
                        onMouseOver={e => (e.currentTarget.style.borderColor = '#8b5cf6')}
                        onMouseOut={e => (e.currentTarget.style.borderColor = '#ddd6fe')}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </section>

          <button 
            className="btn" 
            style={{ width: '100%', padding: '1.25rem', fontSize: '1.125rem', boxShadow: '0 4px 14px 0 rgba(99, 102, 241, 0.39)', marginTop: '1rem' }}
            onClick={handleSendCampaign}
            disabled={sending || selectedEmails.length === 0}
          >
            {sending ? '🚀 Launching Campaign...' : `🚀 Launch Campaign to ${selectedEmails.length} Leads`}
          </button>
        </div>

        {/* Lead Selection Sidebar */}
        <aside>
          <div className="card" style={{ height: 'fit-content', position: 'sticky', top: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Target Audience</h3>
            <div style={{ padding: '0.75rem', background: '#f0f9ff', borderRadius: '6px', border: '1px solid #bae6fd', marginBottom: '1.5rem', fontSize: '0.875rem', color: '#0369a1' }}>
              Selected: <strong>{selectedEmails.length}</strong> / {leads.length} leads
            </div>
            
            <button 
              className="btn btn-outline" 
              style={{ width: '100%', marginBottom: '1.5rem', fontWeight: 600 }}
              onClick={toggleSelectAll}
            >
              {selectedEmails.length === leads.length ? 'Deselect All' : 'Select All Leads'}
            </button>

            <div style={{ maxHeight: 'calc(100vh - 400px)', overflowY: 'auto' }}>
              {loadingLeads ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>Loading leads...</div>
              ) : !Array.isArray(leads) || leads.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted-foreground)' }}>No leads found in database.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {leads.map(lead => (
                    <label 
                      key={lead.id} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        padding: '0.75rem', 
                        borderRadius: '8px',
                        background: selectedEmails.includes(lead.email) ? '#f5f3ff' : 'transparent',
                        border: selectedEmails.includes(lead.email) ? '1px solid #ddd6fe' : '1px solid transparent',
                        transition: 'all 0.2s',
                        cursor: 'pointer'
                      }}
                    >
                      <input 
                        type="checkbox" 
                        checked={selectedEmails.includes(lead.email)}
                        onChange={() => toggleSelectLead(lead.email)}
                        style={{ marginRight: '1rem', width: '16px', height: '16px' }}
                      />
                      <div style={{ overflow: 'hidden' }}>
                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{lead.name || 'N/A'}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{lead.email}</div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>
        </aside>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </div>
  );
}
