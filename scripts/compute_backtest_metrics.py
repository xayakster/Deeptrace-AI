#!/usr/bin/env python3
"""
DeepTrace AI — Backtesting Metrics & Statistical Engine.
Parses reports/evaluation_results.json and reports/robustness_results.json
to compute multi-class confusion matrices, precision, recall, F1, FPR, FNR,
balanced accuracy, calibration, and latency metrics with exact numerators and denominators.
"""

import os
import json
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_RESULTS_PATH = os.path.join(PROJECT_ROOT, "reports", "evaluation_results.json")
ROB_RESULTS_PATH = os.path.join(PROJECT_ROOT, "reports", "robustness_results.json")

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_metrics():
    primary_data = load_json(EVAL_RESULTS_PATH)
    rob_data = load_json(ROB_RESULTS_PATH)

    total_primary = len(primary_data)
    print(f"Loaded {total_primary} primary evaluation records.")

    # Multi-class confusion matrix
    classes = ["AUTHENTIC", "AI_GENERATED", "TAMPERED"]
    all_preds = ["AUTHENTIC", "AI_GENERATED", "TAMPERED", "INCONCLUSIVE"]
    
    matrix = {gt: {pred: 0 for pred in all_preds} for gt in classes}
    category_counts = Counter()
    category_correct = Counter()
    latencies = []
    pdf_success = 0

    for item in primary_data:
        gt = item["ground_truth_label"]
        pred = item["predicted_label"]
        cat = item["category"]
        latencies.append(item["analysis_latency_ms"])
        if item.get("pdf_report_generated") and item.get("pdf_valid_magic"):
            pdf_success += 1

        category_counts[cat] += 1
        if item["is_correct"]:
            category_correct[cat] += 1

        if gt in matrix and pred in matrix[gt]:
            matrix[gt][pred] += 1

    # Print Confusion Matrix
    print("\n" + "=" * 60)
    print("PRIMARY EVALUATION CONFUSION MATRIX (N = 42)")
    print("=" * 60)
    header = f"{'Ground Truth':<15} | " + " | ".join(f"{p:<12}" for p in all_preds) + " | Total"
    print(header)
    print("-" * len(header))
    for gt in classes:
        row = f"{gt:<15} | " + " | ".join(f"{matrix[gt][p]:<12}" for p in all_preds) + f" | {sum(matrix[gt].values())}"
        print(row)
    print("-" * len(header))

    # Calculate Per-Class Metrics
    metrics = {}
    print("\n" + "=" * 80)
    print(f"{'Class':<15} {'TP':<5} {'FP':<5} {'FN':<5} {'TN':<5} {'Precision':<12} {'Recall':<12} {'F1':<10}")
    print("-" * 80)

    for c in classes:
        tp = matrix[c][c]
        fn = sum(matrix[c][p] for p in all_preds if p != c)
        fp = sum(matrix[other][c] for other in classes if other != c)
        tn = sum(sum(matrix[other][p] for p in all_preds if p != c) for other in classes if other != c)
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        metrics[c] = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": prec, "recall": rec, "f1": f1,
            "fpr": fpr, "fnr": fnr
        }
        prec_str = f"{prec*100:.1f}% ({tp}/{tp+fp})" if (tp+fp) > 0 else "0.0% (0/0)"
        rec_str = f"{rec*100:.1f}% ({tp}/{tp+fn})" if (tp+fn) > 0 else "0.0% (0/0)"
        print(f"{c:<15} {tp:<5} {fp:<5} {fn:<5} {tn:<5} {prec_str:<12} {rec_str:<12} {f1*100:.1f}%")

    print("-" * 80)

    # Headline Overall Metrics
    total_tp = sum(matrix[c][c] for c in classes)
    overall_acc = total_tp / total_primary
    recalls = [metrics[c]["recall"] for c in classes]
    balanced_acc = sum(recalls) / len(recalls)

    print(f"\nHeadline Accuracy:  {overall_acc*100:.2f}% ({total_tp}/{total_primary})")
    print(f"Balanced Accuracy:  {balanced_acc*100:.2f}% (Average of Per-Class Recalls)")

    # Category Accuracies
    print("\n" + "=" * 60)
    print("CATEGORY-SPECIFIC ACCURACY BREAKDOWN")
    print("=" * 60)
    for cat in ["genuine_camera", "genuine_processed", "ai_generated", "tampered"]:
        corr = category_correct[cat]
        tot = category_counts[cat]
        pct = (corr / tot) * 100 if tot > 0 else 0.0
        print(f"{cat:<22} : {pct:5.1f}% ({corr}/{tot})")

    # Latency Stats
    lat_arr = np.array(latencies)
    print("\n" + "=" * 60)
    print("OPERATIONAL LATENCY PROFILE (Client Total Roundtrip)")
    print("=" * 60)
    print(f"Mean Latency:    {np.mean(lat_arr):.2f} ms")
    print(f"Median (p50):    {np.median(lat_arr):.2f} ms")
    print(f"p95 Latency:     {np.percentile(lat_arr, 95):.2f} ms")
    print(f"Min / Max:       {np.min(lat_arr):.2f} ms / {np.max(lat_arr):.2f} ms")

    # PDF Report Audit
    print("\n" + "=" * 60)
    print("FORENSIC DOSSIER GENERATION AUDIT")
    print("=" * 60)
    pdf_pct = (pdf_success / total_primary) * 100
    print(f"PDF Generation Success: {pdf_pct:.1f}% ({pdf_success}/{total_primary})")
    pdf_sizes = [item.get("pdf_filesize_bytes", 0) for item in primary_data if item.get("pdf_report_generated")]
    if pdf_sizes:
        print(f"Mean PDF Size:          {np.mean(pdf_sizes):.1f} bytes ({np.mean(pdf_sizes)/1024:.1f} KB)")

    # Robustness Analysis
    print("\n" + "=" * 70)
    print("CONTROLLED ROBUSTNESS STRESS-TESTING RESULTS (N = 18)")
    print("=" * 70)
    trans_counts = Counter()
    trans_correct = Counter()
    for r in rob_data:
        t_type = r["transformation_type"]
        trans_counts[t_type] += 1
        if r["is_correct"]:
            trans_correct[t_type] += 1
        s_id = r.get("sample_id", r.get("variant_id", "ROB"))
        print(f"[{s_id:<18}] {r.get('parent_id', '-')} ({r['ground_truth_label']:<12}) -> {r['predicted_label']:<12} ({r['composite_score']:4.1f}%) | {t_type}")

    print("\nRobustness Degradation by Transformation Type:")
    for t_type, tot in trans_counts.items():
        corr = trans_correct[t_type]
        pct = (corr / tot) * 100 if tot > 0 else 0.0
        print(f"  {t_type:<35} : {pct:5.1f}% ({corr}/{tot})")

    # Export computed metrics to JSON for the report
    computed_summary = {
        "total_primary_samples": total_primary,
        "total_robustness_samples": len(rob_data),
        "overall_accuracy": {"percent": round(overall_acc * 100, 2), "numerator": total_tp, "denominator": total_primary},
        "balanced_accuracy": {"percent": round(balanced_acc * 100, 2)},
        "confusion_matrix": matrix,
        "class_metrics": metrics,
        "category_accuracy": {cat: {"percent": round((category_correct[cat]/category_counts[cat])*100, 2), "numerator": category_correct[cat], "denominator": category_counts[cat]} for cat in category_counts},
        "latency_profile": {
            "mean_ms": round(float(np.mean(lat_arr)), 2),
            "median_ms": round(float(np.median(lat_arr)), 2),
            "p95_ms": round(float(np.percentile(lat_arr, 95)), 2),
            "min_ms": round(float(np.min(lat_arr)), 2),
            "max_ms": round(float(np.max(lat_arr)), 2)
        },
        "pdf_audit": {
            "success_rate_percent": round(pdf_pct, 2),
            "success_count": pdf_success,
            "total_count": total_primary,
            "mean_size_kb": round(float(np.mean(pdf_sizes)/1024), 2) if pdf_sizes else 0
        },
        "robustness_summary": {t_type: {"accuracy_percent": round((trans_correct[t_type]/tot)*100, 2), "correct": trans_correct[t_type], "total": tot} for t_type, tot in trans_counts.items()}
    }

    with open(os.path.join(PROJECT_ROOT, "reports", "computed_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(computed_summary, f, indent=2)
    print("\n[+] Exported computed summary metrics to reports/computed_metrics.json")

if __name__ == "__main__":
    compute_metrics()
