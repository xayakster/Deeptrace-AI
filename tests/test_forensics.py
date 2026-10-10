"""
Unit tests for DeepTrace AI Tri-Branch modular forensic engine:
- Branch 1: Cryptographic hashes, perceptual dHash, EXIF, C2PA manifest auditing
- Branch 2: 2D-FFT azimuthal power spectrum & spectral lattice peak detection
- Branch 3: Spatial block Z-score, Laplacian sensor noise, colorized tamper heatmap overlay
- Arbitration: Multi-Signal Forensic Arbitrator fusing AI & manipulation signals
"""

import os
import io
import tempfile
import numpy as np
from PIL import Image
import pytest

from app import allowed_file
from forensics import (
    calculate_hashes,
    calculate_perceptual_hash,
    extract_metadata,
    audit_c2pa_manifest,
    analyze_frequency_domain,
    compute_laplacian_noise_variance,
    compute_block_anomaly_grid,
    generate_tamper_heatmap_overlay,
    generate_ai_attribution_heatmap,
    generate_ai_attribution_overlay,
    compute_patch_synthesis_attribution,
    perform_tamper_analysis,
    arbitrate_forensic_evidence,
)
from forensics.frequency import compute_azimuthal_average, detect_spectral_lattice_peaks, compute_npr_covariance_score
from forensics.tampering import (
    estimate_original_jpeg_quality,
    compute_texture_reliability_mask,
    compute_multiscale_block_anomaly,
)
from forensics.arbitrator import compute_conformal_prediction_set


def test_allowed_file():
    assert allowed_file("evidence.jpg") is True
    assert allowed_file("sample.JPEG") is True
    assert allowed_file("capture.png") is True
    assert allowed_file("photo.webp") is True
    assert allowed_file("malicious.exe") is False
    assert allowed_file("script.py") is False
    assert allowed_file("no_extension") is False


def test_calculate_hashes():
    data = b"DeepTrace Forensic Cryptographic Test"
    md5, sha256 = calculate_hashes(data)
    
    assert len(md5) == 32
    assert len(sha256) == 64
    assert md5 == "d847509f6706bd54e5c0eb06a6ba8046"
    assert sha256 == "2cc266dedea452b35001d31e3ff664b4090819ed453a2395e2387a31a23208b5"


def test_calculate_perceptual_hash():
    img1 = Image.new('RGB', (100, 100), color=(128, 128, 128))
    phash1 = calculate_perceptual_hash(img1)
    assert len(phash1) == 16  # 64-bit hex string

    # Slightly resized identical image should retain consistent or near-identical pHash
    img2 = img1.resize((150, 150))
    phash2 = calculate_perceptual_hash(img2)
    assert phash1 == phash2


def test_extract_metadata_no_exif():
    img = Image.new('RGB', (100, 100), color=(200, 200, 200))
    metadata = extract_metadata(img)
    assert isinstance(metadata, dict)
    assert "Status" in metadata or len(metadata) == 0


def test_audit_c2pa_manifest_plain_asset():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "plain.jpg")
        Image.new('RGB', (100, 100), color=(50, 100, 150)).save(p, 'JPEG')
        c2pa_data = audit_c2pa_manifest(p)
        assert isinstance(c2pa_data, dict)
        assert "has_c2pa" in c2pa_data
        assert c2pa_data["has_c2pa"] is False
        assert c2pa_data["is_ai_claimed"] is False


def test_frequency_azimuthal_average():
    # Synthetic circular symmetric spectrum
    spectrum = np.zeros((128, 128), dtype=np.float32)
    y, x = np.indices((128, 128))
    r = np.sqrt((x - 64)**2 + (y - 64)**2)
    spectrum[r < 40] = 50.0

    profile = compute_azimuthal_average(spectrum)
    assert len(profile) == 64
    assert profile[10] > 0.0


def test_detect_spectral_lattice_peaks():
    # Spectrum with sharp isolated high-frequency spike
    spectrum = np.full((128, 128), 10.0, dtype=np.float32)
    spectrum[20, 20] = 100.0  # Simulated high-frequency periodic peak
    spectrum[108, 108] = 100.0

    peak_prominence, high_ratio, slope = detect_spectral_lattice_peaks(spectrum)
    assert peak_prominence > 0.30


def test_analyze_frequency_domain():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "freq_test.jpg")
        Image.new('RGB', (128, 128), color=(100, 100, 100)).save(p, 'JPEG')
        freq_res = analyze_frequency_domain(p)
        assert "spectral_peak_ratio" in freq_res
        assert "frequency_ai_score" in freq_res
        assert 0.0 <= freq_res["frequency_ai_score"] <= 100.0


def test_compute_laplacian_noise_variance():
    with tempfile.TemporaryDirectory() as td:
        # Flat image (zero texture noise -> should be close to 0)
        flat_path = os.path.join(td, "flat.jpg")
        Image.new('RGB', (200, 200), color=(128, 128, 128)).save(flat_path, 'JPEG', quality=95)
        var_flat = compute_laplacian_noise_variance(flat_path)
        assert var_flat < 45.0

        # Highly textured noise image (simulating camera optical grain)
        noise_arr = np.random.normal(128, 15, (200, 200, 3)).clip(0, 255).astype(np.uint8)
        noise_path = os.path.join(td, "noise.jpg")
        Image.fromarray(noise_arr).save(noise_path, 'JPEG', quality=95)
        var_noise = compute_laplacian_noise_variance(noise_path)
        assert var_noise > 100.0


def test_compute_block_anomaly_grid():
    # 1. Uniform difference matrix (no localized tampering)
    uniform_ela = Image.new('RGB', (256, 256), color=(10, 10, 10))
    z_max, grid = compute_block_anomaly_grid(uniform_ela, block_size=32)
    assert z_max <= 1.8

    # 2. Localized tamper patch (spliced 64x64 block on 512x512 canvas)
    arr = np.full((512, 512, 3), 5, dtype=np.uint8)
    arr[128:192, 128:192] = 120  # Bright anomalous ELA residual patch
    spliced_ela = Image.fromarray(arr)
    z_spliced, grid_spliced = compute_block_anomaly_grid(spliced_ela, block_size=32)
    assert z_spliced > 3.2


def test_generate_tamper_heatmap_overlay():
    orig = Image.new('RGB', (128, 128), color=(100, 150, 200))
    z_matrix = np.full((4, 4), 3.5, dtype=np.float32)
    heatmap_b64, coverage = generate_tamper_heatmap_overlay(orig, z_matrix, 3.5)
    assert isinstance(heatmap_b64, str)
    assert len(heatmap_b64) > 100
    assert coverage > 0.0


def test_perform_tamper_analysis():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "tamper_test.jpg")
        Image.new('RGB', (256, 256), color=(120, 120, 120)).save(p, 'JPEG', quality=90)
        res = perform_tamper_analysis(p, quality=90, temp_dir=td)
        assert "ela_b64" in res
        assert "heatmap_b64" in res
        assert "spatial_inconsistency" in res
        assert "laplacian_variance" in res
        assert "tamper_score" in res


def test_arbitrate_forensic_evidence_authentic():
    prov = {"has_c2pa": False, "is_ai_claimed": False, "is_hardware_camera": False}
    freq = {"frequency_ai_score": 15.0, "is_spectral_anomaly": False, "spectral_peak_ratio": 0.12}
    tamp = {
        "tamper_score": 14.0,
        "spatial_inconsistency": 0.4,
        "laplacian_variance": 420.0,
        "ela_std": 1.2,
        "tamper_coverage_ratio": 0.0
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert arb["composite_score"] <= 35.0
    assert arb["verdict_badge"] == "AUTHENTIC"
    assert arb["detection_type"] == "AUTHENTIC_CAPTURE"
    assert arb["verdict_color"] == "#00ff66"


def test_arbitrate_forensic_evidence_ai_synthetic():
    prov = {"has_c2pa": False, "is_ai_claimed": False, "is_hardware_camera": False}
    freq = {"frequency_ai_score": 85.0, "is_spectral_anomaly": True, "spectral_peak_ratio": 0.65}
    tamp = {
        "tamper_score": 12.0,
        "spatial_inconsistency": 0.5,
        "laplacian_variance": 22.0,  # Sensor noise void
        "ela_std": 0.4,
        "tamper_coverage_ratio": 0.0
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert arb["composite_score"] > 65.0
    assert arb["verdict_badge"] == "AI GENERATED"
    assert arb["detection_type"] == "AI_GENERATION"
    assert arb["verdict_color"] == "#ff2e2e"


def test_arbitrate_forensic_evidence_spliced():
    prov = {"has_c2pa": False, "is_ai_claimed": False, "is_hardware_camera": False}
    freq = {"frequency_ai_score": 18.0, "is_spectral_anomaly": False, "spectral_peak_ratio": 0.15}
    tamp = {
        "tamper_score": 78.0,
        "spatial_inconsistency": 4.1,  # Strong localized spatial outlier
        "laplacian_variance": 210.0,
        "ela_std": 2.5,
        "tamper_coverage_ratio": 12.5
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert arb["composite_score"] > 65.0
    assert arb["verdict_badge"] == "TAMPERED"
    assert arb["detection_type"] == "LOCALIZED_TAMPERING"


def test_arbitrate_forensic_evidence_c2pa_ai():
    prov = {
        "has_c2pa": True,
        "is_ai_claimed": True,
        "generator": "DALL-E 3",
        "validation_state": "VALID"
    }
    freq = {"frequency_ai_score": 50.0, "is_spectral_anomaly": False, "spectral_peak_ratio": 0.2}
    tamp = {
        "tamper_score": 10.0,
        "spatial_inconsistency": 0.2,
        "laplacian_variance": 30.0,
        "ela_std": 0.5,
        "tamper_coverage_ratio": 0.0
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert arb["composite_score"] == 99.8
    assert "AI GENERATED" in arb["verdict_label"]
    assert arb["detection_type"] == "AI_GENERATION"


def test_arbitrate_forensic_evidence_c2pa_camera():
    prov = {
        "has_c2pa": True,
        "is_ai_claimed": False,
        "is_hardware_camera": True,
        "generator": "Leica M11-P",
        "validation_state": "VALID"
    }
    freq = {"frequency_ai_score": 15.0, "is_spectral_anomaly": False, "spectral_peak_ratio": 0.1}
    tamp = {
        "tamper_score": 12.0,
        "spatial_inconsistency": 0.3,
        "laplacian_variance": 500.0,
        "ela_std": 1.5,
        "tamper_coverage_ratio": 0.0
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert arb["composite_score"] <= 20.0
    assert "AUTHENTIC" in arb["verdict_badge"]
    assert arb["detection_type"] == "AUTHENTIC_CAPTURE"


def test_arbitrate_forensic_evidence_resaved_inconclusive():
    prov = {"has_c2pa": False, "is_ai_claimed": False, "is_hardware_camera": False}
    freq = {"frequency_ai_score": 42.0, "is_spectral_anomaly": False, "spectral_peak_ratio": 0.25}
    tamp = {
        "tamper_score": 52.0,
        "spatial_inconsistency": 2.2,
        "laplacian_variance": 80.0,
        "ela_std": 1.6,
        "tamper_coverage_ratio": 1.2
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp)
    assert 35.0 < arb["composite_score"] <= 65.0
    assert arb["verdict_badge"] == "INCONCLUSIVE"
    assert arb["detection_type"] == "RESAVED_MEDIA"


def test_frequency_domain_missing_image():
    res = analyze_frequency_domain("non_existent_file_path_12345.jpg")
    assert res["is_spectral_anomaly"] is False
    assert "Unable to read" in res["spectral_summary"]


def test_laplacian_variance_missing_image():
    var = compute_laplacian_noise_variance("non_existent_file_path_12345.jpg")
    assert var == 0.0


def test_compute_block_anomaly_grid_small_dimensions():
    tiny_img = Image.new('RGB', (16, 16), color=(50, 50, 50))
    z_max, grid = compute_block_anomaly_grid(tiny_img, block_size=32)
    assert z_max == 0.0
    assert grid.shape == (1, 1)


def test_generate_tamper_heatmap_overlay_colormaps_and_alpha():
    img = Image.new('RGB', (128, 128), color=(200, 200, 200))
    z_matrix = np.random.uniform(0.0, 3.5, size=(4, 4)).astype(np.float32)
    
    # Test JET colormap with alpha=0.50
    jet_b64, coverage_jet = generate_tamper_heatmap_overlay(img, z_matrix, z_max=3.2, alpha=0.50, colormap="JET")
    assert len(jet_b64) > 100
    assert isinstance(coverage_jet, float)

    # Test TURBO colormap with alpha=0.30
    turbo_b64, coverage_turbo = generate_tamper_heatmap_overlay(img, z_matrix, z_max=3.2, alpha=0.30, colormap="TURBO")
    assert len(turbo_b64) > 100
    assert isinstance(coverage_turbo, float)


def test_generate_ai_attribution_heatmap_success():
    img = Image.new('RGB', (128, 128), color=(140, 140, 140))
    res = generate_ai_attribution_heatmap(img, colormap="TURBO", alpha=0.45)

    assert "ai_heatmap_b64" in res
    assert len(res["ai_heatmap_b64"]) > 100
    assert "attribution_peak" in res
    assert res["colormap"] == "TURBO"
    assert res["alpha"] == 0.45
    assert res["attribution_level"] in {"LOW", "MODERATE", "HIGH"}


def test_generate_ai_attribution_heatmap_error_handling():
    res = generate_ai_attribution_heatmap("non_existent_file_path_9999.jpg")
    assert res["attribution_level"] == "ERROR"
    assert res["attribution_peak"] == 0.0
    assert "failed" in res["summary"].lower()


def test_arbitrate_forensic_evidence_with_explainability():
    prov = {"has_c2pa": False, "is_ai_claimed": False, "is_hardware_camera": False}
    freq = {"frequency_ai_score": 85.0, "is_spectral_anomaly": True, "spectral_peak_ratio": 0.65}
    tamp = {
        "tamper_score": 20.0,
        "spatial_inconsistency": 0.8,
        "laplacian_variance": 12.0,
        "ela_std": 0.5,
        "tamper_coverage_ratio": 0.0
    }
    exp = {
        "attribution_peak": 0.88,
        "high_attribution_ratio": 32.5,
        "attribution_level": "HIGH"
    }
    arb = arbitrate_forensic_evidence(prov, freq, tamp, explainability_data=exp)
    assert arb["composite_score"] >= 75.0
    assert "telemetry" in arb
    assert arb["telemetry"]["ai_attribution_peak"] == 0.88
    assert arb["telemetry"]["ai_attribution_coverage"] == 32.5
    assert any("AI ATTRIBUTION PEAK" in b["label"] for b in arb["badges"])


def test_estimate_original_jpeg_quality():
    # 1. Uncompressed / memory image without DQT defaults to 90
    img_plain = Image.new('RGB', (100, 100), color=(120, 120, 120))
    q_default = estimate_original_jpeg_quality("test.jpg", img_plain)
    assert q_default == 90

    # 2. Image saved at high quality Q=95
    buf_high = io.BytesIO()
    img_plain.save(buf_high, format='JPEG', quality=95)
    buf_high.seek(0)
    img_high = Image.open(buf_high)
    q_high = estimate_original_jpeg_quality("high.jpg", img_high)
    assert q_high >= 85

    # 3. Image saved at low quality Q=50
    buf_low = io.BytesIO()
    img_plain.save(buf_low, format='JPEG', quality=50)
    buf_low.seek(0)
    img_low = Image.open(buf_low)
    q_low = estimate_original_jpeg_quality("low.jpg", img_low)
    assert q_low <= 75


def test_compute_texture_reliability_mask():
    # Smooth uniform canvas -> high reliability (close to 1.0)
    smooth_bgr = np.full((128, 128, 3), 128, dtype=np.uint8)
    mask_smooth, mean_smooth = compute_texture_reliability_mask(smooth_bgr, 4, 4, block_size=32)
    assert mask_smooth.shape == (4, 4)
    assert mean_smooth >= 0.95

    # Highly textured noisy canvas -> reliability discounted (< 1.0)
    np.random.seed(42)
    textured_bgr = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)
    mask_tex, mean_tex = compute_texture_reliability_mask(textured_bgr, 4, 4, block_size=32)
    assert mean_tex < mean_smooth
    assert np.all(mask_tex >= 0.35)


def test_compute_multiscale_block_anomaly():
    # Synthetic ELA image with high anomaly in one block
    ela_img = Image.new('RGB', (128, 128), color=(10, 10, 10))
    # Place a bright spliced patch in one 32x32 quadrant
    for x in range(32, 64):
        for y in range(32, 64):
            ela_img.putpixel((x, y), (180, 180, 180))

    img_bgr = np.full((128, 128, 3), 128, dtype=np.uint8)
    z_max, z_matrix, rel_index = compute_multiscale_block_anomaly(ela_img, img_bgr)

    assert z_max > 1.5
    assert z_matrix.shape == (4, 4)
    assert isinstance(rel_index, float)


def test_compute_npr_covariance_score():
    # 1. Very small image returns 0.0
    tiny = np.zeros((8, 8), dtype=np.uint8)
    score_tiny, reg_tiny = compute_npr_covariance_score(tiny)
    assert score_tiny == 0.0

    # 2. Smooth gradient image
    y, x = np.indices((128, 128))
    smooth_gray = ((x + y) / 2).astype(np.uint8)
    score_smooth, reg_smooth = compute_npr_covariance_score(smooth_gray)
    assert 0.0 <= score_smooth <= 1.0

    # 3. High regular periodic pattern (simulated generative upsampling)
    pattern = np.zeros((128, 128), dtype=np.uint8)
    pattern[::2, ::2] = 200
    score_pat, reg_pat = compute_npr_covariance_score(pattern)
    assert score_pat > 0.0


def test_compute_conformal_prediction_set():
    # Decisive AI generation (Score 90%)
    res_high = compute_conformal_prediction_set(90.0, "AI_GENERATION")
    assert res_high["coverage_guarantee"] == "95.0%"
    assert res_high["is_singleton"] is True
    assert res_high["prediction_set"] == ["AI_GENERATION"]
    assert res_high["badge_type"] == "danger"

    # Decisive Authentic Capture (Score 15%)
    res_low = compute_conformal_prediction_set(15.0, "AUTHENTIC_CAPTURE")
    assert res_low["is_singleton"] is True
    assert res_low["prediction_set"] == ["AUTHENTIC_CAPTURE"]
    assert res_low["badge_type"] == "success"

    # Ambiguous recompressed band (Score 50%)
    res_amb = compute_conformal_prediction_set(50.0, "RESAVED_MEDIA")
    assert res_amb["is_singleton"] is False
    assert len(res_amb["prediction_set"]) == 2
    assert "AUTHENTIC_CAPTURE" in res_amb["prediction_set"]
    assert "SYNTHETIC_OR_TAMPERED" in res_amb["prediction_set"]
    assert res_amb["badge_type"] == "warning"


