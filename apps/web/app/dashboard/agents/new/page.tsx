"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";

export default function NewAgentPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!name.trim()) return alert("Name is required");
    setLoading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description, system_prompt: systemPrompt }),
      });
      if (!res.ok) throw new Error("Failed to create agent");
      router.push("/dashboard");
    } catch (err) {
      alert("Error creating agent");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">QuarryAI</h1>
        <Link href="/dashboard" className="text-sm text-gray-500 hover:text-gray-700">← Back</Link>
      </nav>
      <main className="max-w-2xl mx-auto px-6 py-10">
        <h2 className="text-2xl font-semibold text-gray-800 mb-8">Create New Agent</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-8 flex flex-col gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Sales Agent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              value={description} onChange={e => setDescription(e.target.value)} placeholder="What does this agent do?"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black h-32 resize-none"
              value={systemPrompt} onChange={e => setSystemPrompt(e.target.value)} placeholder="You are a helpful sales agent..."
            />
          </div>
          <button
            onClick={handleSubmit} disabled={loading}
            className="bg-black text-white px-6 py-2 rounded-lg text-sm hover:bg-gray-800 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Agent"}
          </button>
        </div>
      </main>
    </div>
  );
}