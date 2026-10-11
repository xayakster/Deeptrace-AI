"""
Unit and Integration Tests for DeepTrace AI — Neural Detector Module.
Tests ONNX runtime engine, preprocessing, prediction, graceful fallback, and data invariants.
"""

import os
import pytest
import numpy as np
import cv2

from backend.forensics.neural_detector import ONNXDetector, detect_neural_synthesis


@pytest.fixture
def sample_bgr_image():
    """Generates a synthetic 256x256 BGR test pattern."""
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.circle(img, (128, 128), 64, (255, 128, 64), -1)
    return img


@pytest.fixture
def real_image_path():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "test_images", "real_images", "authentic_photo.jpg")
    return os.path.abspath(path)


@pytest.fixture
def ai_image_path():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "test_images", "ai_generated_images", "ai_synthetic.jpg")
    return os.path.abspath(path)


def test_singleton_pattern():
    """Verify that ONNXDetector implements the singleton pattern."""
    inst1 = ONNXDetector.get_instance()
    inst2 = ONNXDetector.get_instance()
    assert inst1 is inst2


def test_preprocessing_tensor_shape_and_type(sample_bgr_image):
    """Verify that preprocess_image outputs a valid normalized float32 tensor."""
    detector = ONNXDetector.get_instance()
    tensor = detector.preprocess_image(sample_bgr_image)
    assert isinstance(tensor, np.ndarray)
    assert tensor.dtype == np.float32
    assert tensor.shape[0] == 1  # batch dimension
    assert tensor.shape[1] in (3, detector.target_h)  # NCHW or NHWC layout


def test_fallback_mode_on_missing_model(tmp_path, sample_bgr_image):
    """Verify that ONNXDetector falls back gracefully when model file does not exist."""
    fake_path = str(tmp_path / "non_existent_model.onnx")
    detector = ONNXDetector(model_path=fake_path)
    assert detector.is_fallback is True

    result = detector.predict(sample_bgr_image)
    assert isinstance(result, dict)
    assert "neural_ai_score" in result
    assert "probability" in result
    assert "latency_ms" in result
    assert "verdict" in result
    assert result["is_fallback"] is True
    assert 0.0 <= result["neural_ai_score"] <= 100.0


def test_predict_with_invalid_path():
    """Verify error handling on non-existent file path."""
    detector = ONNXDetector.get_instance()
    result = detector.predict("c:/invalid/path/to/nothing.png")
    assert result["neural_ai_score"] == 0.0
    assert result["verdict"] == "ERROR"


def test_predict_with_real_image(real_image_path):
    """Verify that authentic photos yield low suspicion / natural distribution."""
    if not os.path.exists(real_image_path):
        pytest.skip("Test image not found")
    result = detect_neural_synthesis(real_image_path)
    assert isinstance(result, dict)
    assert 0.0 <= result["neural_ai_score"] <= 100.0
    assert result["neural_ai_score"] < 40.0
    assert result["verdict"] == "NATURAL_IMAGE_DISTRIBUTION"


def test_predict_with_ai_synthetic_image(ai_image_path):
    """Verify that AI synthetic images produce elevated neural attribution score."""
    if not os.path.exists(ai_image_path):
        pytest.skip("Test image not found")
    result = detect_neural_synthesis(ai_image_path)
    assert isinstance(result, dict)
    assert 0.0 <= result["neural_ai_score"] <= 100.0
    assert result["neural_ai_score"] >= 60.0
    assert result["verdict"] == "SYNTHETIC_GENERATIVE_DISTRIBUTION"
