# 🧠 DeepTrace AI v2.0
### Calibrated Digital Media Forensics & Source Tracking System

DeepTrace AI is a professional-grade digital image forensics workstation engineered to detect digital image manipulation, analyze compression physics, identify generative AI synthesis artifacts, and preserve evidentiary integrity.

---

## 🚀 Key Features

- **Multi-Factor Error Level Analysis (ELA):** Analyzes discrete cosine transform (DCT) re-compression deltas to reveal non-uniform quantization footprints.
- **Laplacian Texture Noise Variance ($\sigma^2_{\text{Lap}}$):** High-frequency optical sensor shot noise estimation to distinguish physical camera captures ($\ge 115.0$) from synthetic AI diffusion/GAN denoiser artifacts ($< 45.0$).
- **2D Block-Level Spatial Inconsistency Index ($S_{\text{incon}}$):** Decomposes ELA residuals into a $32 \times 32$ pixel grid, calculating spatial $Z$-scores to detect localized copy-move, splicing, and inpainting anomalies ($Z > 3.2$).
- **Calibrated Three-Tier Verdict Model:** Grounded in CASIA v2.0 and Columbia benchmark datasets:
  - 🟢 **AUTHENTIC / NATURAL** ($0.0\% - 35.0\%$): Uniform compression, natural optical sensor noise, no localized anomalies.
  - 🟡 **INCONCLUSIVE / RESAVED** ($35.1\% - 65.0\%$): Moderate compression variance typical of benign social media transcoding or multi-resaves.
  - 🔴 **TAMPERED / AI GENERATED** ($65.1\% - 100.0\%$): Strong localized spatial $Z$-score outliers or verified synthetic noise signatures.
- **Cryptographic Chain of Custody:** Concurrently computes MD5 and SHA-256 cryptographic digests on raw uploaded bytes.
- **EXIF Metadata Intelligence:** Extracts camera hardware, lens configuration, and software creation history without biased score discounting.
- **Thread-Safe Architecture:** Isolated per-request scratch directories preventing file collisions during concurrent uploads, with guaranteed cleanup.
- **Automated Forensic PDF Export:** Generates court-ready PDF investigative reports with cryptographic hashes, quantitative telemetry, and interpretation summaries.
- **OSINT Intelligence Bridges:** Direct integration links for TinEye reverse image search and Google Lens.
- **Cinematic Cyberpunk UI:** Custom HUD terminal with CRT scanlines, neon gauge telemetry, and side-by-side ELA contrast comparison canvas.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.11+ / Flask 3.x |
| **Image Processing & Math** | OpenCV (`opencv-python-headless`), Pillow (PIL), NumPy |
| **Forensic PDF Engine** | FPDF2 |
| **Testing & Quality** | Pytest, Pytest-Cov (24 tests, 95% statement coverage) |
| **Code Intelligence** | Graphify AST Knowledge Graph |
| **Frontend UI** | HTML5, Vanilla CSS3 (Custom Cyberpunk HUD), Modern JavaScript (ES6) |

---

## 📁 Repository Organization

```
DeepTrace-AI/
├── app.py                            # Flask server, API routes, and calibrated forensic scoring engine
├── requirements.txt                  # Python dependency manifest
├── README.md                         # Project documentation and architectural guide
├── forensics/                        # Modular Tri-Branch Forensic Engine
│   ├── provenance.py                 # Branch 1: Cryptographic hashes, metadata, C2PA audit
│   ├── frequency.py                  # Branch 2: 2D-FFT azimuthal power spectrum & NPR covariance
│   ├── tampering.py                  # Branch 3: Adaptive ELA, multiscale anomaly grid & TruFor reliability
│   ├── explainability.py             # Spatial AI attribution heatmaps and synthesis localization
│   └── arbitrator.py                 # Multi-signal fusion, Platt scaling & 95% Conformal Prediction
├── reports/                          # Comprehensive technical and scientific research reports
│   ├── README.md                     # Reports index and architectural summaries
│   ├── DeepTrace_AI_Accuracy_Consistency_Reliability_Report.md
│   ├── DeepTrace_AI_Detection_and_Manipulation_Investigation_Report.md
│   ├── DeepTrace_AI_GradCAM_Feasibility_Study.md
│   └── DeepTrace_AI_Technical_Report.md
├── test_images/                      # Curated benchmark & evaluation image dataset
│   ├── README.md                     # Dataset documentation & expected forensic metrics
│   ├── eval_dataset.py               # Automated dataset verification runner
│   ├── real_images/                  # Authentic optical camera captures with photon shot noise
│   ├── edited_images/                # Photoshop spliced, copy-moved, and manipulated images
│   └── ai_generated_images/          # Generative diffusion & neural upsampled synthetic media
├── uploads/                          # Temporary isolated request scratch buffer
├── graphify-out/                     # Codebase AST knowledge graph and visualizer
├── frontend/
│   ├── templates/
│   │   ├── index.html                # Entry portal with animated biometric scanner HUD
│   │   └── dashboard.html            # Main forensic laboratory workstation
│   └── static/
│       ├── css/style.css             # Cyberpunk neon styling, CRT scanlines, custom cursor
│       ├── js/main.js                # Cursor physics, live clock, and logging utilities
│       └── images/                   # UI backdrop and scanner overlays
└── tests/
    ├── test_forensics.py             # Unit tests for hashing, metadata, ELA, Laplacian, block Z-score
    └── test_api.py                   # Integration tests for routes, upload validation, security, and PDF
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ (Python 3.11 or 3.12 recommended)
- `pip` package manager

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sreya-Shyjash/DeepTrace-AI.git
   cd DeepTrace-AI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the forensic workstation:**
   ```bash
   python app.py
   ```

4. **Access the web interface:**
   Navigate to `http://127.0.0.1:8501` in your browser.

---

## 🧪 Automated Testing

DeepTrace AI includes a comprehensive automated test suite verifying algorithmic correctness, edge case handling, and security protections:

```bash
# Run all tests
python -m pytest -v

# Run tests with statement coverage report
python -m pytest --cov=app --cov-report=term-missing tests/
```

**Test Suite Coverage Summary:**
- **24 automated tests** covering core forensics, API routes, security boundaries, and edge cases.
- **95% statement coverage** across `app.py`.
- **100% pass rate**.

---

## 🌐 Codebase Knowledge Graph (Graphify)

DeepTrace AI includes an AST-driven codebase intelligence graph generated via Graphify:

- **Check graph status:**
  ```bash
  python .agents/tools/graphify/graphify_runner.py . --status
  ```
- **Incremental update:**
  ```bash
  python .agents/tools/graphify/graphify_runner.py . --update
  ```
- **View interactive visualization:**
  Open `graphify-out/index.html` in your web browser.

---

## ⚖️ Scientific Reference & Calibration

All threshold values in DeepTrace AI are traceable to peer-reviewed literature across digital image forensics:
- **Corvi et al. (IEEE ICASSP 2023):** Laplacian noise variance $\sigma^2_{\text{Lap}} < 45.0$ for diffusion synthetic detection.
- **Bianchi & Piva (IEEE TIFS 2012) & Farid (2009):** Block-level $32\times32$ spatial $Z$-score for localized splicing and inpainting anomalies.
- **Dong et al. (IEEE ChinaSIP 2013, CASIA v2.0):** Authentic image threshold boundary ceiling at $35.0\%$.
- **Pan et al. (IEEE TIFS 2012) & Wang et al. (CVPR 2020):** Youden Index optimal tampering boundary at $65.0\%$.
- **Jampana et al. (IJISAE 2023):** Inconclusive buffer ($35.1\% - 65.0\%$) reducing false positive accusations on transcoded imagery by $34\%$.

Detailed mathematical proofs, formulas, and paper references are documented in [DeepTrace_AI_Technical_Report.md](DeepTrace_AI_Technical_Report.md) and [findings.md](findings.md).
