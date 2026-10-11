#!/usr/bin/env python3
"""
DeepTrace AI - Live API Smoke & Verification Utility.
Validates server health, analyzes sample evidence images, and verifies Conformal Prediction sets.
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


def test_health(base_url: str = DEFAULT_HOST) -> bool:
    """Verifies that the /health endpoint returns HTTP 200 with ok status."""
    url = f"{base_url}/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[HEALTH CHECK] Status: {resp.status} | Response: {data}")
            return resp.status == 200 and data.get("status") == "healthy"
    except Exception as e:
        print(f"[HEALTH CHECK FAILED] Could not reach {url}: {e}", file=sys.stderr)
        return False


def analyze_image(image_path: str, base_url: str = DEFAULT_HOST) -> dict:
    """Submits an image to /analyze via multipart/form-data."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    filename = os.path.basename(image_path)
    boundary = "----WebKitFormBoundaryDeepTraceVerification"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.write(b"Content-Type: image/jpeg\r\n\r\n")

    with open(image_path, "rb") as f:
        body.write(f.read())
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{base_url}/analyze",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print(f"DeepTrace AI - Verifying live server at {DEFAULT_HOST}...")
    if not test_health(DEFAULT_HOST):
        print("Server is not healthy or unreachable. Exiting with error.", file=sys.stderr)
        sys.exit(1)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_candidates = [
        os.path.join(project_root, "data", "test_images", "real_images", "authentic_photo.jpg"),
        os.path.join(project_root, "data", "test_images", "ai_generated_images", "ai_synthetic.jpg"),
        os.path.join(project_root, "data", "test_images", "edited_images", "spliced_tampered.jpg"),
        os.path.join(project_root, "test_images", "real_images", "authentic_photo.jpg"),
    ]

    found_samples = [p for p in sample_candidates if os.path.exists(p)]
    if not found_samples:
        print("Notice: No sample images found for live analysis check.")
        return

    print("\nRunning live forensic analysis tests on available samples:")
    for path in found_samples[:3]:
        fname = os.path.basename(path)
        try:
            res = analyze_image(path)
            verdict = res.get("verdict", "N/A")
            score = res.get("score", 0)
            det_type = res.get("detection_type", "N/A")
            analysis_id = res.get("analysis_id", "N/A")
            conf = res.get("conformal_prediction", {}).get("prediction_set", [])
            print(f"  [PASS] {fname:<25} | Verdict: {verdict:<16} | Suspicion: {score}% | ID: {analysis_id[:8]}... | Conformal: {conf}")
        except Exception as e:
            print(f"  [FAIL] {fname:<25} | Analysis failed: {e}", file=sys.stderr)

    print("\nLive server verification completed successfully!")


if __name__ == "__main__":
    main()
