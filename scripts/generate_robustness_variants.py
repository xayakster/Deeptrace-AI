#!/usr/bin/env python3
"""
DeepTrace AI — Robustness Testbed Generator.
Generates 18 controlled stress-testing variants across 6 representative baseline images:
- JPEG Q=60 compression
- Spatial downsampling (50% scale)
- Social media transcode simulation (800px Lanczos + JPEG Q=70 + metadata strip)
"""

import os
import sys
import json
import csv
import hashlib
import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation_dataset")
ROB_DIR = os.path.join(EVAL_DIR, "robustness_variants")
os.makedirs(ROB_DIR, exist_ok=True)

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

BASELINE_SUBJECTS = [
    {
        "parent_id": "CAM-01",
        "parent_category": "genuine_camera",
        "parent_filename": "cam_01_nikon_d70_portrait.jpg",
        "ground_truth_label": "AUTHENTIC",
        "description": "Genuine Nikon D70 Portrait",
    },
    {
        "parent_id": "CAM-02",
        "parent_category": "genuine_camera",
        "parent_filename": "cam_02_canon_40d_nature.jpg",
        "ground_truth_label": "AUTHENTIC",
        "description": "Genuine Canon 40D Nature",
    },
    {
        "parent_id": "AI-01",
        "parent_category": "ai_generated",
        "parent_filename": "ai_01_midjourney_v5_fantasy_landscape.jpg",
        "ground_truth_label": "AI_GENERATED",
        "description": "Midjourney v5 Fantasy Landscape",
    },
    {
        "parent_id": "AI-04",
        "parent_category": "ai_generated",
        "parent_filename": "ai_04_stablediffusion_v15_animal.png",
        "ground_truth_label": "AI_GENERATED",
        "description": "Stable Diffusion v1.5 Animal",
    },
    {
        "id_prefix": "TAMP-01",
        "parent_id": "TAMP-01",
        "parent_category": "tampered",
        "parent_filename": "tamp_01_casia2_splicing_nature.jpg",
        "ground_truth_label": "TAMPERED",
        "description": "CASIA 2.0 Splicing Nature",
    },
    {
        "id_prefix": "TAMP-03",
        "parent_id": "TAMP-03",
        "parent_category": "tampered",
        "parent_filename": "tamp_03_casia2_copymove_foliage.jpg",
        "ground_truth_label": "TAMPERED",
        "description": "CASIA 2.0 Copy-Move Foliage",
    },
]

def main():
    print("[*] Generating 18 Controlled Robustness Testbed Variants...")
    records = []

    for subj in BASELINE_SUBJECTS:
        p_cat = subj["parent_category"]
        p_fn = subj["parent_filename"]
        p_id = subj["parent_id"]
        gt_label = subj["ground_truth_label"]
        src_path = os.path.join(EVAL_DIR, p_cat, p_fn)

        if not os.path.exists(src_path):
            print(f"[-] Missing baseline subject: {src_path}", file=sys.stderr)
            continue

        base_name = os.path.splitext(p_fn)[0]

        # 1. Variant A: JPEG Quality 60 Compression
        v1_fn = f"{base_name}_rob_jpeg_q60.jpg"
        v1_path = os.path.join(ROB_DIR, v1_fn)
        img = Image.open(src_path).convert("RGB")
        img.save(v1_path, "JPEG", quality=60)
        records.append({
            "variant_id": f"ROB-{p_id}-Q60",
            "filename": v1_fn,
            "parent_id": p_id,
            "parent_category": p_cat,
            "ground_truth_label": gt_label,
            "transformation_type": "JPEG Recompression (Q=60)",
            "transformation_params": "quality=60, standard quantization matrix",
            "filesize_bytes": os.path.getsize(v1_path),
            "resolution": f"{img.size[0]}x{img.size[1]}",
            "sha256_hash": compute_sha256(v1_path),
            "relative_path": os.path.relpath(v1_path, PROJECT_ROOT).replace("\\", "/")
        })

        # 2. Variant B: Spatial Downsampling 50%
        v2_fn = f"{base_name}_rob_downsample_50pct.jpg"
        v2_path = os.path.join(ROB_DIR, v2_fn)
        w, h = img.size
        new_w, new_h = max(32, w // 2), max(32, h // 2)
        down = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
        down.save(v2_path, "JPEG", quality=85)
        records.append({
            "variant_id": f"ROB-{p_id}-DOWN50",
            "filename": v2_fn,
            "parent_id": p_id,
            "parent_category": p_cat,
            "ground_truth_label": gt_label,
            "transformation_type": "Spatial Downsampling (50%)",
            "transformation_params": f"scale=0.5, interpolation=BILINEAR, {w}x{h}->{new_w}x{new_h}",
            "filesize_bytes": os.path.getsize(v2_path),
            "resolution": f"{new_w}x{new_h}",
            "sha256_hash": compute_sha256(v2_path),
            "relative_path": os.path.relpath(v2_path, PROJECT_ROOT).replace("\\", "/")
        })

        # 3. Variant C: Social Media Pipeline Simulation (Lanczos 800px + JPEG Q=70 + EXIF Strip)
        v3_fn = f"{base_name}_rob_social_pipeline.jpg"
        v3_path = os.path.join(ROB_DIR, v3_fn)
        target_w = min(800, w)
        target_h = int(h * (target_w / float(w)))
        social = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        # Strip all metadata
        clean_img = Image.new("RGB", (target_w, target_h))
        clean_img.putdata(list(social.getdata()))
        clean_img.save(v3_path, "JPEG", quality=70)
        records.append({
            "variant_id": f"ROB-{p_id}-SOCIAL",
            "filename": v3_fn,
            "parent_id": p_id,
            "parent_category": p_cat,
            "ground_truth_label": gt_label,
            "transformation_type": "Social Media Pipeline",
            "transformation_params": f"lanczos_width={target_w}, jpeg_q=70, exif_stripped=True",
            "filesize_bytes": os.path.getsize(v3_path),
            "resolution": f"{target_w}x{target_h}",
            "sha256_hash": compute_sha256(v3_path),
            "relative_path": os.path.relpath(v3_path, PROJECT_ROOT).replace("\\", "/")
        })

    # Export Manifests
    json_path = os.path.join(EVAL_DIR, "robustness_manifest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"[+] Wrote robustness JSON manifest: {json_path} ({len(records)} records)")

    csv_path = os.path.join(EVAL_DIR, "robustness_manifest.csv")
    fieldnames = [
        "variant_id", "filename", "parent_id", "parent_category",
        "ground_truth_label", "transformation_type", "transformation_params",
        "filesize_bytes", "resolution", "sha256_hash", "relative_path"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[+] Wrote robustness CSV manifest: {csv_path}")

if __name__ == "__main__":
    main()
