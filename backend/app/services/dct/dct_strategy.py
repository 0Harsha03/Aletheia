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
from app.services.dct.coefficient_selector import get_embeddable_coefficients
from app.services.dct.qim_embedder import embed_bit


class DCTStrategy(EmbeddingStrategy):
    """
    Experimental DCT-based embedding strategy for Aletheia.
    Embeds bits using Quantization Index Modulation (QIM).
    """
    
    STRATEGY_NAME = "dct_experimental"
    Q_STEP = 16.0
    
    def embed(self, image: Image.Image, bitstream: list[int]) -> Image.Image:
        """
        Executes the DCT processing pipeline and embeds the bitstream.
        """
        # 1. Y Channel Extraction
        y_channel, cb, cr = get_ycbcr_channels(image)
        
        # 2. 8x8 Block Generation
        blocks = get_blocks_8x8(y_channel)
        coefficients = get_embeddable_coefficients()
        
        bit_idx = 0
        processed_blocks = []
        for block in blocks:
            # Level shifting for DCT (center around 0)
            shifted_block = block - 128.0
            
            # 3. Forward DCT
            dct_coeffs = forward_dct_8x8(shifted_block)
            
            # 4. QIM Embedding
            for (r, c) in coefficients:
                if bit_idx < len(bitstream):
                    dct_coeffs[r, c] = embed_bit(
                        dct_coeffs[r, c], 
                        bitstream[bit_idx], 
                        step=self.Q_STEP
                    )
                    bit_idx += 1
            
            # 5. Inverse DCT
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
        Returns the maximum number of bits that can be embedded.
        """
        y_channel, _, _ = get_ycbcr_channels(image)
        blocks = get_blocks_8x8(y_channel)
        coefficients = get_embeddable_coefficients()
        return len(blocks) * len(coefficients)
