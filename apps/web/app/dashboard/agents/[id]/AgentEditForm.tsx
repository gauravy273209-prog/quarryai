'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AgentEditForm({ agent, token }: { agent: any; token: string }) {
  const router = useRouter();
  const [data, setData] = useState(agent);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function handleSave() {
    setSaving(true);
    await fetch(`http://localhost:8000/api/v1/agents/${data.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name: data.name, description: data.description, system_prompt: data.system_prompt }),
    });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  async function handleDelete() {
    if (!confirm('Delete this agent? This cannot be undone.')) return;
    setDeleting(true);
    await fetch(`http://localhost:8000/api/v1/agents/${data.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    router.push('/dashboard');
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-8">
      <div className="flex justify-between items-start mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">Edit Agent</h2>
        <button onClick={handleDelete} disabled={deleting}
          className="text-sm text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 px-3 py-1.5 rounded-lg transition-colors">
          {deleting ? 'Deleting...' : 'Delete Agent'}
        </button>
      </div>
      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
          <input type="text" value={data.name || ''} onChange={e => setData({ ...data, name: e.target.value })}
            className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <input type="text" value={data.description || ''} onChange={e => setData({ ...data, description: e.target.value })}
            className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
          <textarea rows={8} value={data.system_prompt || ''} onChange={e => setData({ ...data, system_prompt: e.target.value })}
            className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300 resize-none"
            placeholder="You are a helpful AI voice assistant..." />
        </div>
        {data.phone_number && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
            <div className="w-full border border-gray-100 bg-gray-50 rounded-lg px-4 py-2.5 text-sm text-gray-500">{data.phone_number}</div>
          </div>
        )}
        <div className="flex items-center gap-3 pt-2">
          <button onClick={handleSave} disabled={saving}
            className="bg-black text-white px-6 py-2.5 rounded-lg text-sm hover:bg-gray-800 transition-colors disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          {saved && <span className="text-sm text-green-600">Saved!</span>}
        </div>
      </div>
    </div>
  );
}