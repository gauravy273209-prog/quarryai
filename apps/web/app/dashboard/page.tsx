import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Link from "next/link";

async function getAgents() {
  try {
    const res = await fetch("http://localhost:8000/api/v1/agents/", {
      headers: { Authorization: "Bearer dev-token" },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");
  const agents = await getAgents();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">QuarryAI</h1>
        <Link href="/sign-in" className="text-sm text-gray-500 hover:text-gray-700">Sign out</Link>
      </nav>
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800">Your Agents</h2>
          <Link href="/dashboard/agents/new" className="bg-black text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-800">
            + New Agent
          </Link>
        </div>
        {agents.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <p className="text-gray-400 text-lg">No agents yet.</p>
            <p className="text-gray-400 text-sm mt-1">Create your first agent to get started.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {agents.map((agent: any) => (
              <Link key={agent.id} href={`/dashboard/agents/${agent.id}`}
                className="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-400 transition-colors">
                <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                {agent.description && <p className="text-gray-500 text-sm mt-1">{agent.description}</p>}
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}