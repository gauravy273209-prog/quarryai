import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="px-6 py-4 flex justify-between items-center border-b border-gray-100">
        <h1 className="text-xl font-bold text-gray-900">QuarryAI</h1>
        <div className="flex gap-4">
          <Link href="/sign-in" className="text-sm text-gray-600 hover:text-gray-900">
            Sign in
          </Link>
          <Link href="/sign-up" className="bg-black text-white text-sm px-4 py-2 rounded-lg hover:bg-gray-800">
            Get started
          </Link>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-6 py-24 text-center">
        <div className="inline-block bg-gray-100 text-gray-600 text-xs px-3 py-1 rounded-full mb-6">
          AI Voice Agent Platform
        </div>
        <h2 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
          Build AI voice agents in minutes
        </h2>
        <p className="text-xl text-gray-500 mb-10 max-w-2xl mx-auto">
          QuarryAI lets you create, deploy, and manage AI voice agents for lead generation, customer support, and appointment booking.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/sign-up" className="bg-black text-white px-8 py-3 rounded-lg text-sm font-medium hover:bg-gray-800">
            Start for free
          </Link>
          <Link href="/sign-in" className="border border-gray-200 text-gray-700 px-8 py-3 rounded-lg text-sm font-medium hover:border-gray-400">
            Sign in
          </Link>
        </div>
        <div className="mt-24 grid grid-cols-3 gap-8 text-left">
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="text-2xl mb-3">🎙️</div>
            <h3 className="font-semibold text-gray-900 mb-2">Voice Agents</h3>
            <p className="text-gray-500 text-sm">Create AI agents that can hold natural phone conversations with your customers.</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="text-2xl mb-3">📞</div>
            <h3 className="font-semibold text-gray-900 mb-2">Twilio Integration</h3>
            <p className="text-gray-500 text-sm">Connect real phone numbers and start making and receiving calls instantly.</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="text-2xl mb-3">🏢</div>
            <h3 className="font-semibold text-gray-900 mb-2">Multi-tenant</h3>
            <p className="text-gray-500 text-sm">Built for teams. Each organization gets their own isolated workspace.</p>
          </div>
        </div>
      </main>
    </div>
  );
}