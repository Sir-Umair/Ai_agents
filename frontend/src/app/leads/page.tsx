'use client';

import { useEffect, useState, useCallback } from 'react';
import { api } from '@/lib/api';

interface Lead {
  id: string;
  name: string;
  email: string;
  company?: string;
  notes?: string;
  created_at: string;
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [newLead, setNewLead] = useState({ name: '', email: '', company: '', notes: '' });
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const fetchLeads = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getLeads();
      let actualData: Lead[] = [];
      if (Array.isArray(response)) {
        actualData = response;
      } else if (response && typeof response === 'object') {
        actualData = response.leads || response.data || [];
      }
      setLeads(actualData);
    } catch (err) {
      console.error('Fetch Error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  async function handleAddLead(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createLead(newLead);
      setNewLead({ name: '', email: '', company: '', notes: '' });
      setIsAdding(false);
      fetchLeads();
    } catch (err: any) {
      alert(err.message || 'Failed to add lead');
    }
  }

  // First click selects; clicking Delete on an already-selected row deselects it
  function handleDeleteClick(id: string) {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  }

  async function handleBulkDelete() {
    if (selectedIds.size === 0) return;
    if (!confirm(`Permanently delete ${selectedIds.size} selected lead${selectedIds.size > 1 ? 's' : ''}?`)) return;
    try {
      setLoading(true);
      await Promise.all(Array.from(selectedIds).map(id => api.deleteLead(id)));
      setSelectedIds(new Set());
      fetchLeads();
    } catch (err) {
      alert('Bulk delete failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>Leads Management</h1>
          <p style={{ color: '#6b7280' }}>Organize and manage your contacts for targeted email campaigns.</p>
        </div>
        <button
          onClick={() => setIsAdding(!isAdding)}
          style={{
            backgroundColor: isAdding ? '#ef4444' : '#4f46e5',
            color: 'white',
            padding: '0.625rem 1.25rem',
            borderRadius: '0.5rem',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600',
          }}
        >
          {isAdding ? 'Cancel' : '+ Add New Lead'}
        </button>
      </div>

      {/* Add Lead Form */}
      {isAdding && (
        <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.75rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '2rem', border: '1px solid #e5e7eb' }}>
          <h3 style={{ marginBottom: '1.25rem', fontSize: '1.125rem', fontWeight: '600' }}>Create a New Lead</h3>
          <form onSubmit={handleAddLead} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <input
              placeholder="Name (Optional)" value={newLead.name}
              onChange={e => setNewLead({ ...newLead, name: e.target.value })}
              style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
            />
            <input
              placeholder="Email" type="email" required value={newLead.email}
              onChange={e => setNewLead({ ...newLead, email: e.target.value })}
              style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
            />
            <input
              placeholder="Company" value={newLead.company}
              onChange={e => setNewLead({ ...newLead, company: e.target.value })}
              style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
            />
            <input
              placeholder="Notes" value={newLead.notes}
              onChange={e => setNewLead({ ...newLead, notes: e.target.value })}
              style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
            />
            <button type="submit" style={{ gridColumn: 'span 2', backgroundColor: '#4f46e5', color: 'white', padding: '0.75rem', borderRadius: '0.375rem', border: 'none', cursor: 'pointer' }}>
              Save Lead
            </button>
          </form>
        </div>
      )}

      {/* Floating bulk-action bar */}
      {selectedIds.size > 0 && (
        <div style={{
          position: 'sticky',
          top: '1rem',
          zIndex: 50,
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          background: '#1e1b4b',
          color: 'white',
          padding: '0.75rem 1.5rem',
          borderRadius: '12px',
          marginBottom: '1rem',
          boxShadow: '0 8px 32px rgba(79, 70, 229, 0.35)',
          animation: 'slideIn 0.2s ease',
        }}>
          <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
            {selectedIds.size} lead{selectedIds.size > 1 ? 's' : ''} selected
          </span>
          <div style={{ flex: 1 }} />
          <button
            onClick={handleBulkDelete}
            style={{ background: '#ef4444', border: 'none', color: 'white', padding: '0.4rem 1rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '0.875rem' }}
          >
            Delete {selectedIds.size} Selected
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            style={{ background: 'none', border: '1px solid rgba(255,255,255,0.3)', color: 'rgba(255,255,255,0.7)', padding: '0.4rem 0.75rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.875rem' }}
          >
            Cancel
          </button>
        </div>
      )}

      {/* Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '0.75rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb', minHeight: '200px' }}>
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '200px' }}>
            <p style={{ color: '#6b7280' }}>Loading your leads...</p>
            <button onClick={fetchLeads} style={{ marginTop: '0.5rem', color: '#4f46e5', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.875rem' }}>Retry</button>
          </div>
        ) : leads.length === 0 ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: '#6b7280' }}>
            No leads found yet. Start by adding one!
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <tr>
                <th style={{ textAlign: 'left', padding: '1rem', color: '#374151' }}>Name</th>
                <th style={{ textAlign: 'left', padding: '1rem', color: '#374151' }}>Email</th>
                <th style={{ textAlign: 'left', padding: '1rem', color: '#374151' }}>Company</th>
                <th style={{ textAlign: 'left', padding: '1rem', color: '#374151' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => {
                const isSelected = selectedIds.has(lead.id);
                return (
                  <tr
                    key={lead.id}
                    style={{ borderBottom: '1px solid #f3f4f6', background: isSelected ? 'rgba(239,68,68,0.06)' : 'transparent', transition: 'background 0.15s' }}
                  >
                    <td style={{ padding: '1rem' }}><strong>{lead.name || 'N/A'}</strong></td>
                    <td style={{ padding: '1rem', color: '#4b5563' }}>{lead.email}</td>
                    <td style={{ padding: '1rem', color: '#4b5563' }}>{lead.company || '-'}</td>
                    <td style={{ padding: '1rem' }}>
                      <button
                        onClick={() => handleDeleteClick(lead.id)}
                        style={{
                          color: isSelected ? '#ef4444' : '#9ca3af',
                          background: isSelected ? 'rgba(239,68,68,0.1)' : 'none',
                          border: isSelected ? '1px solid rgba(239,68,68,0.3)' : 'none',
                          cursor: 'pointer',
                          padding: '0.25rem 0.6rem',
                          borderRadius: '6px',
                          fontWeight: isSelected ? 700 : 400,
                          fontSize: '0.875rem',
                          transition: 'all 0.15s',
                        }}
                        title={isSelected ? 'Click to deselect' : 'Click to select for deletion'}
                      >
                        {isSelected ? 'Selected' : 'Delete'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
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
