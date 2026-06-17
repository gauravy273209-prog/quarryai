import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import SignOutButton from "@/app/components/SignOutButton";
import SidebarNav from "@/app/components/SidebarNav";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-60 bg-[#0f1117] flex flex-col fixed h-full z-10 border-r border-white/5">
        <div className="px-5 py-5 border-b border-white/5">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
              <span className="text-white text-sm font-bold">Q</span>
            </div>
            <span className="text-white font-bold text-lg tracking-tight">QuarryAI</span>
          </div>
        </div>
        <SidebarNav />
        <div className="px-3 py-4 border-t border-white/5">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg">
            <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-violet-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">G</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-xs font-medium truncate">Gaurav</p>
              <p className="text-gray-500 text-xs truncate">Free Plan</p>
            </div>
          </div>
          <div className="px-3 mt-1">
            <SignOutButton />
          </div>
        </div>
      </aside>
      <main className="flex-1 ml-60">
        {children}
      </main>
    </div>
  );
}