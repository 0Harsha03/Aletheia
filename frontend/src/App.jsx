/**
 * App.jsx — root component.
 *
 * Sprint 4: adds tab-based navigation.
 *   "Register & Embed" → RegisterPage (Sprints 1-3)
 *   "Verify Media"     → VerifyPage   (Sprint 4)
 *
 * Uses local state (no router dependency) — the app is single-page.
 */

import { useState } from "react";
import { ShieldPlus, ShieldCheck } from "lucide-react";
import Navbar from "./components/Navbar";
import RegisterPage from "./pages/RegisterPage";
import VerifyPage from "./pages/VerifyPage";

const TABS = [
  { id: "register", label: "Register & Embed", icon: ShieldPlus },
  { id: "verify",   label: "Verify Media",     icon: ShieldCheck },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("register");

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      {/* ── Tab switcher ── */}
      <div className="flex items-center justify-center gap-1 pt-6 px-4">
        {TABS.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              id={`tab-${id}`}
              onClick={() => setActiveTab(id)}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold
                          transition-all duration-200 focus:outline-none
                          ${active
                            ? "bg-white/[0.08] border border-white/[0.12] text-slate-100 shadow-lg"
                            : "text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]"
                          }`}
            >
              <Icon className={`w-4 h-4 ${active ? "text-brand-400" : ""}`} strokeWidth={1.8} />
              {label}
            </button>
          );
        })}
      </div>

      {/* ── Page content ── */}
      {activeTab === "register" ? <RegisterPage /> : <VerifyPage />}
    </div>
  );
}
