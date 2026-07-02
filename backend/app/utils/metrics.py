"""
metrics.py — Utilities for image quality assessment.
"""
import numpy as np
from PIL import Image

def calculate_mse(original: Image.Image, reconstructed: Image.Image) -> float:
    """
    Calculates the Mean Squared Error (MSE) between two PIL images.
    """
    orig_arr = np.array(original, dtype=np.float32)
    recon_arr = np.array(reconstructed, dtype=np.float32)
    
    if orig_arr.shape != recon_arr.shape:
        raise ValueError("Images must have the same dimensions to calculate MSE.")
        
    mse = np.mean((orig_arr - recon_arr) ** 2)
    return float(mse)

def calculate_psnr(original: Image.Image, reconstructed: Image.Image) -> float:
    """
    Calculates the Peak Signal-to-Noise Ratio (PSNR) between two PIL images.
    Returns float('inf') if MSE is zero (images are identical).
    """
    mse = calculate_mse(original, reconstructed)
    if mse == 0:
        return float('inf')
        
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return float(psnr)
