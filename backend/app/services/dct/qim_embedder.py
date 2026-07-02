"""
qim_embedder.py — Quantization Index Modulation (QIM) for frequency-domain embedding.
"""

def embed_bit(value: float, bit: int, step: float = 16.0) -> float:
    """
    Embeds a single bit into a DCT coefficient using Quantization Index Modulation.
    
    Bit 0: Quantize to the nearest even multiple of the step.
    Bit 1: Quantize to the nearest odd multiple of the step.
    
    Args:
        value: The original float coefficient.
        bit: The bit to embed (0 or 1).
        step: The quantization step size (higher = more robust but more distortion).
        
    Returns:
        The quantized coefficient.
    """
    if bit not in (0, 1):
        raise ValueError(f"Bit must be 0 or 1, got {bit}")

    # Nearest even multiple: round(value / (2*step)) * (2*step)
    q_even = round(value / (2 * step)) * (2 * step)
    
    # Nearest odd multiple: round((value - step) / (2*step)) * (2*step) + step
    q_odd = round((value - step) / (2 * step)) * (2 * step) + step

    return float(q_even) if bit == 0 else float(q_odd)

def extract_bit(value: float, step: float = 16.0) -> int:
    """
    Extracts a single bit from a QIM-quantized coefficient.
    
    Args:
        value: The quantized float coefficient.
        step: The quantization step size used during embedding.
        
    Returns:
        0 if the coefficient is closer to an even multiple, 1 if odd.
    """
    # Finding the nearest multiple
    quantized_index = round(value / step)
    return int(quantized_index % 2)
