import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import AgentEditForm from "./AgentEditForm";

export default async function AgentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");

  const res = await fetch(
    `http://localhost:8000/api/v1/agents/internal/${userId}/${id}`,
    { cache: "no-store" }
  );

  if (!res.ok) return <div className="p-10 text-red-500">Agent not found.</div>;
  const agent = await res.json();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">QuarryAI</h1>
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-sm text-gray-900 font-medium">Agents</Link>
          <Link href="/dashboard/calls" className="text-sm text-gray-500 hover:text-gray-700">Call History</Link>
          <Link href="/dashboard/analytics" className="text-sm text-gray-500 hover:text-gray-700">Analytics</Link>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto px-6 py-10">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-gray-600 mb-8 inline-block">Back to Agents</Link>
        <AgentEditForm agent={agent} token={userId} />
      </main>
    </div>
  );
}