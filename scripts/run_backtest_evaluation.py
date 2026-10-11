#!/usr/bin/env python3
"""
DeepTrace AI — Real-World Forensic Detection Backtesting Execution Runner.
Evaluates all 42 primary benchmark images + 18 robustness stress variants against the live
DeepTrace AI forensic pipeline via /analyze and /download_report endpoints.

Captures all telemetry, dual-scores, frequency/SRM residuals, tamper heatmaps,
explainability metrics, conformal sets, PDF dossiers, and execution latencies.
"""

import os
import sys
import json
import csv
import io
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

DEFAULT_HOST = os.environ.get("DEEPTRACE_HOST", "http://localhost:8501")

def query_analyze_endpoint(image_path: str, base_url: str = DEFAULT_HOST) -> Dict[str, Any]:
    filename = os.path.basename(image_path)
    boundary = "----WebKitBoundaryBacktesting"
    body = io.BytesIO()
    body.write(b"--" + boundary.encode("utf-8") + b"\r\n")
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    
    # MIME type
    ext = os.path.splitext(filename)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else ("image/png" if ext == ".png" else "image/webp")
    body.write(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
    
    with open(image_path, "rb") as f:
        body.write(f.read())
    body.write(b"\r\n--" + boundary.encode("utf-8") + b"--\r\n")
    
    t0 = time.perf_counter()
    req = urllib.request.Request(
        f"{base_url}/analyze",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    resp_data["_client_latency_ms"] = latency_ms
    return resp_data

def query_download_report(analysis_id: str, base_url: str = DEFAULT_HOST) -> Dict[str, Any]:
    """Requests and audits the generated 4-page PDF forensic dossier."""
    try:
        t0 = time.perf_counter()
        req = urllib.request.Request(
            f"{base_url}/download_report",
            data=json.dumps({"analysis_id": analysis_id}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            pdf_bytes = resp.read()
            status = resp.status
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        
        is_pdf = pdf_bytes.startswith(b"%PDF-")
        return {
            "pdf_generated": True,
            "status_code": status,
            "pdf_size_bytes": len(pdf_bytes),
            "is_valid_pdf_magic": is_pdf,
            "pdf_latency_ms": latency_ms
        }
    except Exception as e:
        return {
            "pdf_generated": False,
            "status_code": 500,
            "pdf_size_bytes": 0,
            "is_valid_pdf_magic": False,
            "pdf_latency_ms": 0.0,
            "error": str(e)
        }

def evaluate_manifest(manifest_path: str, is_robustness: bool = False) -> List[Dict[str, Any]]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    results = []
    total = len(manifest)
    print(f"[*] Commencing backtest on {'robustness' if is_robustness else 'primary'} dataset ({total} images)...")

    for idx, item in enumerate(manifest, 1):
        rel_path = item["relative_path"]
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        img_id = item.get("image_id", item.get("variant_id"))
        gt_label = item["ground_truth_label"]
        fn = item["filename"]

        print(f"[{idx:02d}/{total:02d}] Testing {img_id:<16} | {fn:<35}", end="", flush=True)

        try:
            res = query_analyze_endpoint(abs_path)
            analysis_id = res.get("analysis_id", "")
            
            # Audit PDF Dossier
            pdf_audit = query_download_report(analysis_id) if analysis_id else {}

            scores_obj = res.get("scores", {})
            dual_obj = res.get("dual_telemetry", {})
            freq_obj = res.get("frequency_analysis", {})
            tamp_obj = res.get("tamper_analysis", {})
            conf_obj = res.get("conformal_prediction", {})
            expl_obj = res.get("explainability", {})

            pred_badge = res.get("verdict_badge", res.get("verdict", "UNKNOWN"))
            # Standardize mapped predicted label for classification metrics
            if pred_badge in ("AI GENERATED", "SYNTHETIC"):
                pred_label = "AI_GENERATED"
            elif pred_badge in ("TAMPERED", "MANIPULATED"):
                pred_label = "TAMPERED"
            elif pred_badge in ("AUTHENTIC", "NATURAL"):
                pred_label = "AUTHENTIC"
            elif pred_badge in ("INCONCLUSIVE", "SUSPICIOUS"):
                pred_label = "INCONCLUSIVE"
            else:
                pred_label = "UNKNOWN"

            is_correct = (pred_label == gt_label)
            is_false_negative = (gt_label in ("AI_GENERATED", "TAMPERED") and pred_label == "AUTHENTIC")
            is_false_positive = (gt_label == "AUTHENTIC" and pred_label in ("AI_GENERATED", "TAMPERED"))

            rec = {
                "sample_id": img_id,
                "filename": fn,
                "category": item.get("category", item.get("parent_category", "unknown")),
                "ground_truth_label": gt_label,
                "predicted_label": pred_label,
                "verdict_badge": pred_badge,
                "is_correct": is_correct,
                "is_false_negative": is_false_negative,
                "is_false_positive": is_false_positive,
                
                # Scores
                "composite_score": res.get("score", 0.0),
                "neural_ai_score": scores_obj.get("neural_ai_score", res.get("neural_ai_score", 0.0)),
                "physical_sensor_score": scores_obj.get("physical_sensor_score", res.get("physical_sensor_score", 0.0)),
                "tamper_score": scores_obj.get("tamper_score", res.get("tamper_score", 0.0)),
                
                # Physical / Frequency / SRM Telemetry
                "spectral_peak_ratio": freq_obj.get("spectral_peak_ratio", 0.0),
                "decay_slope": freq_obj.get("decay_slope", 0.0),
                "srm_void_ratio": freq_obj.get("srm_void_ratio", 0.0),
                "srm_noise_energy": freq_obj.get("srm_noise_energy", 0.0),
                "npr_covariance_score": freq_obj.get("npr_covariance_score", 0.0),
                
                # Tamper Localization Telemetry
                "spatial_inconsistency_z": tamp_obj.get("spatial_inconsistency", 0.0),
                "tamper_coverage_ratio": tamp_obj.get("tamper_coverage_ratio", 0.0),
                "laplacian_noise_variance": tamp_obj.get("laplacian_variance", 0.0),
                "ela_std": tamp_obj.get("ela_std", 0.0),
                "texture_reliability_index": tamp_obj.get("reliability_index", 1.0),
                
                # Explainability & Heatmaps
                "has_ela_overlay": bool(res.get("ela_image")),
                "has_tamper_heatmap": bool(res.get("heatmap_image")),
                "has_ai_attribution": bool(res.get("ai_attribution_overlay")),
                "ai_attribution_peak": expl_obj.get("ai_attribution_peak", 0.0),
                "ai_attribution_coverage": expl_obj.get("ai_attribution_coverage", 0.0),
                
                # Conformal Prediction
                "conformal_prediction_set": conf_obj.get("prediction_set", []),
                "conformal_status_label": conf_obj.get("status_label", ""),
                
                # PDF Dossier Audit
                "pdf_report_generated": pdf_audit.get("pdf_generated", False),
                "pdf_filesize_bytes": pdf_audit.get("pdf_size_bytes", 0),
                "pdf_valid_magic": pdf_audit.get("is_valid_pdf_magic", False),
                "pdf_generation_ms": pdf_audit.get("pdf_latency_ms", 0.0),
                
                # Operational Performance
                "analysis_id": analysis_id,
                "analysis_latency_ms": res.get("_client_latency_ms", 0.0),
                "server_reported_latency_ms": res.get("latency_ms", 0.0),
                "error": None
            }

            if is_robustness:
                rec["parent_id"] = item.get("parent_id", "")
                rec["transformation_type"] = item.get("transformation_type", "")
                rec["transformation_params"] = item.get("transformation_params", "")

            results.append(rec)
            status_symbol = "[PASS]" if is_correct else ("[FAIL FN]" if is_false_negative else "[FAIL INCON/FP]")
            print(f" -> {pred_badge:<12} ({res.get('score', 0)}%) {status_symbol} ({res.get('_client_latency_ms', 0)}ms)")

        except Exception as e:
            print(f" -> ERROR: {e}")
            results.append({
                "sample_id": img_id,
                "filename": fn,
                "category": item.get("category", "unknown"),
                "ground_truth_label": gt_label,
                "predicted_label": "ERROR",
                "verdict_badge": "ERROR",
                "is_correct": False,
                "is_false_negative": False,
                "is_false_positive": False,
                "composite_score": 0.0,
                "error": str(e)
            })

    return results

def main():
    print(f"DeepTrace AI — Real-World Forensic Detection Backtesting Execution")
    print(f"Target Server: {DEFAULT_HOST}\n")

    # 1. Primary Evaluation (42 images)
    primary_manifest = os.path.join(PROJECT_ROOT, "evaluation_dataset", "dataset_manifest.json")
    primary_results = evaluate_manifest(primary_manifest, is_robustness=False)

    json_out = os.path.join(REPORTS_DIR, "evaluation_results.json")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(primary_results, f, indent=2)
    print(f"\n[+] Saved primary evaluation JSON: {json_out} ({len(primary_results)} samples)")

    csv_out = os.path.join(REPORTS_DIR, "evaluation_results.csv")
    if primary_results:
        fieldnames = list(primary_results[0].keys())
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(primary_results)
        print(f"[+] Saved primary evaluation CSV: {csv_out}")

    # 2. Robustness Variants Evaluation (18 images)
    rob_manifest = os.path.join(PROJECT_ROOT, "evaluation_dataset", "robustness_manifest.json")
    rob_results = evaluate_manifest(rob_manifest, is_robustness=True)

    rob_json_out = os.path.join(REPORTS_DIR, "robustness_results.json")
    with open(rob_json_out, "w", encoding="utf-8") as f:
        json.dump(rob_results, f, indent=2)
    print(f"\n[+] Saved robustness evaluation JSON: {rob_json_out} ({len(rob_results)} samples)")

    rob_csv_out = os.path.join(REPORTS_DIR, "robustness_results.csv")
    if rob_results:
        fieldnames = list(rob_results[0].keys())
        with open(rob_csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rob_results)
        print(f"[+] Saved robustness evaluation CSV: {rob_csv_out}")

    print("\n[✓] Backtesting execution run complete!")

if __name__ == "__main__":
    main()
