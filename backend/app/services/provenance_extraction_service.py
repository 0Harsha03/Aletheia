"""
provenance_extraction_service.py — Orchestrates the full provenance extraction pipeline.

Responsibilities:
  1. Accept a PIL Image (already opened by the route handler).
  2. Read the LSB bitstream (header + payload bits).
  3. Decode payload bits back into bytes.
  4. Deserialise bytes into a MediaIdentityRecord.
  5. Determine which embedding strategy was used (from DB or heuristic).
  6. Return a structured ExtractionResult.

Design:
    The extraction pipeline is intentionally strategy-agnostic at this layer.
    Sprint 4 can add:
      - A strategy-detection step (e.g. check for ADPE watermark in first region).
      - Region-specific extraction for distributed payloads.
      - pHash / Hamming integrity comparison.
    None of those changes will require modifying the route or schemas.
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
from app.services.embedding.mir_serializer import MediaIdentityRecord


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExtractionResult:
    """Structured return value from extract_provenance()."""

    mir: MediaIdentityRecord
    """The recovered Media Identity Record."""

    strategy_used: str
    """Name of the embedding strategy detected (or inferred)."""

    n_payload_bytes: int
    """Number of payload bytes recovered from the image."""

    success: bool = True


# ---------------------------------------------------------------------------
# Strategy detection heuristic
# ---------------------------------------------------------------------------

def _detect_strategy(image: Image.Image, db_strategy: str | None) -> str:
    """
    Determine the embedding strategy used.

    Priority:
      1. If the MongoDB document has a stored strategy name, use it.
      2. Otherwise fall back to "sequential_lsb" (the Sprint 2 default).

    Sprint 4 can extend this to inspect image metadata or perform a
    region-scan to distinguish LSB from ADPE.

    Args:
        image:       The carrier image (may be used for heuristics later).
        db_strategy: Strategy name stored in MongoDB, or None.

    Returns:
        str — strategy identifier for the API response.
    """
    if db_strategy:
        return db_strategy
    return "sequential_lsb"


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------

async def extract_provenance(
    image: Image.Image,
    db=None,
) -> ExtractionResult:
    """
    Execute the full provenance extraction pipeline.

    Args:
        image: A PIL Image object (the embedded carrier).
        db:    Optional Motor database (used to look up stored strategy metadata).
               If None, strategy is inferred from heuristics.

    Returns:
        ExtractionResult with the recovered MIR, strategy name, and byte count.

    Raises:
        HTTPException 422: If no valid provenance data is found in the image.
        HTTPException 500: For unexpected processing errors.
    """

    # ------------------------------------------------------------------
    # 1. Read LSB bitstream (header + payload)
    # ------------------------------------------------------------------
    try:
        n_payload_bytes, payload_bits = read_payload_bitstream(image)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Provenance extraction failed: {exc}",
        ) from exc

    # ------------------------------------------------------------------
    # 2. Decode payload bits → bytes
    # ------------------------------------------------------------------
    try:
        payload_bytes = bits_to_bytes(payload_bits)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Bit decoding failed: {exc}",
        ) from exc

    # ------------------------------------------------------------------
    # 3. Deserialise bytes → MediaIdentityRecord
    # ------------------------------------------------------------------
    try:
        mir = deserialize(payload_bytes)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"MIR deserialization failed: {exc}",
        ) from exc

    # ------------------------------------------------------------------
    # 4. Determine embedding strategy
    #    Optionally look up the media_id in MongoDB for richer metadata.
    # ------------------------------------------------------------------
    db_strategy = None
    if db is not None:
        try:
            doc = await db["registered_media"].find_one({"image_id": mir.media_id})
            if doc:
                db_strategy = doc.get("embedding_strategy")
        except Exception:
            pass  # Non-fatal: strategy lookup failure does not block extraction

    strategy_used = _detect_strategy(image, db_strategy)

    # ------------------------------------------------------------------
    # 5. Return structured result
    # ------------------------------------------------------------------
    return ExtractionResult(
        mir=mir,
        strategy_used=strategy_used,
        n_payload_bytes=n_payload_bytes,
        success=True,
    )
