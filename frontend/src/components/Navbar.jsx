/**
 * Navbar — top bar with the Aletheia brand identity.
 */

import { ShieldCheck } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-surface-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-brand-400" strokeWidth={1.8} />
          </div>
          <div>
            <span className="text-slate-100 font-bold text-lg tracking-tight">Aletheia</span>
            <span className="ml-2 text-slate-500 text-xs font-medium hidden sm:inline">
              AI Media Provenance Framework
            </span>
          </div>
        </div>

        {/* Status pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />
          <span className="text-emerald-400 text-xs font-semibold tracking-wide hidden sm:inline">
            Registration Engine Active
          </span>
          <span className="text-emerald-400 text-xs font-semibold tracking-wide sm:hidden">
            v1.0
          </span>
        </div>
      </div>
    </header>
  );
}
