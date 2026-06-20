import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

async function getAgents(token: string) {
  try {
    const res = await fetch(`${API_URL}/api/v1/agents/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch { return []; }
}

const gradients = [
  "from-blue-500 to-violet-600",
  "from-emerald-400 to-cyan-500",
  "from-orange-400 to-pink-500",
];

function getInitials(name: string) {
  return name.split(" ").map((w: string) => w[0]).join("").toUpperCase().slice(0, 2);
}

export default async function DashboardPage() {
  const { userId, getToken } = await auth();
  if (!userId) redirect("/sign-in");
  const token = await getToken();
  const agents = await getAgents(token ?? "");
  return (
    <div className="min-h-screen bg-[#f8f9fc]">
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Agents</h2>
            <p className="text-gray-400 text-sm mt-1">Manage your AI voice agents</p>
          </div>
          <Link href="/dashboard/agents/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
            <span>+</span> New Agent
          </Link>
        </div>
        {agents.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-100 p-16 text-center">
            <p className="text-gray-700 font-medium">No agents yet</p>
            <p className="text-gray-400 text-sm mt-1">Create your first voice agent to get started</p>
            <Link href="/dashboard/agents/new" className="inline-block mt-5 bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">Create Agent</Link>
          </div>
        ) : (
          <div className="grid gap-2.5">
            {agents.map((agent: { id: string; name: string; description?: string; phone_number?: string }, index: number) => {
              const gradient = gradients[index % gradients.length];
              return (
                <Link key={agent.id} href={`/dashboard/agents/${agent.id}`} className="bg-white rounded-xl border border-gray-100 px-5 py-4 hover:border-blue-200 hover:shadow-md transition-all flex items-center justify-between group">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 bg-gradient-to-br ${gradient} rounded-xl flex items-center justify-center`}>
                      <span className="text-white text-xs font-bold">{getInitials(agent.name)}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-sm">{agent.name}</h3>
                      {agent.description && <p className="text-gray-400 text-xs mt-0.5">{agent.description}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-gray-300 text-xs bg-gray-50 px-2.5 py-1 rounded-md border border-gray-100">{agent.phone_number || "No number"}</span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-100">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>Active
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
