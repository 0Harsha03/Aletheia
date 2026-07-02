"""
verification_service.py — Complete provenance verification workflow.

Pipeline (Sprint 4):
  1. Extract MIR from uploaded image (reuses Sprint 3 extraction pipeline).
  2. Generate pHash of the uploaded image.
  3. Retrieve stored registration record by media_id.
  4. Retrieve stored pHash (written by embedding service at embed time).
  5. Compute Hamming Distance.
  6. Compute similarity percentage and verdict.
  7. Return VerificationResult.

Sprint 5 extension points:
  - Add AES decryption of the embedded payload before step 1.
  - Add digital signature verification after step 3.
  - Extend VerificationResult with integrity_score, confidence, heatmap paths.
  None of those require modifying the existing pipeline steps.
"""

from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
from fastapi import HTTPException

from app.services.extraction import (
    ExtractionError,
    read_payload_bitstream,
    bits_to_bytes,
    deserialize,
)
from app.services.verification.phash_service import generate_phash
from app.services.verification.hamming_distance import (
    compute_hamming_distance,
    compute_similarity,
    get_verification_verdict,
    VERDICT_AUTHENTIC,
    VERDICT_MINOR_MODIFICATION,
)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class VerificationResult:
    """Structured output of the verification pipeline."""

    status:           str    # "verified" | "unverified"
    media_id:         str
    model_name:       str
    timestamp:        str
    media_type:       str
    framework:        str
    strategy:         str
    uploaded_phash:   str
    stored_phash:     str
    hamming_distance: int
    similarity:       float
    verification:     str    # AUTHENTIC | MINOR MODIFICATION | MODIFIED | UNVERIFIED


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------

async def verify_provenance(image: Image.Image, db) -> VerificationResult:
    """
    Execute the full provenance verification pipeline.

    Args:
        image: PIL Image of the uploaded (potentially embedded) media asset.
        db:    Motor database instance.

    Returns:
        VerificationResult.

    Raises:
        HTTPException 422: If no valid MIR is recoverable from the image.
        HTTPException 404: If the recovered media_id has no registry entry.
        HTTPException 422: If the registry entry has no stored pHash.
        HTTPException 500: For unexpected processing failures.
    """

    # ------------------------------------------------------------------
    # 1. Extract MIR using Sprint 3 pipeline (unchanged)
    # ------------------------------------------------------------------
    try:
        n_bytes, payload_bits = read_payload_bitstream(image)
        payload_bytes = bits_to_bytes(payload_bits)
        mir = deserialize(payload_bytes)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"MIR extraction failed — this image may not contain "
                   f"Aletheia provenance data. Details: {exc}",
        ) from exc

    # ------------------------------------------------------------------
    # 2. Generate pHash of the uploaded image
    # ------------------------------------------------------------------
    try:
        uploaded_phash = generate_phash(image)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ------------------------------------------------------------------
    # 3. Retrieve stored registration record
    # ------------------------------------------------------------------
    doc = await db["registered_media"].find_one({"image_id": mir.media_id})
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No Aletheia registration found for media_id='{mir.media_id}'. "
                "The image may have been registered on a different instance."
            ),
        )

    stored_phash: str | None = doc.get("phash")
    if not stored_phash:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No pHash stored for media_id='{mir.media_id}'. "
                "Re-embed the image to generate and store the perceptual hash."
            ),
        )

    strategy: str = doc.get("embedding_strategy", "sequential_lsb")

    # ------------------------------------------------------------------
    # 4. Compute Hamming Distance
    # ------------------------------------------------------------------
    try:
        distance = compute_hamming_distance(stored_phash, uploaded_phash)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ------------------------------------------------------------------
    # 5. Similarity + verdict
    # ------------------------------------------------------------------
    similarity = compute_similarity(distance)
    verdict    = get_verification_verdict(distance)

    overall_status = (
        "verified"
        if verdict in (VERDICT_AUTHENTIC, VERDICT_MINOR_MODIFICATION)
        else "unverified"
    )

    # ------------------------------------------------------------------
    # 6. Return result
    # ------------------------------------------------------------------
    return VerificationResult(
        status=overall_status,
        media_id=mir.media_id,
        model_name=mir.model_name,
        timestamp=mir.timestamp,
        media_type=mir.media_type,
        framework=mir.framework,
        strategy=strategy,
        uploaded_phash=uploaded_phash,
        stored_phash=stored_phash,
        hamming_distance=distance,
        similarity=similarity,
        verification=verdict,
    )
