"""
bitstream_reader.py — Reads LSB-embedded bits from a carrier image.

This is the primary entry point for the extraction pipeline.
It is the exact inverse of lsb_strategy.py's embed() operation.

Protocol (mirrors binary_encoder.py):
    ┌──────────────────────────────┬──────────────────────────────────────────┐
    │  32-bit length header        │  Payload bits                            │
    │  (big-endian, MSB first)     │  (each byte → 8 bits, MSB first)        │
    │  = number of PAYLOAD bytes   │  len(data) × 8 bits                     │
    └──────────────────────────────┴──────────────────────────────────────────┘

Extraction reads exactly:
    32 bits  (header)  +  header_value × 8 bits  (payload)

Design notes:
    - Works for any image embedded with a strategy that uses sequential LSB
      in row-major order (currently LSBStrategy and ADPEStrategy v1).
    - Sprint 4 region-specific extraction can call read_raw_lsbs() directly,
      specifying an offset and bit count per region.
"""

from __future__ import annotations

from PIL import Image


class ExtractionError(Exception):
    """
    Raised when the extraction pipeline cannot recover a valid bitstream.

    Callers should catch this and return an appropriate HTTP 422 response.
    """


# Maximum sane payload size: 1 MB of MIR data.
# Prevents runaway allocation if the image has no valid header.
_MAX_PAYLOAD_BYTES = 1_048_576  # 1 MiB


def read_raw_lsbs(image: Image.Image, n_bits: int, offset: int = 0) -> list[int]:
    """
    Read `n_bits` LSBs from the image starting at channel index `offset`.

    Channels are enumerated in row-major order: R, G, B of pixel (0,0),
    then R, G, B of pixel (1,0), etc.

    Args:
        image:   PIL Image (will be converted to RGB if needed).
        n_bits:  Number of LSBs to read.
        offset:  Channel index to start reading from (default 0).

    Returns:
        list[int] — flat list of 0/1 integers, length == n_bits.

    Raises:
        ExtractionError: If the image has insufficient channels.
    """
    img = image.convert("RGB")
    pixels = list(img.getdata())
    flat: list[int] = []
    for r, g, b in pixels:
        flat.append(r & 1)
        flat.append(g & 1)
        flat.append(b & 1)

    end = offset + n_bits
    if end > len(flat):
        raise ExtractionError(
            f"Requested {n_bits} bits at offset {offset}, but image only has "
            f"{len(flat)} channels total."
        )

    return flat[offset:end]


def read_payload_bitstream(image: Image.Image, offset: int = 0, region_width: int | None = None) -> tuple[int, list[int]]:
    """
    Read the full provenance payload from an LSB-embedded image.

    Steps:
        1. Read the first 32 LSBs → 32-bit big-endian payload byte count.
        2. Validate the declared byte count (sanity check).
        3. Read the next  n_bytes × 8  LSBs → payload bits.

    Args:
        image: PIL Image that was processed by an LSB-based EmbeddingStrategy.
        offset: Channel index to start reading from (default 0).

    Returns:
        Tuple of (n_payload_bytes, payload_bits):
          - n_payload_bytes: int — number of payload bytes declared in header.
          - payload_bits:  list[int] — payload bits only (header NOT included).

    Raises:
        ExtractionError: If the image is too small, the header is corrupt,
                         or the declared payload exceeds the image capacity.
    """
    img = image.convert("RGB")
    pixels = list(img.getdata())
    total_channels = len(pixels) * 3

    # ------------------------------------------------------------------
    # 1. Read 32-bit header
    # ------------------------------------------------------------------
    if total_channels - offset < 32:
        raise ExtractionError(
            "Image is too small to contain a valid provenance header "
            f"(needs ≥ 32 channels from offset, found {total_channels - offset})."
        )

    w, h = image.size
    row_capacity = (region_width * 3) if region_width else (total_channels)
    
    def get_bit(idx: int) -> int:
        if region_width:
            row = idx // row_capacity
            col = idx % row_capacity
            actual_offset = offset + (row * w * 3) + col
        else:
            actual_offset = offset + idx
            
        if actual_offset >= total_channels:
            raise ExtractionError("Out of bounds")
            
        pixel_idx = actual_offset // 3
        channel = actual_offset % 3
        p = pixels[pixel_idx]
        return p[channel] & 1

    n_bytes = 0
    for i in range(32):
        n_bytes = (n_bytes << 1) | get_bit(i)

    # ------------------------------------------------------------------
    # 2. Sanity-check declared length
    # ------------------------------------------------------------------
    if n_bytes == 0:
        raise ExtractionError(
            "Header declares 0 payload bytes — this image may not have "
            "provenance data embedded."
        )

    if n_bytes > _MAX_PAYLOAD_BYTES:
        raise ExtractionError(
            f"Header declares {n_bytes:,} bytes, which exceeds the maximum "
            f"allowed payload size ({_MAX_PAYLOAD_BYTES:,} bytes). "
            "The image may not contain Aletheia provenance data."
        )

    # ------------------------------------------------------------------
    # 3. Read payload bits
    # ------------------------------------------------------------------
    payload_bit_count = n_bytes * 8
    total_needed = 32 + payload_bit_count

    if total_channels - offset < total_needed:
        raise ExtractionError(
            f"Header declares {n_bytes} payload bytes ({payload_bit_count} bits), "
            f"but image only has {total_channels - offset - 32} channels after the header."
        )

    payload_bits = []
    for i in range(32, 32 + payload_bit_count):
        payload_bits.append(get_bit(i))
        
    return n_bytes, payload_bits
