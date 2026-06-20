'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

interface Message { role: string; content: string; }
interface Call {
  id: string; agent_name: string; status: string;
  duration_seconds: number | null; transcript: Message[]; started_at: string | null;
}

const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  completed: { label: 'Completed', color: '#22c55e', bg: 'rgba(34,197,94,0.12)' },
  failed:    { label: 'Failed',    color: '#ef4444', bg: 'rgba(239,68,68,0.12)'  },
  ongoing:   { label: 'Ongoing',   color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  queued:    { label: 'Queued',    color: '#6366f1', bg: 'rgba(99,102,241,0.12)' },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] ?? { label: status, color: '#94a3b8', bg: 'rgba(148,163,184,0.12)' };
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: cfg.bg, color: cfg.color, border: '1px solid ' + cfg.color + '44', borderRadius: 20, padding: '3px 10px', fontSize: 12, fontWeight: 600 }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: cfg.color, display: 'inline-block' }} />
      {cfg.label}
    </span>
  );
}

function AgentAvatar({ name }: { name: string }) {
  const initials = name.split(' ').map((w: string) => w[0]).join('').slice(0, 2).toUpperCase();
  const hue = name.charCodeAt(0) * 37 % 360;
  return (
    <div style={{ width: 36, height: 36, borderRadius: '50%', flexShrink: 0, background: `linear-gradient(135deg, hsl(${hue},70%,55%), hsl(${(hue+60)%360},70%,45%))`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: '#fff' }}>
      {initials}
    </div>
  );
}

function formatDuration(seconds: number | null) {
  if (!seconds) return '—';
  const m = Math.floor(seconds / 60), s = seconds % 60;
  return m > 0 ? m + 'm ' + s + 's' : s + 's';
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function CallsPage() {
  const { getToken } = useAuth();
  const [calls, setCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchCalls = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/v1/calls/`, {
          headers: { Authorization: 'Bearer ' + token },
        });
        if (!res.ok) throw new Error('Failed to load calls (status ' + res.status + ')');
        const data = await res.json();
        setCalls(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchCalls();
  }, [getToken]);

  const filtered = calls.filter((c) =>
    c.agent_name?.toLowerCase().includes(search.toLowerCase()) ||
    c.status?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ padding: '32px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>Call History</h1>
        <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>
          {loading ? 'Loading…' : calls.length + ' call' + (calls.length !== 1 ? 's' : '') + ' recorded'}
        </p>
      </div>

      {error && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, padding: '12px 16px', marginBottom: 20, color: '#ef4444', fontSize: 14 }}>
          ⚠️ {error}
        </div>
      )}

      <div style={{ marginBottom: 20, position: 'relative' }}>
        <span style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569', fontSize: 16 }}>🔍</span>
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by agent or status…"
          style={{ width: '100%', boxSizing: 'border-box', background: '#1a1d27', border: '1px solid #2d3748', borderRadius: 10, padding: '10px 14px 10px 40px', color: '#f1f5f9', fontSize: 14, outline: 'none' }} />
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', paddingTop: 80, color: '#475569' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div><p>Loading calls…</p>
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', paddingTop: 80 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📞</div>
          <p style={{ fontSize: 16, color: '#64748b' }}>{search ? 'No calls match your search.' : 'No calls yet.'}</p>
          <p style={{ fontSize: 13, color: '#475569', marginTop: 6 }}>{search ? 'Try a different search term.' : 'Calls will appear here once Twilio is connected.'}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map((call) => (
            <div key={call.id} style={{ background: '#1a1d27', border: '1px solid #2d3748', borderRadius: 12, padding: '16px 20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
                  <AgentAvatar name={call.agent_name ?? '?'} />
                  <div style={{ minWidth: 0 }}>
                    <p style={{ margin: 0, fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>{call.agent_name ?? 'Unknown agent'}</p>
                    <p style={{ margin: 0, fontSize: 12, color: '#64748b', marginTop: 2 }}>{formatDate(call.started_at)}</p>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
                  <span style={{ fontSize: 13, color: '#94a3b8' }}>⏱ {formatDuration(call.duration_seconds)}</span>
                  <StatusBadge status={call.status} />
                  <button onClick={() => setExpanded(expanded === call.id ? null : call.id)}
                    style={{ background: 'transparent', border: '1px solid #2d3748', borderRadius: 8, padding: '4px 12px', fontSize: 12, color: '#6366f1', cursor: 'pointer' }}>
                    {expanded === call.id ? 'Hide' : 'Transcript'}
                  </button>
                </div>
              </div>
              {expanded === call.id && (
                <div style={{ marginTop: 16, borderTop: '1px solid #2d3748', paddingTop: 16 }}>
                  {!call.transcript || call.transcript.length === 0 ? (
                    <p style={{ color: '#475569', fontSize: 13, textAlign: 'center' }}>No transcript available.</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {call.transcript.map((msg, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                          <div style={{ maxWidth: '75%', padding: '8px 14px', borderRadius: 10, fontSize: 13, background: msg.role === 'user' ? 'rgba(99,102,241,0.15)' : '#0f1117', color: msg.role === 'user' ? '#a5b4fc' : '#cbd5e1', border: '1px solid ' + (msg.role === 'user' ? '#6366f133' : '#2d3748') }}>
                            <span style={{ fontWeight: 600, fontSize: 11, opacity: 0.6, textTransform: 'uppercase', display: 'block', marginBottom: 2 }}>{msg.role === 'user' ? 'Caller' : 'Alex'}</span>
                            {msg.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
