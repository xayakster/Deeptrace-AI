# Design Specification: AI Image Detection Accuracy & Robustness Overhaul

**Date:** 2026-10-11  
**Status:** Approved by User  
**Target Architecture:** Approach 1 — Lightweight ONNX Multi-Generator Classifier + Enhanced Noise-Print Physical Residuals with Dual Independent Telemetry  

---

## 1. Problem Statement & Objectives

### 1.1 Problem Statement
The existing DeepTrace AI detection pipeline relies primarily on hand-crafted frequency heuristics (Frank 2020 2D-FFT checkerboard peaks) and Laplacian noise voids ($\sigma^2 < 45.0$). Modern generative models—specifically **Diffusion Transformers (DiTs)** like **FLUX.1 Schnell/Dev**, **Midjourney v6/v6.1**, **Stable Diffusion 3/3.5**, and **Ideogram 2.0**—utilize continuous patch embeddings and advanced continuous VAE decoders. They do not produce transposed-convolution checkerboard grid artifacts and often incorporate natural or post-processed film grain, causing the legacy heuristics to fail and producing unacceptable false negatives.

### 1.2 Objectives
1. **Eliminate False Negatives:** Accurately classify modern DiT, diffusion, and GAN imagery (>95% detection rate across FLUX.1, Midjourney v6+, SDXL/SD3).
2. **Lightweight & Fast:** Use `onnxruntime` with a quantized/optimized model (<30 MB) running in **sub-50ms on CPU** with **zero GPU and zero PyTorch** requirements.
3. **Dual Independent Scoring:** Expose two orthogonal lines of forensic evidence side-by-side:
   - **Deep Neural Attribution Index (0–100%)**: Learned feature representations from pre-trained multi-generator benchmarks (GenImage).
   - **Physical Optical Sensor Score (0–100%)**: Photon shot noise, Spatial Rich Model (SRM) residuals, 2D-FFT decay, and NPR covariance.
4. **Court Defensibility & Standards Adherence:** Maintain full compliance with **SWGDE 18-Q-002**, **ISO/IEC 27037:2012**, and **ENFSI** evaluative reporting standards with 95% Conformal Prediction statistical guarantees.
5. **Zero Regression:** Preserve 100% backward compatibility with all existing routes, dashboard controls, reports, and the 53-test test suite.

---

## 2. System Architecture & Component Design

```
[Incoming Evidence Image]
           │
           ├──► Branch 1: Cryptographic Hashes, EXIF & C2PA Provenance
           │
           ├──► Branch 2A: Deep Neural Detector (`backend/forensics/neural_detector.py`)
           │    • ONNX Runtime Inference (`CPUExecutionProvider`, 2 threads)
           │    • MobileNetV4 / ConvNeXt-Tiny fine-tuned on GenImage (1.3M images)
           │    • Output: `neural_ai_score` (0-100%), `neural_latency_ms`
           │
           ├──► Branch 2B: Enhanced Physical Spectral Residuals (`backend/forensics/frequency.py`)
           │    • SRM High-Pass Noise Energy
           │    • 2D-FFT Azimuthal Power Decay
           │    • NPR Lag-2 Covariance Autocorrelation
           │    • Output: `physical_sensor_score` (0-100%)
           │
           ├──► Branch 3: Spatial Tampering & Adaptive ELA (`backend/forensics/tampering.py`)
           │    • TruFor Texture Reliability Discounting
           │    • Multiscale Block Anomaly Z-Score
           │    • Output: `tamper_score` (0-100%), Localization Heatmap
           │
           ▼
[Multi-Signal Forensic Arbitrator (`backend/forensics/arbitrator.py`)]
  • Dual Independent Telemetry Cards (Neural vs Physical)
  • Continuous Platt Temperature Scaling
  • 95% Marginal Coverage Conformal Prediction Sets
           │
           ├──► Web Dashboard V3: Dual HUD Meters & Visual Toggles
           └──► 4-Page Forensic Dossier PDF: Quantitative Telemetry Matrix
```

### 2.1 Component 1: `backend/forensics/neural_detector.py`
A new, self-contained neural detection module:
- **`ONNXDetector` Class (Singleton):**
  - Manages lazy loading of the ONNX model from `backend/models/deepfake_detector.onnx`.
  - Configured with `onnxruntime.SessionOptions(intra_op_num_threads=2, execution_mode=ExecutionMode.ORT_SEQUENTIAL)`.
  - Preprocesses input images via bilinear/bicubic resize to $256 \times 256$ with ImageNet channel standardization:
    $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$
  - Temperature-calibrated softmax inference:
    $$P(\text{AI}) = \frac{e^{z_1 / T}}{e^{z_0 / T} + e^{z_1 / T}}, \quad T = 1.15$$
  - Extract spatial feature activation map (LayerCAM/GradCAM equivalent from final convolution feature tensor) for explainability heatmaps.
  - **Robust Fallback:** If `onnxruntime` or the weight file is absent, automatically falls back to an enhanced SRM/NPR physical ensemble without throwing exceptions or blocking analysis.

### 2.2 Component 2: Enhanced Physical Forensic Residuals (`backend/forensics/frequency.py`)
Augments the physical signal branch with:
- **Spatial Rich Models (SRM) High-Pass Residuals (Fridrich & Kodovsky, 2012):**
  Applies $3 \times 3$ and $5 \times 5$ linear high-pass residual filters to isolate high-frequency sensor noise from image scene semantics:
  $$F_{\text{edge}} = \begin{bmatrix} -1 & 2 & -1 \\ 2 & -4 & 2 \\ -1 & 2 & -1 \end{bmatrix}$$
  Real camera sensors exhibit uniform stochastic shot noise across non-saturated regions; neural synthetic decoders produce correlated residual voids or artificial high-frequency banding.
- **Multiscale Wavelet Noise Variance:**
  Computes sub-band noise variance across horizontal, vertical, and diagonal detail coefficients.

### 2.3 Component 3: Arbitrator Dual-Score Schema (`backend/forensics/arbitrator.py`)
Refactors the arbitrator to output dual independent evaluation dimensions:
```json
{
  "scores": {
    "composite_score": 94.2,
    "neural_ai_score": 96.5,
    "physical_sensor_score": 88.0,
    "tamper_score": 12.0
  },
  "dual_telemetry": {
    "neural": {
      "score": 96.5,
      "probability": 0.965,
      "model": "DeepTrace-MobileNetV4-GenImage-ONNX",
      "latency_ms": 34.2,
      "verdict": "SYNTHETIC_GENERATIVE_DISTRIBUTION"
    },
    "physical": {
      "score": 88.0,
      "laplacian_variance": 58.2,
      "srm_noise_energy": 0.124,
      "npr_covariance": 0.38,
      "spectral_peak_ratio": 0.22,
      "verdict": "SENSOR_NOISE_ANOMALY"
    }
  },
  "conformal_prediction": {
    "prediction_set": ["AI_GENERATION"],
    "coverage_guarantee": "95.0%",
    "status_label": "95% CONFIDENCE: DECISIVE ANOMALY"
  }
}
```

### 2.4 Component 4: Dashboard V3 UI & 4-Page Dossier Updates
- **Dashboard V3:** Add a side-by-side **Dual-Signal Forensics Meter** in [`dashboard.html`](file:///c:/Users/Asus/Desktop/Deeptrace-AI/frontend/templates/dashboard.html) displaying:
  - Metric A: `Deep Neural Attribution Index` (learned generative feature space).
  - Metric B: `Physical Sensor Consistency Score` (hardware optics and shot noise).
- **Forensic Dossier PDF (`forensics/dossier.py`):**
  - Page 1: Displays both Neural and Physical scores alongside the Verdict Banner.
  - Page 2: Telemetry Matrix expanded to include SRM residual energy, ONNX latency, and neural confidence alongside camera EXIF metadata.

---

## 3. Data Flow & Execution Sequence

```
1. Client POST /analyze (multipart/form-data)
2. File validation & decompression bomb check (<15 MB, Image.MAX_IMAGE_PIXELS=50M)
3. Branch 1: MD5, SHA-256, dHash, EXIF extraction, C2PA audit
4. Branch 2A (Parallel / Fast): ONNX Neural Inference (<40ms) -> neural_ai_score
5. Branch 2B: 2D-FFT, SRM high-pass residual, NPR covariance -> physical_sensor_score
6. Branch 3: Multi-scale ELA & TruFor texture reliability -> tamper_score
7. Multi-Signal Arbitrator: Fuses dual signals, computes 95% Conformal Prediction set
8. LRU Analysis Record Cache: Binds immutable state to UUIDv4 analysis_id
9. JSON Response returned to dashboard / Client initiates report download via analysis_id
```

---

## 4. Error Handling & Edge Case Strategy

1. **Missing or Corrupted Model File:** If `backend/models/deepfake_detector.onnx` is missing or fails integrity check, `neural_detector.py` logs a warning, switches to `fallback_mode=True`, and uses the enhanced SRM/NPR physical residual score as `neural_ai_score` with an informative badge (`FALLBACK: PHYSICAL ONLY`).
2. **Extreme Aspect Ratios / Giant Images:** Scaled with aspect-ratio-preserving padding to standard $256 \times 256$ input tensors without distortion.
3. **Low-Memory / CPU Thread Contention:** ONNX Session configured with `intra_op_num_threads=2` to prevent CPU thread starvation under concurrent web requests.

---

## 5. Verification & Testing Strategy

1. **Unit Tests (`tests/test_neural_detector.py`):**
   - Test ONNX model loading and session initialization.
   - Test preprocessing (RGB conversion, tensor shapes `[1, 3, 256, 256]`, normalization bounds).
   - Test inference reproducibility on authentic vs synthetic test fixtures.
   - Test graceful fallback behavior when model is absent.
2. **Integration Tests (`tests/test_api.py`):**
   - Test `/analyze` payload includes `neural_ai_score` and `physical_sensor_score`.
   - Test `/download_report` reflects dual scores in generated PDF.
3. **Dataset Benchmark (`scripts/evaluate_dataset.py`):**
   - Verify 100% detection rate on `data/test_images/ai_generated_images/` (synthetic portraits, diffusion samples).
   - Verify authentic images in `data/test_images/real_images/` remain properly classified as `AUTHENTIC`.
4. **Coverage Target:** Maintain $\ge 85\%$ statement coverage across `backend/`.
