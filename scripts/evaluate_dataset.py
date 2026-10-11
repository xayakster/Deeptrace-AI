#!/usr/bin/env python3
"""
DeepTrace AI - Dataset Evaluation & Benchmark Script.
Evaluates the multi-branch forensic analysis pipeline against labeled datasets
in data/test_images/ (authentic, spliced, AI-generated).
"""

import os
import sys
import json
import io
import urllib.request
import urllib.error

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

DEFAULT_HOST = os.environ.get("DEEPTRACE_HOST", "http://localhost:8501")

def get_data_dir() -> str:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidate = os.path.join(project_root, "data", "test_images")
    if os.path.exists(candidate):
        return candidate
    legacy_candidate = os.path.join(project_root, "test_images")
    if os.path.exists(legacy_candidate):
        return legacy_candidate
    raise FileNotFoundError(f"Could not locate dataset images directory in {candidate} or {legacy_candidate}")

def analyze_sample(image_path: str, base_url: str = DEFAULT_HOST) -> dict:
    filename = os.path.basename(image_path)
    boundary = "----WebKitBoundaryBenchmark"
    body = io.BytesIO()
    body.write(b"--" + boundary.encode("utf-8") + b"\r\n")
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    with open(image_path, "rb") as f:
        body.write(f.read())
    body.write(b"\r\n--" + boundary.encode("utf-8") + b"--\r\n")

    req = urllib.request.Request(
        f"{base_url}/analyze",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    data_dir = get_data_dir()
    categories = ['real_images', 'edited_images', 'ai_generated_images']

    print(f"DeepTrace AI - Dataset Evaluation Suite")
    print(f"Target Server: {DEFAULT_HOST}")
    print(f"Dataset Root:  {data_dir}\n")
    print(f"{'Category':<22} {'Image':<26} {'Verdict':<15} {'Score':<8} {'Conformal 95% Set'}")
    print("-" * 95)

    total_evaluated = 0
    for category in categories:
        folder = os.path.join(data_dir, category)
        if not os.path.exists(folder):
            continue
        for img_name in sorted(os.listdir(folder)):
            if not img_name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
            path = os.path.join(folder, img_name)
            try:
                data = analyze_sample(path)
                v_badge = data.get('verdict_badge', data.get('verdict', 'UNKNOWN'))
                score = f"{data.get('score', 0)}%"
                conf_set = str(data.get('conformal_prediction', {}).get('prediction_set', []))
                print(f"{category:<22} {img_name:<26} {v_badge:<15} {score:<8} {conf_set}")
                total_evaluated += 1
            except Exception as e:
                print(f"{category:<22} {img_name:<26} {'ERROR':<15} {'-':<8} {e}", file=sys.stderr)

    print("-" * 95)
    print(f"Evaluation complete. Total samples analyzed: {total_evaluated}")

if __name__ == "__main__":
    main()
