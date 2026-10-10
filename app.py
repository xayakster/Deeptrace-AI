"""
DeepTrace AI v2.5 — Tri-Branch Forensic Engine & Web Application
AI-Powered Digital Media Forensics & Source Tracking System
"""

import os
import io
import uuid
import base64
import shutil
import tempfile
from typing import Dict, Any
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF

# Import modular forensics engine
from forensics import (
    calculate_hashes,
    calculate_perceptual_hash,
    extract_metadata,
    audit_c2pa_manifest,
    analyze_frequency_domain,
    perform_tamper_analysis,
    generate_ai_attribution_heatmap,
    arbitrate_forensic_evidence,
)

# Configure Decompression Bomb Protection
Image.MAX_IMAGE_PIXELS = 50_000_000

app = Flask(
    __name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

# Application Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Validate file extension against allowed forensic image formats."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- PDF FORENSIC DOSSIER GENERATOR ---

class ForensicReport(FPDF):
    """Programmatic PDF Forensic Report Generator for DeepTrace AI."""

    def header(self):
        self.set_font('Courier', 'B', 15)
        self.set_text_color(20, 20, 20)
        self.cell(0, 10, 'DEEPTRACE AI - FORENSIC DOSSIER', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_draw_color(0, 242, 255)
        self.set_line_width(0.8)
        self.line(10, 22, 200, 22)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'DeepTrace Forensic OS v2.5 - Confidential - Page {self.page_no()}', new_x="RIGHT", new_y="TOP", align='C')


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
        # BRANCH 2: FREQUENCY DOMAIN & SPECTRAL AI SCREENING
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
        # MULTI-SIGNAL FORENSIC ARBITRATOR
        # ---------------------------------------------------------
        arbitration = arbitrate_forensic_evidence(
            provenance_data=provenance_data,
            frequency_data=frequency_data,
            tamper_data=tamper_data,
            explainability_data=ai_explain_data
        )

        return jsonify({
            "hashes": {
                "md5": md5,
                "sha256": sha256,
                "phash": phash
            },
            "metadata": metadata,
            "provenance": provenance_data,
            "frequency": frequency_data,
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
    score_clean = str(data.get('score', '0')).replace('%', '').strip()
    try:
        score_val = float(score_clean)
    except ValueError:
        score_val = 0.0

    verdict_label = data.get('verdict', 'INCONCLUSIVE')
    verdict_badge = data.get('verdict_badge', 'INCONCLUSIVE')
    detection_type = data.get('detection_type', 'N/A')
    summary_text = data.get('verdict_summary', 'Forensic analysis completed.')

    ai_score = data.get('ai_score', 'N/A')
    tamper_score = data.get('tamper_score', 'N/A')

    telemetry = data.get('telemetry', {})
    z_score = telemetry.get('spatial_inconsistency', 'N/A')
    lap_var = telemetry.get('laplacian_variance', 'N/A')
    spectral_peak = telemetry.get('spectral_peak_ratio', 'N/A')
    coverage_ratio = telemetry.get('tamper_coverage_ratio', '0.0')

    provenance = data.get('provenance', {})
    has_c2pa = provenance.get('has_c2pa', False)
    c2pa_status = provenance.get('details', 'No C2PA manifest found.')
    c2pa_gen = provenance.get('generator', 'N/A')

    pdf = ForensicReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Section 1: Case Details
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Courier", size=10)
    pdf.cell(0, 6, f"TIMESTAMP: {data.get('timestamp', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"CASE ID:   DT-2026-CYBER", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"ENGINE:    DeepTrace Forensic OS v2.5 (Tri-Branch Architecture)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 2: Cryptographic Signatures
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "1. CRYPTOGRAPHIC SIGNATURES & HASH CHAIN", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=9)
    pdf.cell(0, 5, f"MD5 Digest:        {data.get('md5', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"SHA-256 Digest:    {data.get('sha256', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Perceptual dHash:  {data.get('phash', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Section 3: C2PA Content Credentials
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "2. C2PA PROVENANCE & CONTENT CREDENTIALS AUDIT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=9)
    pdf.cell(0, 5, f"Manifest Present:  {'YES' if has_c2pa else 'NO'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Claim Generator:   {c2pa_gen}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Validation State:  {provenance.get('validation_state', 'NONE')}", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 5, f"Provenance Audit:  {c2pa_status}")
    pdf.ln(4)

    # Section 4: Calibrated Verdict & Score Breakdown
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "3. CALIBRATED FORENSIC VERDICT & MULTI-BRANCH SCORES", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=10)
    pdf.cell(0, 6, f"COMPOSITE SUSPICION:  {score_val:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"CLASSIFICATION:       {verdict_label}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"DECISION TIER:        {verdict_badge}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"DETECTION SUB-TYPE:   {detection_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"AI SYNTHESIS INDEX:   {ai_score}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"TAMPERING INDEX:      {tamper_score}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 4b: Conformal Uncertainty Guarantee
    conformal = data.get('conformal_prediction', {})
    conf_set = ", ".join(conformal.get('prediction_set', [detection_type]))
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "4. CONFORMAL UNCERTAINTY GUARANTEE (95% COVERAGE)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=9)
    pdf.cell(0, 5, f"Coverage Guarantee:   95.0% Marginal Confidence", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Guaranteed Set:       [{conf_set}]", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Status Assessment:    {conformal.get('status_label', 'DECISIVE EVALUATION')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 5: Quantitative Physical & Structural Telemetry
    npr_cov = telemetry.get('npr_covariance_score', 'N/A')
    rel_idx = telemetry.get('reliability_index', '1.0')
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "5. QUANTITATIVE PHYSICAL & STRUCTURAL TELEMETRY", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=9)
    pdf.cell(0, 5, f"Spatial Inconsistency (Z-Score): {z_score} (Tamper Cutoff: > 3.2)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Texture Reliability Index:      {rel_idx} (TruFor Anomaly Weight)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Sensor Noise Texture Variance:  {lap_var} (AI Void Cutoff: < 45.0)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"2D-FFT Spectral Peak Ratio:     {spectral_peak} (Lattice Anomaly: > 0.38)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"NPR Structural Covariance:      {npr_cov} (DiT Upsample Anomaly: > 0.65)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Tamper Heatmap Coverage:        {coverage_ratio}% of total canvas", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 6: Findings & Legal Interpretation
    pdf.set_font("Courier", 'B', 11)
    pdf.cell(0, 7, "6. FORENSIC FINDINGS & SCIENTIFIC SUMMARY", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", size=9)
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(3)

    # Section 7: Visual Forensic Evidence & Spatial Overlay Attachment
    visual_b64 = data.get('active_image') or data.get('heatmap') or data.get('ai_heatmap')
    if visual_b64 and len(str(visual_b64)) > 100:
        try:
            raw_b64 = str(visual_b64).split(',')[-1]
            img_bytes = base64.b64decode(raw_b64)
            img_stream = io.BytesIO(img_bytes)
            pdf.add_page()
            pdf.set_font("Courier", 'B', 11)
            pdf.cell(0, 7, "6. VISUAL FORENSIC EVIDENCE EXHIBIT", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Courier", size=9)
            mode_tag = str(data.get('active_mode', 'SPATIAL OVERLAY')).upper()
            pdf.cell(0, 5, f"EXHIBIT TYPE: Primary Visual Matrix [{mode_tag}]", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            pdf.image(img_stream, x=15, y=38, w=180)
            pdf.ln(130)
        except Exception:
            pass

    disclaimer = (
        "EVIDENTIARY NOTICE: This report represents digital forensic analysis performed using "
        "passive statistical feature extraction, 2D Discrete Fourier Transforms, block-level Error "
        "Level Analysis, spatial feature attribution, and C2PA Content Credentials. Unless backed "
        "by a cryptographically signed hardware manifest or exact cryptographic source match, "
        "findings represent probabilistic evidence in accordance with digital forensics best practices."
    )
    pdf.set_text_color(120, 120, 120)
    pdf.set_font("Courier", 'I', 8)
    pdf.multi_cell(0, 4, disclaimer)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="DeepTrace_Forensic_Dossier.pdf",
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)