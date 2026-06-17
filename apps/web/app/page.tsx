import Link from "next/link";

export default function HomePage() {
  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#f1f5f9", fontFamily: "Inter, sans-serif" }}>

      {/* Nav */}
      <nav style={{ padding: "16px 32px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e2433" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, #6366f1, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 700, color: "#fff" }}>Q</div>
          <span style={{ fontWeight: 700, fontSize: 16, color: "#f1f5f9" }}>QuarryAI</span>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <Link href="/sign-in" style={{ color: "#94a3b8", fontSize: 14, textDecoration: "none" }}>Sign in</Link>
          <Link href="/sign-up" style={{ background: "#6366f1", color: "#fff", fontSize: 14, padding: "8px 18px", borderRadius: 8, textDecoration: "none", fontWeight: 500 }}>Get started</Link>
        </div>
      </nav>

      {/* Hero */}
      <main style={{ maxWidth: 800, margin: "0 auto", padding: "96px 32px 64px", textAlign: "center" }}>
        <div style={{ display: "inline-block", background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.3)", color: "#a5b4fc", fontSize: 12, padding: "4px 14px", borderRadius: 20, marginBottom: 24, fontWeight: 500 }}>
          AI Voice Agent Platform
        </div>
        <h1 style={{ fontSize: 52, fontWeight: 800, lineHeight: 1.1, marginBottom: 20, color: "#f1f5f9", letterSpacing: "-0.02em" }}>
          Build Voice AI Agents<br />
          <span style={{ background: "linear-gradient(135deg, #6366f1, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>in Minutes</span>
        </h1>
        <p style={{ fontSize: 18, color: "#64748b", marginBottom: 40, maxWidth: 560, margin: "0 auto 40px", lineHeight: 1.6 }}>
          QuarryAI lets you create, deploy, and manage AI voice agents for lead generation, customer support, and appointment booking.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <Link href="/sign-up" style={{ background: "#6366f1", color: "#fff", padding: "12px 28px", borderRadius: 10, fontSize: 15, fontWeight: 600, textDecoration: "none" }}>
            Start for free →
          </Link>
          <Link href="/sign-in" style={{ background: "transparent", color: "#94a3b8", padding: "12px 28px", borderRadius: 10, fontSize: 15, border: "1px solid #2d3748", textDecoration: "none" }}>
            Sign in
          </Link>
        </div>

        {/* Feature Cards */}
        <div style={{ marginTop: 80, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, textAlign: "left" }}>
          {[
            { icon: "🎙️", title: "Voice Agents", desc: "Create AI agents that hold natural phone conversations with your customers using Deepgram + Groq." },
            { icon: "📞", title: "Twilio Integration", desc: "Connect real phone numbers and start making and receiving calls instantly. 66% cheaper than Vapi." },
            { icon: "📊", title: "Analytics", desc: "Track call history, duration, transcripts, and agent performance from your dashboard." },
          ].map((f) => (
            <div key={f.title} style={{ background: "#1a1d27", border: "1px solid #2d3748", borderRadius: 12, padding: "24px" }}>
              <div style={{ fontSize: 28, marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ margin: "0 0 8px", fontWeight: 600, color: "#f1f5f9", fontSize: 15 }}>{f.title}</h3>
              <p style={{ margin: 0, color: "#64748b", fontSize: 13, lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Pricing */}
        <div style={{ marginTop: 80 }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, color: "#f1f5f9", marginBottom: 8 }}>Simple Pricing</h2>
          <p style={{ color: "#64748b", marginBottom: 40, fontSize: 15 }}>66% cheaper than Vapi. You own every line of it.</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, textAlign: "left" }}>
            {[
              { plan: "Starter", price: "₹2,999", minutes: "500 min/mo", color: "#2d3748" },
              { plan: "Pro", price: "₹7,999", minutes: "2,000 min/mo", color: "#6366f1", highlight: true },
              { plan: "Business", price: "₹29,999", minutes: "10,000 min/mo", color: "#2d3748" },
            ].map((p) => (
              <div key={p.plan} style={{
                background: p.highlight ? "rgba(99,102,241,0.1)" : "#1a1d27",
                border: "1px solid " + (p.highlight ? "#6366f1" : "#2d3748"),
                borderRadius: 12, padding: "24px",
              }}>
                <p style={{ margin: "0 0 4px", color: "#94a3b8", fontSize: 13 }}>{p.plan}</p>
                <p style={{ margin: "0 0 4px", fontSize: 28, fontWeight: 700, color: "#f1f5f9" }}>{p.price}</p>
                <p style={{ margin: "0 0 20px", color: "#64748b", fontSize: 13 }}>{p.minutes}</p>
                <Link href="/sign-up" style={{
                  display: "block", textAlign: "center",
                  background: p.highlight ? "#6366f1" : "transparent",
                  color: p.highlight ? "#fff" : "#6366f1",
                  border: "1px solid #6366f1",
                  padding: "8px", borderRadius: 8, fontSize: 13, fontWeight: 500, textDecoration: "none",
                }}>
                  Get started
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Footer CTA */}
        <div style={{ marginTop: 80, padding: "48px 32px", background: "#1a1d27", border: "1px solid #2d3748", borderRadius: 16 }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, color: "#f1f5f9", marginBottom: 12 }}>Ready to go live?</h2>
          <p style={{ color: "#64748b", marginBottom: 28 }}>Join QuarryAI and own your Voice AI stack.</p>
          <Link href="/sign-up" style={{ background: "#6366f1", color: "#fff", padding: "12px 32px", borderRadius: 10, fontSize: 15, fontWeight: 600, textDecoration: "none" }}>
            Start for free →
          </Link>
        </div>
      </main>
    </div>
  );
}