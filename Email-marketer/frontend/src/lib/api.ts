const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
};

export const api = {
  // Auth
  async login() {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`);
    if (!response.ok) throw new Error('Failed to initiate login');
    return response.json();
  },

  async getMe() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch user info');
    return response.json();
  },

  // Leads
  async getLeads() {
    const response = await fetch(`${API_BASE_URL}/leads/`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch leads');
    return response.json();
  },

  async createLead(lead: { name: string; email: string; company?: string; notes?: string }) {
    const response = await fetch(`${API_BASE_URL}/leads/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(lead),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create lead');
    }
    return response.json();
  },

  async deleteLead(id: string) {
    const response = await fetch(`${API_BASE_URL}/leads/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete lead');
    return true;
  },

  // Emails
  async sendBulkEmails(data: { 
    emails: string[], 
    subject: string, 
    body: string, 
    attachment?: File | null,
    follow_up_delay: number,
    follow_up_body?: string,
    auto_reply_prompt?: string
  }) {
    const formData = new FormData();
    formData.append('emails_json', JSON.stringify(data.emails));
    formData.append('subject', data.subject);
    formData.append('body', data.body);
    formData.append('follow_up_delay', data.follow_up_delay.toString());
    if (data.follow_up_body) formData.append('follow_up_body', data.follow_up_body);
    if (data.auto_reply_prompt) formData.append('auto_reply_prompt', data.auto_reply_prompt);
    if (data.attachment) {
      formData.append('attachment', data.attachment);
    }

    const response = await fetch(`${API_BASE_URL}/emails/send-bulk`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Failed to send campaign');
    }
    return response.json();
  },

  async getAutoReplySuggestions(subject: string, body: string) {
    const response = await fetch(`${API_BASE_URL}/emails/auto-reply-suggestions`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ subject, body }),
    });
    return response.json();
  },

  async scheduleFollowUp(data: { lead_email: string; subject: string; body: string; delay_hours: number }) {
    const response = await fetch(`${API_BASE_URL}/emails/schedule-followup`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to schedule follow-up');
    return response.json();
  },

  async generateEmailContent(prompt: string) {
    const response = await fetch(`${API_BASE_URL}/emails/generate-content`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to generate content');
    }
    return response.json();
  },

  async generateFollowupContent(original_subject: string, original_body: string) {
    const response = await fetch(`${API_BASE_URL}/emails/generate-followup-content`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ original_subject, original_body }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to generate followup content');
    }
    return response.json();
  },

  async generateFollowupFromPrompt(data: { prompt: string; original_subject: string; original_body: string }) {
    const response = await fetch(`${API_BASE_URL}/emails/generate-followup-from-prompt`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to generate followup content from prompt');
    }
    return response.json();
  },

  async processReplies() {
    const response = await fetch(`${API_BASE_URL}/emails/process-replies`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to process replies');
    return response.json();
  },

  // Settings
  async getSettings() {
    const response = await fetch(`${API_BASE_URL}/settings/`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch settings');
    return response.json();
  },

  async updateSettings(data: any) {
    const response = await fetch(`${API_BASE_URL}/settings/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update settings');
    return response.json();
  },

  // Client Responses (replaces Google Sheets)
  async getResponses() {
    const response = await fetch(`${API_BASE_URL}/responses/`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch responses');
    return response.json();
  },

  async getCampaignDashboard() {
    const response = await fetch(`${API_BASE_URL}/responses/campaigns`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch campaign dashboard');
    return response.json();
  },

  async getThread(threadId: string) {
    const response = await fetch(`${API_BASE_URL}/responses/thread/${threadId}`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch thread');
    return response.json();
  },

  async deleteResponse(id: string) {
    const response = await fetch(`${API_BASE_URL}/responses/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete response');
    return response.json();
  },

  async deleteCampaign(campaignId: string) {
    const response = await fetch(`${API_BASE_URL}/responses/campaign/${campaignId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete campaign');
    return response.json();
  },

  // Recent activity logs for dashboard
  async getRecentLogs(limit = 50) {
    const response = await fetch(`${API_BASE_URL}/logs/recent?limit=${limit}`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch logs');
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/logs/stats`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  async deleteLog(id: string) {
    const response = await fetch(`${API_BASE_URL}/logs/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete log');
    return response.json();
  },
};
