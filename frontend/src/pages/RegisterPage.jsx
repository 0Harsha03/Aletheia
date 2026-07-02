/**
 * RegisterPage — the single page of the Media Registration Engine.
 *
 * Orchestrates: UploadZone → ModelSelector → Register button → RegistrationSuccess
 */

import { useState } from "react";
import { ArrowDown, Loader2, AlertCircle, ShieldPlus } from "lucide-react";

import UploadZone from "../components/UploadZone";
import ModelSelector from "../components/ModelSelector";
import RegistrationSuccess from "../components/RegistrationSuccess";
import { registerMedia } from "../services/api";

/* ── Step indicator ─────────────────────────────────────── */
function Step({ number, label, active }) {
  return (
    <div className={`flex items-center gap-2 ${active ? "opacity-100" : "opacity-30"}`}>
      <span
        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border
          ${active ? "bg-brand-600 border-brand-500 text-white" : "bg-surface-800 border-white/10 text-slate-500"}`}
      >
        {number}
      </span>
      <span className={`text-xs font-medium hidden sm:inline ${active ? "text-slate-300" : "text-slate-600"}`}>
        {label}
      </span>
    </div>
  );
}

function StepDivider() {
  return <div className="hidden sm:block h-px w-8 bg-white/10 mx-1" />;
}

/* ── Main page ──────────────────────────────────────────── */
export default function RegisterPage() {
  const [file, setFile] = useState(null);
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const canSubmit = file && model && !loading;

  const handleRegister = async () => {
    if (!canSubmit) return;
    setLoading(true);
    setError("");
    try {
      const data = await registerMedia(file, model);
      setResult(data.metadata);
    } catch (err) {
      const detail =
        err.response?.data?.detail ??
        err.message ??
        "An unexpected error occurred. Please try again.";
      setError(typeof detail === "string" ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setModel("");
    setError("");
    setResult(null);
  };

  /* Current active step:
     1 = upload, 2 = model select, 3 = register, 4 = embed, 5 = verify
     After registration we jump to step 4 (embed panel shown in success view) */
  const activeStep = result ? 4 : model ? 3 : file ? 2 : 1;

  return (
    <main className="min-h-[calc(100vh-64px)] flex flex-col">
      {/* ── Page header ── */}
      <section className="pt-12 pb-8 px-6 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-600/10 border border-brand-500/20 mb-5">
          <ShieldPlus className="w-3.5 h-3.5 text-brand-400" />
          <span className="text-brand-400 text-xs font-semibold tracking-widest uppercase">
            Sprint 1, 2 &amp; 3
          </span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
          AI Media{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-indigo-400">
            Provenance Framework
          </span>
        </h1>

        <p className="mt-3 text-lg text-slate-500 font-medium tracking-wide">
          Registration, Embedding &amp; Provenance Extraction
        </p>

        <p className="mt-3 max-w-xl mx-auto text-sm text-slate-600 leading-relaxed">
          Register AI-generated media, embed a Media Identity Record (MIR) via
          LSB steganography, then extract and verify the recovered MIR.
        </p>

        {/* Step progress */}
        <div className="flex items-center justify-center gap-1 mt-6 flex-wrap">
          <Step number={1} label="Upload Image"    active={activeStep >= 1} />
          <StepDivider />
          <ArrowDown className="w-3 h-3 text-slate-700 rotate-[-90deg] shrink-0" />
          <StepDivider />
          <Step number={2} label="Select AI Model" active={activeStep >= 2} />
          <StepDivider />
          <ArrowDown className="w-3 h-3 text-slate-700 rotate-[-90deg] shrink-0" />
          <StepDivider />
          <Step number={3} label="Register"        active={activeStep >= 3} />
          <StepDivider />
          <ArrowDown className="w-3 h-3 text-slate-700 rotate-[-90deg] shrink-0" />
          <StepDivider />
          <Step number={4} label="Embed Provenance" active={activeStep >= 4} />
          <StepDivider />
          <ArrowDown className="w-3 h-3 text-slate-700 rotate-[-90deg] shrink-0" />
          <StepDivider />
          <Step number={5} label="Verify" active={activeStep >= 5} />
        </div>
      </section>

      {/* ── Main card ── */}
      <section className="flex-1 flex items-start justify-center px-4 pb-16">
        <div className="w-full max-w-xl glass-card p-8">
          {result ? (
            /* ── Success state ── */
            <RegistrationSuccess metadata={result} onReset={handleReset} />
          ) : (
            /* ── Registration form ── */
            <div className="space-y-7">
              {/* 1 — Upload */}
              <UploadZone file={file} onFile={setFile} />

              {/* Divider */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-white/[0.05]" />
                <ArrowDown className="w-4 h-4 text-slate-600 shrink-0" />
                <div className="flex-1 h-px bg-white/[0.05]" />
              </div>

              {/* 2 — Model */}
              <ModelSelector value={model} onChange={setModel} />

              {/* Divider */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-white/[0.05]" />
                <ArrowDown className="w-4 h-4 text-slate-600 shrink-0" />
                <div className="flex-1 h-px bg-white/[0.05]" />
              </div>

              {/* Error */}
              {error && (
                <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 animate-fade-in">
                  <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                  <p className="text-sm text-red-300 leading-relaxed">{error}</p>
                </div>
              )}

              {/* 3 — Register button */}
              <button
                id="register-btn"
                onClick={handleRegister}
                disabled={!canSubmit}
                className="btn-primary w-full text-base py-3.5"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Registering…
                  </>
                ) : (
                  <>
                    <ShieldPlus className="w-5 h-5" />
                    Register Media
                  </>
                )}
              </button>

              {/* Hint */}
              {(!file || !model) && (
                <p className="text-center text-xs text-slate-600">
                  {!file && !model
                    ? "Upload an image and select a model to continue."
                    : !file
                    ? "Upload an image to continue."
                    : "Select an AI model to continue."}
                </p>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
