"""
schemas/verification.py — API I/O contracts for the verification engine.
"""

from pydantic import BaseModel, Field


class VerifyResponse(BaseModel):
    """Response from POST /api/verify."""

    status:           str   = Field(..., examples=["verified"])
    media_id:         str   = Field(..., examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    model_name:       str   = Field(..., examples=["Stable Diffusion XL"])
    timestamp:        str   = Field(..., examples=["2026-07-02T08:00:00+00:00"])
    media_type:       str   = Field(..., examples=["image"])
    framework:        str   = Field(..., examples=["Aletheia"])
    strategy:         str   = Field(..., examples=["sequential_lsb"])
    uploaded_phash:   str   = Field(..., examples=["a3b4c5d6e7f80192"])
    stored_phash:     str   = Field(..., examples=["a3b4c5d6e7f80192"])
    hamming_distance: int   = Field(..., examples=[3])
    similarity:       float = Field(..., examples=[98.43])
    verification:     str   = Field(
        ...,
        description="AUTHENTIC | MINOR MODIFICATION | MODIFIED | UNVERIFIED",
        examples=["AUTHENTIC"],
    )
