"""
dct_strategy.py — Experimental frequency-domain embedding strategy using DCT.
"""

from PIL import Image

from app.services.embedding.embedding_strategy import EmbeddingStrategy
from app.services.dct.block_processor import (
    get_ycbcr_channels,
    get_blocks_8x8,
    reconstruct_y_channel,
    reconstruct_image
)
from app.services.dct.dct_transform import forward_dct_8x8, inverse_dct_8x8


class DCTStrategy(EmbeddingStrategy):
    """
    Experimental DCT-based embedding strategy for Aletheia.
    Currently establishes the image processing pipeline (Forward and Inverse DCT)
    without mutating coefficients to embed a payload.
    """
    
    STRATEGY_NAME = "dct_experimental"
    
    def embed(self, image: Image.Image, bitstream: list[int]) -> Image.Image:
        """
        Executes the DCT processing pipeline.
        This sprint ONLY runs the transform and inverse transform.
        The bitstream is intentionally ignored.
        """
        # 1. Y Channel Extraction
        y_channel, cb, cr = get_ycbcr_channels(image)
        
        # 2. 8x8 Block Generation
        blocks = get_blocks_8x8(y_channel)
        
        processed_blocks = []
        for block in blocks:
            # Level shifting for DCT (center around 0)
            shifted_block = block - 128.0
            
            # 3. Forward DCT
            dct_coeffs = forward_dct_8x8(shifted_block)
            
            # [Watermark embedding would happen here using coefficient_selector]
            
            # 4. Inverse DCT
            idct_block = inverse_dct_8x8(dct_coeffs)
            
            # Reverse level shifting
            reconstructed_block = idct_block + 128.0
            
            processed_blocks.append(reconstructed_block)
            
        # 5. Image Reconstruction
        y_recon = reconstruct_y_channel(processed_blocks, original_y=y_channel)
        final_image = reconstruct_image(y_recon, cb, cr)
        
        return final_image

    def capacity(self, image: Image.Image) -> int:
        """
        Returns the embedding capacity.
        Implementation deferred to future sprint.
        """
        return 0
