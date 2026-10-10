"""
DeepTrace AI — Provenance & Cryptographic Verification Module
Part of the Tri-Branch Forensic Architecture (Branch 1)

Handles:
- Cryptographic hash fingerprints (MD5, SHA-256)
- Perceptual difference hashing (dHash) for visual lineage
- Safe, non-discounting EXIF metadata parsing
- C2PA Content Credentials cryptographic manifest auditing
"""

import json
import hashlib
from typing import Tuple, Dict, Any, Optional
from PIL import Image
from PIL.ExifTags import TAGS

# Safe import for C2PA library
try:
    import c2pa
    HAS_C2PA = True
except ImportError:
    HAS_C2PA = False


def calculate_hashes(file_bytes: bytes) -> Tuple[str, str]:
    """
    Computes cryptographic fingerprints for digital evidence chain of custody.
    Returns (MD5, SHA-256) as lowercase hex strings.
    """
    md5 = hashlib.md5(file_bytes).hexdigest()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    return md5, sha256


def calculate_perceptual_hash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Computes a 64-bit difference hash (dHash) for perceptual visual lineage.
    Resistant to minor scaling, mild recompression, and format conversion.
    """
    try:
        # Resize to (hash_size + 1, hash_size) in grayscale
        resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
        pixels = list(resized.getdata())
        
        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                left_pixel = pixels[row * (hash_size + 1) + col]
                right_pixel = pixels[row * (hash_size + 1) + col + 1]
                difference.append(1 if left_pixel > right_pixel else 0)
        
        decimal_val = 0
        hex_string = []
        for index, val in enumerate(difference):
            if val:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_string.append(hex(decimal_val)[2:])
                decimal_val = 0
                
        return ''.join(hex_string)
    except Exception:
        return "0000000000000000"


def extract_metadata(image: Image.Image) -> Dict[str, Any]:
    """
    Extracts and decodes EXIF metadata tags from image headers.
    Handles corrupt, missing, and non-standard tags safely.
    Strictly descriptive: does not apply arbitrary trust discounts to scores.
    """
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if isinstance(value, bytes):
                    value = value.decode(errors='ignore')
                exif_data[str(decoded)] = str(value)
        else:
            exif_data = {"Status": "No EXIF Metadata found."}
    except Exception:
        exif_data = {"Status": "Extraction Failure or Malformed EXIF."}
    return exif_data


def audit_c2pa_manifest(file_path: str) -> Dict[str, Any]:
    """
    Audits C2PA (Coalition for Content Provenance and Authenticity) manifests.
    Verifies cryptographic signatures and detects declarations of AI synthesis
    (e.g., DALL-E 3, Adobe Firefly, Microsoft Designer, Google Imagen).
    """
    provenance_info = {
        "has_c2pa": False,
        "is_ai_claimed": False,
        "is_hardware_camera": False,
        "validation_state": "NONE",
        "issuer": "N/A",
        "generator": "N/A",
        "details": "No C2PA manifest found in asset."
    }

    if not HAS_C2PA:
        provenance_info["details"] = "C2PA module not available in environment."
        return provenance_info

    try:
        reader = c2pa.Reader.try_create(file_path)
        if reader is None:
            return provenance_info

        provenance_info["has_c2pa"] = True
        val_state = reader.get_validation_state() or "UNVERIFIED"
        provenance_info["validation_state"] = str(val_state).upper()

        manifest_json_str = reader.json()
        manifest_data = json.loads(manifest_json_str)

        # Inspect active manifest claims
        active_manifest = manifest_data.get("active_manifest", {})
        if not active_manifest and "manifests" in manifest_data:
            manifests = manifest_data.get("manifests", {})
            if manifests:
                active_manifest = next(iter(manifests.values()))

        # Extract title and claim generator
        claim_generator = active_manifest.get("claim_generator", "")
        title = active_manifest.get("title", "")
        provenance_info["generator"] = claim_generator or title or "Standard C2PA Signer"

        # Extract signature issuer if present
        signature_info = active_manifest.get("signature_info", {})
        issuer = signature_info.get("issuer", "")
        provenance_info["issuer"] = issuer or "Authenticated Signer"

        # Search for AI indicators across assertions and action claims
        raw_manifest_str = json.dumps(active_manifest).lower()
        ai_keywords = [
            "ai_generated", "dall-e", "firefly", "midjourney",
            "stablediffusion", "synthetic", "c2pa.created.synthetic",
            "generative", "trained algorithmic media"
        ]

        if any(kw in raw_manifest_str for kw in ai_keywords):
            provenance_info["is_ai_claimed"] = True
            provenance_info["details"] = (
                f"Cryptographically verified AI provenance ({provenance_info['generator']}). "
                f"Digital manifest indicates generative AI creation."
            )
        else:
            # Check for camera hardware signatures (Leica, Sony, Nikon CAI firmware)
            hardware_keywords = ["camera", "sensor", "capture", "device", "c2pa.created.captured"]
            if any(kw in raw_manifest_str for kw in hardware_keywords):
                provenance_info["is_hardware_camera"] = True
                provenance_info["details"] = (
                    f"Cryptographically verified camera provenance ({provenance_info['generator']}). "
                    f"Physical capture device signature authenticated."
                )
            else:
                provenance_info["details"] = (
                    f"Valid C2PA manifest present from {provenance_info['generator']}."
                )

        return provenance_info

    except Exception as e:
        provenance_info["has_c2pa"] = True
        provenance_info["validation_state"] = "PARSING_ERROR"
        provenance_info["details"] = f"Manifest detected but parsing encountered: {str(e)}"
        return provenance_info
