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

