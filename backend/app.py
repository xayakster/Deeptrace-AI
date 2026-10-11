"""
DeepTrace AI v2.5 — Backend Application Server & Forensic API
AI-Powered Digital Media Forensics & Source Tracking System
"""

import os
import io
import sys
import time
import uuid
import base64
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from collections import OrderedDict
from typing import Dict, Any, Optional
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF

# Configure project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'static')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Import modular forensics engine (supporting both backend package and legacy imports)
try:
    from backend.forensics import (
        calculate_hashes,
        calculate_perceptual_hash,
        extract_metadata,
        audit_c2pa_manifest,
        analyze_frequency_domain,
        detect_neural_synthesis,
        perform_tamper_analysis,
        generate_ai_attribution_heatmap,
        arbitrate_forensic_evidence,
        generate_forensic_dossier_pdf,
        ForensicDossierPDF,
    )
except ImportError:
    from forensics import (
        calculate_hashes,
        calculate_perceptual_hash,
        extract_metadata,
        audit_c2pa_manifest,
        analyze_frequency_domain,
        detect_neural_synthesis,
        perform_tamper_analysis,
        generate_ai_attribution_heatmap,
        arbitrate_forensic_evidence,
        generate_forensic_dossier_pdf,
        ForensicDossierPDF,
    )

# Configure Decompression Bomb Protection
Image.MAX_IMAGE_PIXELS = 50_000_000

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

# Application Configuration
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # 15 MB max upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'}


# --- THREAD-SAFE SERVER-SIDE EXAMINATION RECORD CACHE ---

class AnalysisRecordCache:
    """
    Thread-safe, memory-bounded LRU cache for immutable forensic examination records.
    Guarantees that reports downloaded via analysis_id reflect exact server-side evidence
    and prevents client-side payload tampering.
    """
    def __init__(self, capacity: int = 100, max_age_seconds: int = 3600):
        self.capacity = capacity
        self.max_age_seconds = max_age_seconds
        self._cache = OrderedDict()
        self._lock = threading.Lock()

    def put(self, analysis_id: str, record: Dict[str, Any]):
        with self._lock:
            if len(self._cache) >= self.capacity:
                self._cache.popitem(last=False)
            record['_cached_at'] = time.time()
            self._cache[analysis_id] = record

    def get(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if analysis_id not in self._cache:
                return None
            record = self._cache[analysis_id]
            if time.time() - record.get('_cached_at', 0) > self.max_age_seconds:
                del self._cache[analysis_id]
                return None
            self._cache.move_to_end(analysis_id)
            return record


ANALYSIS_RECORD_CACHE = AnalysisRecordCache()
ForensicReport = ForensicDossierPDF  # Backward-compatibility alias


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle uploads exceeding maximum allowed size."""
    return jsonify({
        "error": "File exceeds 15 MB. Please upload an image smaller than 15 MB."
    }), 413


def allowed_file(filename: str) -> bool:
    """Validate file extension against allowed forensic image formats."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- APPLICATION ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "DeepTrace AI Forensic OS",
        "version": "2.5.0",
        "architecture": "Tri-Branch Hybrid Engine (Provenance, Spectral AI, Tamper Localization)"
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded in request."}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "Empty filename provided."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported format. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400

    try:
        quality = int(request.form.get('quality', 90))
        quality = max(50, min(98, quality))
    except (ValueError, TypeError):
        quality = 90

    # Parse interactive explainability options (alpha opacity and false-color palette)
    try:
        alpha = float(request.form.get('alpha', 0.45))
        alpha = max(0.05, min(0.95, alpha))
    except (ValueError, TypeError):
        alpha = 0.45

    colormap = str(request.form.get('colormap', 'JET')).upper().strip()
    if colormap not in {'JET', 'TURBO'}:
        colormap = 'JET'

    # Create isolated request scratch directory to guarantee thread safety
    req_temp_dir = tempfile.mkdtemp(prefix='dt_req_', dir=UPLOAD_FOLDER)
    temp_evidence_path = os.path.join(req_temp_dir, f"evidence_{uuid.uuid4().hex[:8]}.jpg")

    try:
        file_bytes = file.read()
        if len(file_bytes) == 0:
            return jsonify({"error": "Uploaded file is empty (0 bytes)."}), 400

        if len(file_bytes) > 15 * 1024 * 1024:
            return jsonify({
                "error": "File exceeds 15 MB. Please upload an image smaller than 15 MB."
            }), 400

        # Validate that payload is a decodeable image
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Fast structural sanity verification
            # Re-open after verify() (Pillow requirement)
            img = Image.open(io.BytesIO(file_bytes))
        except Exception:
            return jsonify({"error": "Uploaded file is corrupted or not a valid image."}), 400

        # Write clean evidence copy
        with open(temp_evidence_path, 'wb') as f:
            f.write(file_bytes)

        # ---------------------------------------------------------
        # BRANCH 1: PROVENANCE & CRYPTOGRAPHIC VERIFICATION
        # ---------------------------------------------------------
        md5, sha256 = calculate_hashes(file_bytes)
        phash = calculate_perceptual_hash(img)
        metadata = extract_metadata(img)
        provenance_data = audit_c2pa_manifest(temp_evidence_path)

        # ---------------------------------------------------------
        # BRANCH 2A: DEEP NEURAL ATTRIBUTION (ONNX CLASSIFIER)
        # ---------------------------------------------------------
        neural_data = detect_neural_synthesis(temp_evidence_path)

        # ---------------------------------------------------------
        # BRANCH 2B: FREQUENCY DOMAIN & PHYSICAL SENSOR SCREENING
        # ---------------------------------------------------------
        frequency_data = analyze_frequency_domain(temp_evidence_path)

        # ---------------------------------------------------------
        # BRANCH 3: IMAGE TAMPERING & PHOTOSHOP LOCALIZATION
        # ---------------------------------------------------------
        tamper_data = perform_tamper_analysis(
            temp_evidence_path,
            quality=quality,
            temp_dir=req_temp_dir,
            alpha=alpha,
            colormap=colormap
        )

        # ---------------------------------------------------------
        # SPATIAL EXPLAINABILITY: AI GENERATION ATTRIBUTION
        # ---------------------------------------------------------
        ai_explain_data = generate_ai_attribution_heatmap(
            temp_evidence_path,
            colormap=colormap,
            alpha=alpha
        )

        # ---------------------------------------------------------
        # MULTI-SIGNAL FORENSIC ARBITRATOR (DUAL-SIGNAL FUSION)
        # ---------------------------------------------------------
        arbitration = arbitrate_forensic_evidence(
            provenance_data=provenance_data,
            frequency_data=frequency_data,
            tamper_data=tamper_data,
            explainability_data=ai_explain_data,
            neural_data=neural_data
        )

        # Generate persistent analysis record identifier
        analysis_id = str(uuid.uuid4())
        
        # Construct complete examination record for server-side integrity binding
        exam_record = {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "file_bytes": file_bytes,
            "original_bytes": file_bytes,
            "hashes": {
                "md5": md5,
                "sha256": sha256,
                "phash": phash
            },
            "md5": md5,
            "sha256": sha256,
            "phash": phash,
            "metadata": metadata,
            "provenance": provenance_data,
            "frequency": frequency_data,
            "neural": neural_data,
            "tamper": {
                "spatial_inconsistency": tamper_data["spatial_inconsistency"],
                "laplacian_variance": tamper_data["laplacian_variance"],
                "tamper_coverage_ratio": tamper_data["tamper_coverage_ratio"],
                "base_ela_score": tamper_data["base_ela_score"],
                "tamper_score": tamper_data["tamper_score"],
                "adaptive_quality": tamper_data.get("adaptive_quality", 90),
                "reliability_index": tamper_data.get("reliability_index", 1.0)
            },
            "explainability": {
                "attribution_peak": ai_explain_data["attribution_peak"],
                "high_attribution_ratio": ai_explain_data["high_attribution_ratio"],
                "attribution_level": ai_explain_data["attribution_level"],
                "summary": ai_explain_data["summary"],
                "colormap": colormap,
                "alpha": alpha
            },
            "ela": tamper_data["ela_b64"],
            "heatmap": tamper_data["heatmap_b64"],
            "ai_heatmap": ai_explain_data["ai_heatmap_b64"],
            "score": arbitration["composite_score"],
            "ai_score": arbitration["ai_score"],
            "neural_ai_score": arbitration.get("neural_ai_score", arbitration["ai_score"]),
            "physical_sensor_score": arbitration.get("physical_sensor_score", arbitration["ai_score"]),
            "scores": arbitration.get("scores", {}),
            "dual_telemetry": arbitration.get("dual_telemetry", {}),
            "tamper_score": arbitration["tamper_score"],
            "verdict": arbitration["verdict_label"],
            "verdict_badge": arbitration["verdict_badge"],
            "verdict_color": arbitration["verdict_color"],
            "detection_type": arbitration["detection_type"],
            "verdict_summary": arbitration["summary"],
            "badges": arbitration["badges"],
            "conformal_prediction": arbitration.get("conformal_prediction", {}),
            "telemetry": arbitration["telemetry"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "tineye": f"https://tineye.com/search/{md5}"
        }
        ANALYSIS_RECORD_CACHE.put(analysis_id, exam_record)

        return jsonify({
            "analysis_id": analysis_id,
            "hashes": {
                "md5": md5,
                "sha256": sha256,
                "phash": phash
            },
            "metadata": metadata,
            "provenance": provenance_data,
            "frequency": frequency_data,
            "neural": neural_data,
            "tamper": {
                "spatial_inconsistency": tamper_data["spatial_inconsistency"],
                "laplacian_variance": tamper_data["laplacian_variance"],
                "tamper_coverage_ratio": tamper_data["tamper_coverage_ratio"],
                "base_ela_score": tamper_data["base_ela_score"],
                "tamper_score": tamper_data["tamper_score"],
                "adaptive_quality": tamper_data.get("adaptive_quality", 90),
                "reliability_index": tamper_data.get("reliability_index", 1.0)
            },
            "explainability": {
                "attribution_peak": ai_explain_data["attribution_peak"],
                "high_attribution_ratio": ai_explain_data["high_attribution_ratio"],
                "attribution_level": ai_explain_data["attribution_level"],
                "summary": ai_explain_data["summary"],
                "colormap": colormap,
                "alpha": alpha
            },
            "ela": tamper_data["ela_b64"],
            "heatmap": tamper_data["heatmap_b64"],
            "ai_heatmap": ai_explain_data["ai_heatmap_b64"],
            "score": arbitration["composite_score"],
            "ai_score": arbitration["ai_score"],
            "neural_ai_score": arbitration.get("neural_ai_score", arbitration["ai_score"]),
            "physical_sensor_score": arbitration.get("physical_sensor_score", arbitration["ai_score"]),
            "scores": arbitration.get("scores", {}),
            "dual_telemetry": arbitration.get("dual_telemetry", {}),
            "tamper_score": arbitration["tamper_score"],
            "verdict": arbitration["verdict_label"],
            "verdict_badge": arbitration["verdict_badge"],
            "verdict_color": arbitration["verdict_color"],
            "detection_type": arbitration["detection_type"],
            "verdict_summary": arbitration["summary"],
            "badges": arbitration["badges"],
            "conformal_prediction": arbitration.get("conformal_prediction", {}),
            "telemetry": arbitration["telemetry"],
            "tineye": f"https://tineye.com/search/{md5}"
        })

    except Exception as e:
        return jsonify({"error": f"Forensic analysis failed: {str(e)}"}), 500

    finally:
        # Guarantee cleanup of request scratch directory
        if os.path.exists(req_temp_dir):
            try:
                shutil.rmtree(req_temp_dir, ignore_errors=True)
            except Exception:
                pass


@app.route('/download_report', methods=['POST'])
def download_report():
    data = request.json or {}
    analysis_id = data.get('analysis_id')
    cached_record = ANALYSIS_RECORD_CACHE.get(analysis_id) if analysis_id else None

    if cached_record:
        report_data = dict(cached_record)
        # Allow client-selected UI visual preferences if provided
        if 'active_image' in data:
            report_data['active_image'] = data['active_image']
        if 'active_mode' in data:
            report_data['active_mode'] = data['active_mode']
        if 'colormap' in data:
            report_data['colormap'] = data['colormap']
    else:
        # 100% backward-compatible fallback for raw JSON payloads
        report_data = data

    pdf_buffer = generate_forensic_dossier_pdf(report_data)

    md5_tag = str(
        report_data.get('hashes', {}).get('md5')
        or report_data.get('md5')
        or 'dossier'
    )[:8]

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"DeepTrace_Dossier_{md5_tag}.pdf",
        mimetype='application/pdf'
    )


def main():
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() in ('true', '1')
    host = os.environ.get('HOST', '0.0.0.0')  # nosec B104
    port = int(os.environ.get('PORT', 8501))
    app.run(host=host, port=port, debug=debug_mode)  # nosec B201


if __name__ == '__main__':
    main()
