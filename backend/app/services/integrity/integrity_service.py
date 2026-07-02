"""
integrity_service.py — Provenance Integrity Assessment Engine.
"""

from dataclasses import dataclass

@dataclass
class IntegrityAssessment:
    score: int
    observation: str
    status: str

def assess_integrity(
    recovered_regions: int,
    total_regions: int,
    similarity: float,
    hamming_distance: int,
    inconsistent: bool
) -> IntegrityAssessment:
    """
    Computes an Integrity Score and observation based on multi-region recovery 
    metrics and pHash similarity.
    """
    recovery_percentage = (recovered_regions / total_regions) * 100 if total_regions > 0 else 0

    # Base score on similarity
    score = similarity
    
    # Penalize if regions were lost (up to 20% penalty)
    if recovery_percentage < 100:
        penalty = ((100 - recovery_percentage) / 100) * 20
        score -= penalty
        
    if inconsistent:
        score -= 20
        
    # Cap between 0 and 100
    score = int(max(0, min(100, round(score))))

    # Determine status and observation
    if score >= 90 and hamming_distance <= 5 and recovered_regions == total_regions and not inconsistent:
        status = "AUTHENTIC"
        observation = "No tampering detected. Embedded provenance successfully recovered."
    elif score >= 70 or (recovered_regions > 0 and similarity >= 80):
        status = "MODIFIED"
        if recovered_regions == total_regions:
            observation = "Image has been visually modified but full provenance remains intact."
        else:
            observation = f"Partial provenance recovery ({recovered_regions}/{total_regions} regions). Image likely modified or cropped."
        if inconsistent:
            observation += " Warning: Provenance inconsistency detected across regions."
    else:
        status = "UNVERIFIED"
        observation = "Significant tampering detected. Embedded provenance could not be fully verified."

    return IntegrityAssessment(score=score, observation=observation, status=status)
