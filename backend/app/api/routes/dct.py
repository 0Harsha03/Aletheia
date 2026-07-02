"""
api/routes/dct.py — Experimental DCT testing routes.
"""
import io
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image

from app.services.dct.dct_strategy import DCTStrategy
from app.utils.metrics import calculate_psnr, calculate_mse
from app.services.dct.block_processor import get_ycbcr_channels, get_blocks_8x8

router = APIRouter()

@router.post(
    "/test",
    summary="Test the experimental DCT processing pipeline",
    description="Runs the forward and inverse DCT on an uploaded image to verify quality (PSNR/MSE)."
)
async def test_dct_pipeline(
    file: UploadFile = File(..., description="Image to test the DCT pipeline on.")
):
    contents = await file.read()
    
    try:
        # Convert to RGB to ensure standard 3-channel handling
        original_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot open uploaded file as an image: {exc}",
        )
        
    strategy = DCTStrategy()
    
    # Execute DCT pipeline (no actual bits embedded)
    reconstructed_image = strategy.embed(original_image, [])
    
    # Calculate visual quality metrics
    psnr = calculate_psnr(original_image, reconstructed_image)
    mse = calculate_mse(original_image, reconstructed_image)
    
    # Calculate block count
    y_channel, _, _ = get_ycbcr_channels(original_image)
    blocks = get_blocks_8x8(y_channel)
    
    return {
        "status": "success",
        "blocks": len(blocks),
        "psnr": round(psnr, 4),
        "mse": round(mse, 4)
    }
