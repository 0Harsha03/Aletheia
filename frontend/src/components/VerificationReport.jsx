/**
 * VerificationReport — Sprint 4 UI component.
 *
 * Displays the full provenance verification report returned by POST /api/verify.
 * Status card color is determined by the verification verdict:
 *   AUTHENTIC          → emerald (green)
 *   MINOR MODIFICATION → amber  (yellow)
 *   MODIFIED           → orange
 *   UNVERIFIED         → red
 */

import { ShieldCheck, ShieldAlert, ShieldX, Hash, Cpu, Clock, Layers, Fingerprint, Binary, Activity } from "lucide-react";

/* ── Verdict color mapping ───────────────────────────── */
const VERDICT_STYLES = {
  "AUTHENTIC":          { ring: "border-emerald-500/40", bg: "bg-emerald-500/10", icon: ShieldCheck, iconColor: "text-emerald-400", textColor: "text-emerald-300", badge: "bg-emerald-500/20 border-emerald-500/30 text-emerald-300" },
  "MINOR MODIFICATION": { ring: "border-amber-500/40",   bg: "bg-amber-500/10",   icon: ShieldAlert, iconColor: "text-amber-400",   textColor: "text-amber-300",   badge: "bg-amber-500/20 border-amber-500/30 text-amber-300" },
  "MODIFIED":           { ring: "border-orange-500/40",  bg: "bg-orange-500/10",  icon: ShieldAlert, iconColor: "text-orange-400",  textColor: "text-orange-300",  badge: "bg-orange-500/20 border-orange-500/30 text-orange-300" },
  "UNVERIFIED":         { ring: "border-red-500/40",     bg: "bg-red-500/10",     icon: ShieldX,     iconColor: "text-red-400",     textColor: "text-red-300",     badge: "bg-red-500/20 border-red-500/30 text-red-300" },
};

/* ── Detail row ──────────────────────────────────────── */
function DetailRow({ icon: Icon, label, value, mono = false }) {
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-white/[0.04] last:border-0">
      <div className="w-7 h-7 rounded-md bg-white/[0.04] border border-white/[0.06] flex items-center justify-center shrink-0 mt-0.5">
        <Icon className="w-3.5 h-3.5 text-slate-400" strokeWidth={1.8} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest mb-0.5">{label}</p>
        <p className={`text-sm leading-snug break-all ${mono ? "font-mono text-slate-300" : "font-medium text-slate-200"}`}>{value}</p>
      </div>
    </div>
  );
}

/* ── Similarity bar ──────────────────────────────────── */
function SimilarityBar({ similarity, style }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-500 font-medium">Similarity</span>
        <span className={`font-bold ${style.textColor}`}>{similarity}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/[0.05] overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${style.bg.replace("/10", "/60")}`}
          style={{ width: `${similarity}%` }}
        />
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────── */
export default function VerificationReport({ report }) {
  const style = VERDICT_STYLES[report.verification] ?? VERDICT_STYLES["UNVERIFIED"];
  const StatusIcon = style.icon;

  return (
    <div className="animate-slide-up space-y-5">

      {/* ── Status card ── */}
      <div className={`p-5 rounded-2xl border ${style.ring} ${style.bg}`}>
        <div className="flex items-center gap-4">
          <div className={`w-14 h-14 rounded-xl border ${style.ring} ${style.bg} flex items-center justify-center shrink-0`}>
            <StatusIcon className={`w-7 h-7 ${style.iconColor}`} strokeWidth={1.5} />
          </div>
          <div>
            <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-bold uppercase tracking-wider mb-1 ${style.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${style.iconColor.replace("text-", "bg-")}`} />
              {report.verification}
            </div>
            <p className="text-slate-400 text-sm leading-snug">
              {report.verification === "AUTHENTIC" && "MIR extracted successfully. pHash matches within tolerance."}
              {report.verification === "MINOR MODIFICATION" && "MIR recovered. Minor perceptual difference detected."}
              {report.verification === "MODIFIED" && "MIR recovered, but significant modification detected."}
              {report.verification === "UNVERIFIED" && "Image has been substantially altered or does not match registry."}
            </p>
          </div>
        </div>
      </div>

      {/* ── Similarity + Hamming ── */}
      <div className="glass-card px-5 py-4 space-y-4">
        <SimilarityBar similarity={report.similarity} style={style} />
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">Hamming Distance</span>
          <span className="font-mono font-bold text-slate-300">
            {report.hamming_distance} / 64 bits
          </span>
        </div>
      </div>

      {/* ── MIR details ── */}
      <div className="glass-card px-5 py-1">
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest pt-3 pb-1">
          Recovered Media Identity Record
        </p>
        <DetailRow icon={Hash}        label="Media ID"   value={report.media_id}   mono />
        <DetailRow icon={Cpu}         label="AI Model"   value={report.model_name} />
        <DetailRow icon={Clock}       label="Timestamp"  value={new Date(report.timestamp).toLocaleString("en-GB", { timeZone: "UTC", dateStyle: "long", timeStyle: "long" })} />
        <DetailRow icon={Layers}      label="Media Type" value={report.media_type} />
        <DetailRow icon={Activity}    label="Strategy"   value={report.strategy}   mono />
      </div>

      {/* ── pHash comparison ── */}
      <div className="glass-card px-5 py-1">
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest pt-3 pb-1">
          Perceptual Hash (pHash)
        </p>
        <DetailRow icon={Fingerprint} label="Stored pHash (at embed time)" value={report.stored_phash}   mono />
        <DetailRow icon={Binary}      label="Uploaded pHash (this image)"  value={report.uploaded_phash} mono />
      </div>

    </div>
  );
}
