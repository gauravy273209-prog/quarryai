'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface AgentStat {
  agent_name: string;
  call_count: number;
  avg_duration: number;
}

interface AnalyticsSummary {
  total_calls: number;
  avg_duration_seconds: number;
  total_talk_time_seconds: number;
  per_agent: AgentStat[];
}

function formatDuration(seconds: number): string {
  if (!seconds || seconds < 60) return seconds + 's';
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return m + 'm ' + s + 's';
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div style={{
      background: '#1a1d27', border: '1px solid #2d3748',
      borderRadius: 12, padding: '20px 24px',
      display: 'flex', alignItems: 'center', gap: 16,
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 10, flexShrink: 0,
        background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
      }}>
        {icon}
      </div>
      <div>
        <p style={{ margin: 0, fontSize: 12, color: '#64748b', fontWeight: 500 }}>{label}</p>
        <p style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#f1f5f9', marginTop: 2 }}>{value}</p>
      </div>
    </div>
  );
}

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8'];

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const { getToken } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      const token = await getToken();
      const res = await fetch('http://localhost:8000/api/v1/analytics/summary', {
        headers: { Authorization: 'Bearer ' + token },
      });
      const d = await res.json();
      setData(d);
      setLoading(false);
    };
    fetchData().catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#475569' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
        <p>Loading analytics…</p>
      </div>
    </div>
  );

  if (!data) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#ef4444' }}>
      Failed to load analytics.
    </div>
  );

  const perAgent = data.per_agent ?? [];
const chartData = perAgent.map(a => ({
    name: a.agent_name.length > 12 ? a.agent_name.slice(0, 12) + '…' : a.agent_name,
    calls: a.call_count,
    fullName: a.agent_name,
  }));

  return (
    <div style={{ padding: '32px', maxWidth: 900, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>Analytics</h1>
        <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>Overview of your voice AI activity</p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 28 }}>
        <StatCard icon="📞" label="Total Calls" value={String(data.total_calls)} />
        <StatCard icon="⏱" label="Avg Duration" value={formatDuration(data.avg_duration_seconds)} />
        <StatCard icon="🎙️" label="Total Talk Time" value={formatDuration(data.total_talk_time_seconds)} />
      </div>

      {/* Bar Chart */}
      {chartData.length > 0 && (
        <div style={{
          background: '#1a1d27', border: '1px solid #2d3748',
          borderRadius: 12, padding: '24px', marginBottom: 28,
        }}>
          <h3 style={{ margin: '0 0 20px', fontSize: 15, fontWeight: 600, color: '#f1f5f9' }}>
            Calls per Agent
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barCategoryGap="30%">
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: '#0f1117', border: '1px solid #2d3748', borderRadius: 8, color: '#f1f5f9' }}
                cursor={{ fill: 'rgba(99,102,241,0.08)' }}
                formatter={(value: number, _: string, props: { payload?: { fullName?: string } }) => [value + ' calls', props.payload?.fullName ?? '']}
              />
              <Bar dataKey="calls" radius={[6, 6, 0, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Per Agent Table */}
      <div style={{ background: '#1a1d27', border: '1px solid #2d3748', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #2d3748' }}>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: '#f1f5f9' }}>Per Agent Breakdown</h3>
        </div>
        {perAgent.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#475569' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>🤖</div>
            <p>No agent data yet. Make some calls first!</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2d3748' }}>
                {['Agent', 'Total Calls', 'Avg Duration'].map(h => (
                  <th key={h} style={{ padding: '12px 24px', textAlign: 'left', color: '#64748b', fontWeight: 500, fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {perAgent.map((agent, i) => (
                <tr key={i} style={{ borderBottom: i < data.per_agent.length - 1 ? '1px solid #2d3748' : 'none' }}>
                  <td style={{ padding: '14px 24px', color: '#f1f5f9', fontWeight: 500 }}>{agent.agent_name}</td>
                  <td style={{ padding: '14px 24px', color: '#94a3b8' }}>{agent.call_count}</td>
                  <td style={{ padding: '14px 24px', color: '#94a3b8' }}>{formatDuration(agent.avg_duration)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}