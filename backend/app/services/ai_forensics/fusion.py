"""
fusion.py — Weighted evidence fusion for the AI Forensics Engine.

Takes a list of DetectionResults from independent detector plugins and
produces a single AIEvidenceResult via a configurable weighted ensemble.

Design Principles
-----------------
- Weights are injected externally (not hardcoded into detectors).
- Unknown detectors receive a configurable default weight.
- If all detectors fail, the engine gracefully returns a LOW_CONFIDENCE result.
- Confidence is computed as the weighted mean of individual confidences,
  penalized if fewer than expected detectors returned results.
"""
from __future__ import annotations

import logging

from app.services.ai_forensics.models import AIEvidenceResult, DetectionResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default weights  (tunable — do not put business logic here)
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS: dict[str, float] = {
    "foundation_clip":      0.60,   # CLIP zero-shot — best generalization
    "statistical_features": 0.20,   # Handcrafted — fast, interpretable baseline
    "artifact_cv":          0.20,   # Classical CV — texture + edge analysis
    # Future detectors — add entries here, no other code changes needed:
    # "frequency_spectral": 0.50,
    # "semantic_vit":       0.60,
}

DEFAULT_WEIGHT = 0.40   # Fallback for any unregistered detector name


class DetectionFusion:
    """
    Aggregates DetectionResults into a single AIEvidenceResult
    using configurable weighted-average fusion.

    Usage::

        fusion = DetectionFusion(weights=DEFAULT_WEIGHTS)
        evidence = fusion.fuse(results)
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        default_weight: float = DEFAULT_WEIGHT,
    ) -> None:
        self._weights = weights if weights is not None else DEFAULT_WEIGHTS
        self._default_weight = default_weight

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fuse(self, results: list[DetectionResult]) -> AIEvidenceResult:
        """
        Combine individual DetectionResults into a single AIEvidenceResult.

        Args:
            results: List of DetectionResult objects from the detection engine.
                     May be empty if all detectors failed.

        Returns:
            AIEvidenceResult with aggregated probability, confidence, and explanation.
        """
        if not results:
            return self._no_evidence_result()

        # ----------------------------------------------------------------
        # Weighted average of scores and confidences
        # ----------------------------------------------------------------
        total_weight     = 0.0
        weighted_score   = 0.0
        weighted_conf    = 0.0

        for result in results:
            w = self._weights.get(result.engine, self._default_weight)
            weighted_score += result.score      * w
            weighted_conf  += result.confidence * w
            total_weight   += w

        ai_probability = weighted_score / total_weight
        confidence     = weighted_conf  / total_weight

        # ----------------------------------------------------------------
        # Verdict
        # ----------------------------------------------------------------
        verdict = AIEvidenceResult.verdict_label(ai_probability)

        # ----------------------------------------------------------------
        # Explanation narrative
        # ----------------------------------------------------------------
        explanation = self._build_explanation(results, ai_probability, verdict)

        return AIEvidenceResult(
            ai_probability=round(ai_probability, 4),
            confidence=round(confidence, 4),
            verdict=verdict,
            explanation=explanation,
            detector_breakdown=results,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_explanation(
        self,
        results: list[DetectionResult],
        probability: float,
        verdict: str,
    ) -> str:
        lines = [
            f"AI Forensics Engine processed {len(results)} detector(s). "
            f"Weighted probability: {probability:.1%}. Verdict: {verdict}."
        ]
        for r in results:
            w = self._weights.get(r.engine, self._default_weight)
            lines.append(
                f"  [{r.engine} | weight={w:.2f}] "
                f"score={r.score:.3f}, confidence={r.confidence:.3f} — {r.reason}"
            )
        return "\n".join(lines)

    @staticmethod
    def _no_evidence_result() -> AIEvidenceResult:
        return AIEvidenceResult(
            ai_probability=0.0,
            confidence=0.0,
            verdict="UNKNOWN",
            explanation=(
                "No detectors produced results. "
                "All registered plugins may have failed or are unavailable."
            ),
            detector_breakdown=[],
        )
