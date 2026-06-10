"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

export default function EditAgentPage() {
  const router = useRouter();
  const { id } = useParams();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/${id}`)
      .then(res => res.json())
      .then(data => {
        setName(data.name || "");
        setDescription(data.description || "");
        setSystemPrompt(data.system_prompt || "");
      })
      .finally(() => setFetching(false));
  }, [id]);

  async function handleSave() {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, system_prompt: systemPrompt }),
      });
      if (!res.ok) throw new Error("Failed to update");
      router.push("/dashboard");
    } catch {
      alert("Error saving agent");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this agent?")) return;
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/${id}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  if (fetching) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">QuarryAI</h1>
        <Link href="/dashboard" className="text-sm text-gray-500 hover:text-gray-700">← Back</Link>
      </nav>
      <main className="max-w-2xl mx-auto px-6 py-10">
        <h2 className="text-2xl font-semibold text-gray-800 mb-8">Edit Agent</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-8 flex flex-col gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              value={name} onChange={e => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              value={description} onChange={e => setDescription(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black h-32 resize-none"
              value={systemPrompt} onChange={e => setSystemPrompt(e.target.value)}
            />
          </div>
          <div className="flex justify-between">
            <button
              onClick={handleDelete}
              className="text-red-500 text-sm hover:text-red-700"
            >
              Delete Agent
            </button>
            <button
              onClick={handleSave} disabled={loading}
              className="bg-black text-white px-6 py-2 rounded-lg text-sm hover:bg-gray-800 disabled:opacity-50"
            >
              {loading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}