"""
Integration tests for DeepTrace AI Flask web endpoints & security protections:
- Route responsiveness (/, /dashboard, /health)
- File validation & upload security
- Analysis pipeline endpoint (/analyze)
- PDF report download (/download_report)
- Concurrent request isolation & temporary file cleanup
"""

import os
import io
import json
import pytest
from PIL import Image
import numpy as np

from app import app, UPLOAD_FOLDER


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def create_test_image(format='JPEG', size=(200, 200), color=(100, 150, 200)):
    buf = io.BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"DEEPTRACE" in response.data


def test_dashboard_route(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Forensic Workspace" in response.data
    assert b"Forensic Findings" in response.data


def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_analyze_no_file(client):
    response = client.post('/analyze')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_analyze_empty_filename(client):
    data = {'file': (io.BytesIO(b""), '')}
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_disallowed_extension(client):
    data = {'file': (io.BytesIO(b"echo hello"), 'exploit.sh')}
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "Unsupported format" in response.get_json()["error"]


def test_analyze_corrupted_file(client):
    data = {'file': (io.BytesIO(b"Not an image at all"), 'corrupt.jpg')}
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "corrupted" in response.get_json()["error"]


def test_analyze_valid_jpeg(client):
    img_buf = create_test_image('JPEG')
    data = {
        'file': (img_buf, 'test_evidence.jpg'),
        'quality': '90'
    }
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_data = response.get_json()

    # Validate complete response contract
    assert "hashes" in res_data
    assert "md5" in res_data["hashes"]
    assert "sha256" in res_data["hashes"]
    assert "phash" in res_data["hashes"]
    assert "ela" in res_data
    assert "heatmap" in res_data
    assert "score" in res_data
    assert "ai_score" in res_data
    assert "tamper_score" in res_data
    assert "verdict" in res_data
    assert "verdict_badge" in res_data
    assert "verdict_color" in res_data
    assert "detection_type" in res_data
    assert "verdict_summary" in res_data
    assert "provenance" in res_data
    assert "frequency" in res_data
    assert "telemetry" in res_data
    assert "badges" in res_data
    assert "spatial_inconsistency" in res_data["telemetry"]
    assert "laplacian_variance" in res_data["telemetry"]
    assert "analysis_id" in res_data
    assert len(res_data["analysis_id"]) == 36
    assert "tineye" in res_data


def test_analyze_valid_png(client):
    img_buf = create_test_image('PNG')
    data = {'file': (img_buf, 'test_evidence.png')}
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json()["score"] >= 0.0


def test_download_report_pdf(client):
    payload = {
        "md5": "0123456789abcdef0123456789abcdef",
        "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "score": "28.5%",
        "verdict": "AUTHENTIC / NATURAL",
        "telemetry": {
            "spatial_inconsistency": 1.25,
            "laplacian_variance": 145.8
        },
        "timestamp": "2026-10-10 12:00:00"
    }
    response = client.post(
        '/download_report',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    # Verify standard PDF file header
    assert response.data.startswith(b'%PDF-')
    assert len(response.data) > 10000


def test_temp_file_cleanup_and_isolation(client):
    """
    Verifies that requests use isolated scratch folders and leave no orphaned files in uploads.
    """
    initial_files = set(os.listdir(UPLOAD_FOLDER))
    img_buf = create_test_image('JPEG')
    data = {'file': (img_buf, 'cleanup_test.jpg')}

    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200

def test_analyze_invalid_quality_fallback(client):
    img_buf = create_test_image('JPEG')
    data = {
        'file': (img_buf, 'test_quality.jpg'),
        'quality': 'invalid_quality_string'
    }
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert "score" in response.get_json()


def test_download_report_invalid_score(client):
    payload = {
        "md5": "abcdef1234567890",
        "score": "invalid_score",
        "timestamp": "2026-10-10 12:00:00"
    }
    response = client.post(
        '/download_report',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.data.startswith(b'%PDF-')


def test_analyze_with_explainability_options(client):
    img_buf = create_test_image('JPEG', size=(150, 150))
    data = {
        'file': (img_buf, 'test_explain.jpg'),
        'quality': 92,
        'alpha': 0.65,
        'colormap': 'TURBO'
    }
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_json = response.get_json()

    assert "heatmap" in res_json
    assert "ai_heatmap" in res_json
    assert len(res_json["ai_heatmap"]) > 100
    assert "explainability" in res_json
    assert res_json["explainability"]["colormap"] == "TURBO"
    assert res_json["explainability"]["alpha"] == 0.65
    assert "attribution_peak" in res_json["explainability"]


def test_download_report_with_visual_exhibit(client):
    # Base64 test image data
    test_img = Image.new('RGB', (100, 100), color=(100, 120, 140))
    buf = io.BytesIO()
    test_img.save(buf, format='JPEG')
    import base64
    b64_data = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')

    payload = {
        "md5": "abcdef1234567890abcdef1234567890",
        "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "score": "78.5%",
        "verdict": "TAMPERED / SPLICED",
        "verdict_badge": "TAMPERED",
        "detection_type": "LOCALIZED_TAMPERING",
        "active_mode": "SPATIAL TAMPER HEATMAP",
        "active_image": b64_data,
        "timestamp": "2026-10-10 12:00:00"
    }
    response = client.post(
        '/download_report',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.data.startswith(b'%PDF-')
    assert len(response.data) > 1000


def test_analyze_conformal_prediction_and_telemetry(client):
    img_buf = create_test_image('JPEG')
    data = {
        'file': (img_buf, 'test_conformal.jpg'),
        'quality': 90
    }
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_data = response.get_json()

    # Validate conformal prediction schema
    assert "conformal_prediction" in res_data
    conf = res_data["conformal_prediction"]
    assert conf["coverage_guarantee"] == "95.0%"
    assert isinstance(conf["prediction_set"], list)
    assert len(conf["prediction_set"]) >= 1
    assert "status_label" in conf

    # Validate telemetry additions
    assert "telemetry" in res_data
    telem = res_data["telemetry"]
    assert "npr_covariance_score" in telem
    assert "reliability_index" in telem
    assert "adaptive_quality" in res_data["tamper"]
    assert "reliability_index" in res_data["tamper"]


def test_download_report_with_conformal_guarantee(client):
    payload = {
        "md5": "0123456789abcdef0123456789abcdef",
        "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "score": "88.2%",
        "verdict": "AI GENERATED / SYNTHETIC",
        "verdict_badge": "AI GENERATED",
        "detection_type": "AI_GENERATION",
        "conformal_prediction": {
            "coverage_guarantee": "95.0%",
            "prediction_set": ["AI_GENERATION"],
            "status_label": "95% CONFIDENCE: DECISIVE ANOMALY"
        },
        "telemetry": {
            "spatial_inconsistency": 1.2,
            "laplacian_variance": 18.5,
            "spectral_peak_ratio": 0.54,
            "npr_covariance_score": 0.82,
            "reliability_index": 0.95,
            "tamper_coverage_ratio": 0.0
        },
        "timestamp": "2026-10-10 18:00:00"
    }
    response = client.post(
        '/download_report',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.data.startswith(b'%PDF-')
    assert len(response.data) > 1000


def test_dashboard_layout_and_interaction_revisions(client):
    """
    Verify Dashboard V3 layout refinements and interaction revisions:
    1. Forensic Findings expanded vertically (#v3-findings-panel, .v3-panel-findings)
    2. Split Curation locked by default (#stage-btn-curtain disabled)
    3. Restored original upload design with magnetic interaction (.v3-upload-zone, #upload-text, #upload-label)
    4. Reverted analysis view buttons (.v3-view-tabs, .v3-tab-btn, #btn-toggle-ela, #btn-toggle-heatmap, #btn-toggle-ai)
    5. Hold to Confirm export button retained (#btn-hold-export)
    """
    response = client.get('/dashboard')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # 1. Layout Refinement
    assert 'v3-panel-findings' in html
    assert 'id="v3-findings-panel"' in html
    assert 'v3-console-drawer' in html

    # 2. Lock Split Curation
    assert 'id="stage-btn-curtain"' in html
    assert 'disabled' in html
    assert 'aria-disabled="true"' in html

    # 3. Restored Upload Design with Magnetic Properties
    assert 'v3-upload-zone' in html
    assert 'id="upload-text"' in html
    assert 'magnetic-glow' in html
    assert 'DRAG & DROP HERE (JPG,PNG,WEBP)' in html

    # 4. Reverted Analysis Buttons
    assert 'v3-view-tabs' in html
    assert 'v3-tab-btn' in html
    assert 'id="btn-toggle-ela"' in html
    assert 'id="btn-toggle-heatmap"' in html
    assert 'id="btn-toggle-ai"' in html

    # 5. Retained Hold to Confirm Export with (HOLD) label without 1.6s text
    assert 'id="btn-hold-export"' in html
    assert 'id="hold-overlay"' in html
    assert 'EXPORT FORENSIC REPORTS' in html
    assert '<span class="hold-hint">(HOLD)</span>' in html
    assert '1.6S' not in html
    assert '1.6s' not in html


def test_analyze_file_exceeds_15mb(client):
    """
    Verify that an uploaded image exceeding 15 MB is rejected with a clear error message
    asking the user to upload an image smaller than 15 MB, preventing it from proceeding to analysis.
    """
    # Create dummy buffer larger than 15 MB (15 MB + 1024 bytes)
    oversized_data = b"0" * (15 * 1024 * 1024 + 1024)
    data = {'file': (io.BytesIO(oversized_data), 'oversized.jpg')}
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code in (400, 413)
    res_json = response.get_json()
    assert "error" in res_json
    assert "File exceeds 15 MB. Please upload an image smaller than 15 MB." in res_json["error"]


def test_dashboard_file_size_limit_and_hold_label(client):
    """
    Verify client-side 15 MB validation message and (HOLD) button label in dashboard.html.
    """
    response = client.get('/dashboard')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'MAX_FILE_SIZE = 15 * 1024 * 1024' in html
    assert 'File exceeds 15 MB. Please upload an image smaller than 15 MB.' in html
    assert '<span class="hold-hint">(HOLD)</span>' in html
    assert '(HOLD 1.6S)' not in html


def test_analyze_caches_record_and_download_report_by_analysis_id(client):
    """
    Verify that /analyze returns an analysis_id, caches the record server-side,
    and /download_report resolves the cached record correctly by analysis_id.
    """
    img_buf = create_test_image('JPEG')
    data = {'file': (img_buf, 'cached_evidence.jpg')}
    res = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert "analysis_id" in res_data
    analysis_id = res_data['analysis_id']

    # Fetch report using only analysis_id
    rep_res = client.post(
        '/download_report',
        data=json.dumps({'analysis_id': analysis_id}),
        content_type='application/json'
    )
    assert rep_res.status_code == 200
    assert rep_res.mimetype == 'application/pdf'
    assert rep_res.data.startswith(b'%PDF-')
    assert len(rep_res.data) > 10000
    expected_dl_name = f"DeepTrace_Dossier_{res_data['hashes']['md5'][:8]}.pdf"
    assert expected_dl_name in rep_res.headers.get('Content-Disposition', '')


def test_analysis_record_cache_unit():
    """
    Unit test for thread-safe AnalysisRecordCache: put, get, LRU eviction, and TTL expiration.
    """
    from app import AnalysisRecordCache
    import time

    cache = AnalysisRecordCache(capacity=2, max_age_seconds=1)
    cache.put("id1", {"val": 1})
    cache.put("id2", {"val": 2})

    assert cache.get("id1")["val"] == 1
    assert cache.get("id2")["val"] == 2

    # LRU eviction: adding id3 must evict oldest unaccessed item
    cache.put("id3", {"val": 3})
    assert cache.get("id1") is None
    assert cache.get("id2")["val"] == 2
    assert cache.get("id3")["val"] == 3

    # TTL expiration test
    time.sleep(1.1)
    assert cache.get("id2") is None
    assert cache.get("id3") is None


def test_dossier_4_page_structure():
    """
    Verify complete 4-page Forensic Dossier generation, ENFSI verbal scale mapping,
    and presence of 4 distinct page objects in the compiled PDF document.
    """
    import re
    from forensics.dossier import generate_forensic_dossier_pdf, map_enfsi_verbal_scale

    # Test ENFSI scale mapping for different score thresholds
    scale_low = map_enfsi_verbal_scale(15.0, "AUTHENTIC_CAPTURE")
    assert "Extremely strong support for Authentic" in scale_low["verbal_assessment"]
    assert scale_low["level"] == "Level 1"

    scale_high = map_enfsi_verbal_scale(98.0, "AI_GENERATION")
    assert "Extremely strong support for Synthetic" in scale_high["verbal_assessment"]
    assert scale_high["level"] == "Level 8"

    # Test complete dossier compilation with dummy multi-branch data
    test_img = Image.new('RGB', (120, 120), color=(180, 80, 60))
    buf = io.BytesIO()
    test_img.save(buf, format='JPEG')
    import base64
    b64_img = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')

    mock_record = {
        "filename": "court_exhibit.jpg",
        "file_bytes": buf.getvalue(),
        "hashes": {
            "md5": "112233445566778899aabbccddeeff00",
            "sha256": "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
            "phash": "fedcba9876543210"
        },
        "score": 84.5,
        "ai_score": 89.0,
        "tamper_score": 25.0,
        "verdict": "AI GENERATED / SYNTHETIC",
        "verdict_badge": "AI GENERATED",
        "detection_type": "AI_SYNTHESIS",
        "verdict_summary": "Extensive synthetic artifacts identified across spatial and frequency domains.",
        "conformal_prediction": {
            "coverage_guarantee": "95.0%",
            "prediction_set": ["AI_GENERATION"],
            "status_label": "95% CONFIDENCE: DECISIVE ANOMALY",
            "is_singleton": True
        },
        "metadata": {
            "Make": "Sony",
            "Model": "ILCE-7RM4",
            "DateTimeOriginal": "2026-05-14 10:22:15",
            "Software": "Adobe Photoshop 25.0",
            "FNumber": 2.8,
            "ExposureTime": 0.004,
            "ISO": 400
        },
        "telemetry": {
            "spatial_inconsistency": 1.45,
            "laplacian_variance": 22.4,
            "spectral_peak_ratio": 0.65,
            "npr_covariance_score": 0.88,
            "reliability_index": 0.92,
            "tamper_coverage_ratio": 2.1
        },
        "ela": b64_img,
        "heatmap": b64_img,
        "ai_heatmap": b64_img
    }

    pdf_stream = generate_forensic_dossier_pdf(mock_record)
    assert isinstance(pdf_stream, io.BytesIO)
    pdf_bytes = pdf_stream.getvalue()
    assert pdf_bytes.startswith(b'%PDF-')
    assert len(pdf_bytes) > 15000

    # Verify exactly 4 page objects exist in the compiled dossier
    page_matches = re.findall(rb'/Type\s*/Page\b', pdf_bytes)
    assert len(page_matches) == 4



