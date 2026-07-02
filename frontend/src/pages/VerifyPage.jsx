/**
 * VerifyPage — Sprint 4 standalone verification page.
 *
 * Workflow:
 *   1. User uploads an embedded PNG.
 *   2. verifyMedia() is called (POST /api/verify).
 *   3. VerificationReport is displayed.
 *
 * No business logic lives here — all verification is server-side.
 */

import { useState, useRef } from "react";
import { UploadCloud, ShieldCheck, Loader2, AlertCircle, RefreshCw, FileImage } from "lucide-react";
import VerificationReport from "../components/VerificationReport";
import { verifyMedia } from "../services/api";

/* ── Drop zone ───────────────────────────────────────── */
function VerifyDropZone({ file, onFile }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const accept = (f) => {
    if (f && f.type.startsWith("image/")) onFile(f);
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); accept(e.dataTransfer.files[0]); }}
      className={`relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed
        cursor-pointer transition-all duration-200 py-10 px-6
        ${dragging
          ? "border-violet-400 bg-violet-500/10"
          : file
          ? "border-emerald-500/40 bg-emerald-500/5"
          : "border-white/10 hover:border-white/20 bg-white/[0.02] hover:bg-white/[0.04]"
        }`}
    >
      <input ref={inputRef} type="file" accept="image/*" className="hidden"
        onChange={(e) => accept(e.target.files?.[0])} />

      {file ? (
        <>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <FileImage className="w-6 h-6 text-emerald-400" strokeWidth={1.5} />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-slate-200">{file.name}</p>
            <p className="text-xs text-slate-500 mt-0.5">{(file.size / 1024).toFixed(1)} KB — click to change</p>
          </div>
        </>
      ) : (
        <>
          <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
            <UploadCloud className="w-6 h-6 text-violet-400" strokeWidth={1.5} />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-slate-300">Drop embedded PNG here</p>
            <p className="text-xs text-slate-500 mt-0.5">or click to browse — must be an Aletheia-embedded image</p>
          </div>
        </>
      )}
    </div>
  );
}

/* ── Page ────────────────────────────────────────────── */
export default function VerifyPage() {
  const [file,    setFile]    = useState(null);
  const [phase,   setPhase]   = useState("idle");   // idle | loading | success | error
  const [report,  setReport]  = useState(null);
  const [error,   setError]   = useState("");

  const handleVerify = async () => {
    if (!file) return;
    setPhase("loading");
    setError("");
    try {
      const data = await verifyMedia(file);
      setReport(data);
      setPhase("success");
    } catch (err) {
      const detail = err.response?.data?.detail ?? err.message ?? "Verification failed.";
      setError(typeof detail === "string" ? detail : JSON.stringify(detail));
      setPhase("error");
    }
  };

  const handleReset = () => {
    setFile(null);
    setPhase("idle");
    setReport(null);
    setError("");
  };

  return (
    <main className="min-h-[calc(100vh-64px)] flex flex-col">

      {/* ── Page header ── */}
      <section className="pt-12 pb-8 px-6 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-600/10 border border-violet-500/20 mb-5">
          <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
          <span className="text-violet-400 text-xs font-semibold tracking-widest uppercase">
            Sprint 4 · Verification Engine
          </span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
          Provenance{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
            Verification
          </span>
        </h1>

        <p className="mt-3 text-lg text-slate-500 font-medium tracking-wide">
          Perceptual Hash Integrity Engine
        </p>
        <p className="mt-3 max-w-lg mx-auto text-sm text-slate-600 leading-relaxed">
          Upload an Aletheia-embedded image. The engine extracts the MIR,
          generates a perceptual hash, and compares it against the stored
          registry fingerprint to produce a verification report.
        </p>
      </section>

      {/* ── Main card ── */}
      <section className="flex-1 flex items-start justify-center px-4 pb-16">
        <div className="w-full max-w-xl glass-card p-8">

          {phase === "success" && report ? (
            <div className="space-y-6">
              <VerificationReport report={report} />
              <button onClick={handleReset} className="btn-primary w-full">
                <RefreshCw className="w-4 h-4" />
                Verify Another Image
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <VerifyDropZone file={file} onFile={setFile} />

              {/* Error */}
              {phase === "error" && (
                <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                  <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                  <p className="text-sm text-red-300 leading-relaxed">{error}</p>
                </div>
              )}

              {/* Verify button */}
              <button
                id="verify-submit-btn"
                onClick={handleVerify}
                disabled={!file || phase === "loading"}
                className="btn-primary w-full text-base py-3.5 bg-violet-600 hover:bg-violet-500
                           shadow-violet-900/40 hover:shadow-violet-600/30
                           disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {phase === "loading" ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Verifying…
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-5 h-5" />
                    Verify Provenance
                  </>
                )}
              </button>

              {!file && (
                <p className="text-center text-xs text-slate-600">
                  Upload an Aletheia-embedded PNG to begin verification.
                </p>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
