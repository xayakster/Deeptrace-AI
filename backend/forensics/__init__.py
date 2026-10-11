"""
DeepTrace AI — Modular Forensic Engine
Package initialization and public API exports.
"""

from .provenance import (
    calculate_hashes,
    calculate_perceptual_hash,
    extract_metadata,
    audit_c2pa_manifest,
)
from .frequency import (
    analyze_frequency_domain,
)
from .tampering import (
    perform_tamper_analysis,
    compute_laplacian_noise_variance,
    compute_block_anomaly_grid,
    generate_tamper_heatmap_overlay,
)
from .explainability import (
    generate_ai_attribution_heatmap,
    generate_ai_attribution_overlay,
    compute_patch_synthesis_attribution,
)
from .arbitrator import (
    arbitrate_forensic_evidence,
)
from .dossier import (
    generate_forensic_dossier_pdf,
    map_enfsi_verbal_scale,
    ForensicDossierPDF,
)

__all__ = [
    "calculate_hashes",
    "calculate_perceptual_hash",
    "extract_metadata",
    "audit_c2pa_manifest",
    "analyze_frequency_domain",
    "perform_tamper_analysis",
    "compute_laplacian_noise_variance",
    "compute_block_anomaly_grid",
    "generate_tamper_heatmap_overlay",
    "generate_ai_attribution_heatmap",
    "generate_ai_attribution_overlay",
    "compute_patch_synthesis_attribution",
    "arbitrate_forensic_evidence",
    "generate_forensic_dossier_pdf",
    "map_enfsi_verbal_scale",
    "ForensicDossierPDF",
]
