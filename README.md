# 🧠 DeepTrace AI v2.5
### Tri-Branch Calibrated Digital Media Forensics & Source Tracking System

DeepTrace AI is a court-defensible digital image forensics workstation engineered to detect digital image manipulation, analyze compression physics, identify generative AI synthesis artifacts, extract hardware provenance, and generate accredited forensic examination dossiers.

---

## 🚀 Key Features

- **Tri-Branch Forensic Analysis Engine:**
  - **Branch 1 (Provenance & Hardware Cryptography):** Computes RFC 1321 MD5, FIPS 180-4 SHA-256, and 64-bit perceptual dHash digests; parses embedded EXIF sensor/camera metadata; validates cryptographic C2PA Content Credentials manifests.
  - **Branch 2 (Frequency Domain & Structural Screening):** Applies 2D Fast Fourier Transform (2D-FFT) with azimuthal power spectrum integration to detect synthetic lattice peaks; analyzes Neighboring Pixel Relationships (NPR) lag-2 structural covariance for diffusion upsampling traces.
  - **Branch 3 (Spatial Tampering & Photoshop Localization):** Multiscale Error Level Analysis (ELA) with DCT quantization table quality estimation ($Q$ baseline); TruFor-inspired gradient texture reliability weighting; $32 \times 32$ spatial $Z$-score anomaly mapping.
- **Continuous Sigmoid Arbitration & 95% Conformal Prediction:** Fuses multi-branch evidence into calibrated suspicion scores with Platt temperature scaling and statistical guarantees (95% marginal coverage confidence sets).
- **Court-Defensible 4-Page Forensic Dossier:** Compiles publication-grade PDF dossiers adhering to **SWGDE 18-Q-002**, **ISO/IEC 27037:2012**, **ENFSI** Bayesian Likelihood Ratio ($LR$) verbal scales, and **ASTM E3079**:
  - *Page 1:* Executive Forensic Brief, Chain of Custody, Cryptographic Hashes, C2PA Audit, Verdict Banner, Conformal Guarantee, and Prioritized Actionable Takeaways.
  - *Page 2:* 7-Row Quantitative Telemetry Matrix, Camera Hardware & EXIF Table, and Physical/Generative Mechanism Interpretability (Daubert/Frye compliance).
  - *Page 3:* 4-Quadrant Comparative Evidence Gallery (Exhibit A: Original Evidence, Exhibit B: ELA Residual, Exhibit C: Spatial Tamper Heatmap, Exhibit D: Neural AI Attribution Heatmap) with calibrated false-color legends.
  - *Page 4:* SOP Analytical Pipeline, Tool Specifications, Standards Declarations, Evidentiary Notice, Examiner Certification, and Cryptographic SHA-256 Seal.
- **Server-Side Anti-Tampering (`AnalysisRecordCache`):** Thread-safe LRU cache cryptographically binding examination state to unique `analysis_id` tokens, preventing client-side payload tampering while preserving legacy compatibility.
- **Dashboard V3 Workstation:**
  - Magnetic Drop Zone with spring-lerp proximity physics and strict 15 MB file size validation.
  - Dual Comparison Workspace with interactive Before/After Split Curtain Slider (`#curtain-handle`).
  - 1.6-second Hold-to-Confirm export button (`#btn-hold-export`) preventing accidental concurrent exports.
- **Single-Frame Landing Page:** 100vh non-scrolling editorial presentation featuring an interactive canvas optical forensic lens simulator with real-time false-color overlays and filter switching.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.11+ / Flask 3.x |
| **Image Processing & Math** | OpenCV (`opencv-python-headless`), Pillow (PIL), NumPy |
| **Forensic PDF Engine** | FPDF2 2.8.9 (In-memory `io.BytesIO` streaming) |
| **Testing & Quality** | Pytest, Pytest-Cov (53 tests, 88% overall statement coverage, 100% pass rate) |
| **Code Intelligence** | Graphify AST Knowledge Graph (181 nodes, 198 edges) |
| **Security Scanning** | Bandit (AST security scanning, 0 High / 0 Medium vulnerabilities) |
| **Frontend UI** | HTML5, Vanilla CSS3 (Obsidian Dark Studio), Modern JavaScript (ES6) |

---

## 📁 Project Structure & Architectural Rules

DeepTrace AI follows Cookiecutter-standardized project structuring principles with strict separation of responsibilities:

```text
root/
│
├── frontend/       # Frontend UI templates, styles, and static assets
│   ├── templates/  # Jinja2 templates (index.html, dashboard.html)
│   └── static/     # CSS (Obsidian dark studio), JS, and UI graphics
│
├── backend/        # Backend server, API routes, and forensics engine
│   ├── app.py      # Core Flask server and forensic endpoints
│   ├── forensics/  # Modular Tri-Branch forensic engine
│   │   ├── arbitrator.py     # Multi-signal arbitrator & Conformal Prediction
│   │   ├── dossier.py        # 4-Page Court-Defensible Dossier compiler
│   │   ├── explainability.py # Spatial AI attribution heatmaps
│   │   ├── frequency.py      # 2D-FFT azimuthal power & NPR covariance
│   │   ├── provenance.py     # Hashes, EXIF metadata, C2PA audit
│   │   ├── tampering.py      # Adaptive ELA, multiscale anomaly, TruFor
│   │   └── __init__.py       # Package exports and public API
│   └── __init__.py # Backend package root
│
├── tests/          # Automated test suite
│   ├── conftest.py           # Pytest path and environment fixtures
│   ├── test_api.py           # Integration tests for routes, cache, 4-page PDF
│   └── test_forensics.py     # Unit tests for multi-branch forensic algorithms
│
├── scripts/        # Utility, smoke test, and benchmark scripts
│   ├── verify_api_live.py    # Live server health & evidence analysis test
│   └── evaluate_dataset.py   # Full benchmark evaluation against test datasets
│
├── configs/        # Deployment and tooling configuration files
│   ├── Dockerfile            # Container build specification
│   ├── docker-compose.yml    # Multi-container orchestration definition
│   ├── .dockerignore         # Docker build exclusion rules
│   └── pytest.ini            # Pytest execution configuration
│
├── data/           # Datasets and benchmark test images
│   └── test_images/
│       ├── real_images/         # Authentic optical camera captures
│       ├── edited_images/       # Photoshop spliced & manipulated images
│       ├── ai_generated_images/ # Neural synthetic media (Midjourney, DALL-E, SD)
│       └── README.md            # Dataset specification and citations
│
├── docs/           # Documentation, research reports, and presentation assets
│   ├── reports/      # Forensic investigation & architectural reports
│   ├── archive/      # Historical prompt requirements & UI specs
│   └── presentation/ # Workstation screenshots & presentation slides
│
├── app.py          # Clean root runner delegating to backend.app
├── requirements.txt# Python dependency manifest
└── README.md       # Canonical project documentation and entry point
```

### Project Structure Rules
1. **Root Cleanliness:** The root directory contains only entry points (`app.py`, `README.md`, `requirements.txt`).
2. **Strict Responsibility Placement:**
   - Frontend-related code belongs exclusively in `frontend/`.
   - Backend/API/forensic code belongs exclusively in `backend/`.
   - Automated tests belong exclusively in `tests/`.
   - Operational and benchmark scripts belong in `scripts/`.
   - Deployment and tool configurations belong in `configs/`.
   - Datasets and benchmark images belong in `data/`.
   - Reports, archives, and architectural documents belong in `docs/`.
3. **No Suffix Sprawl:** Never create versioned backup folders (`v2`, `backup`, `old`, `new`). Use Git history.

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ (Python 3.11 or 3.12 recommended)
- `pip` package manager

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/xayakster/Deeptrace-AI.git
   cd Deeptrace-AI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the forensic workstation:**
   ```bash
   # Via root runner
   python app.py

   # Or via backend package module
   python -m backend.app
   ```

4. **Access the web interface:**
   Navigate to `http://127.0.0.1:8501` in your browser.

---

## 🐳 Docker Deployment

To build and run DeepTrace AI in Docker using the standardized configuration files:

```bash
# Build and run with Docker Compose
docker compose -f configs/docker-compose.yml up --build

# Or build manually with Dockerfile
docker build -f configs/Dockerfile -t deeptrace-ai .
docker run -p 8501:8501 deeptrace-ai
```

---

## 🧪 Automated Testing

DeepTrace AI includes a comprehensive automated test suite verifying algorithmic correctness, edge case handling, and security protections:

```bash
# Run all tests
pytest tests/

# Run tests with statement coverage report
python -m pytest --cov=backend tests/
```

**Test Suite Coverage Summary:**
- **53 automated tests** covering core forensics, API routes, security boundaries, and edge cases.
- **88% overall statement coverage** (96% on `dossier.py`, 97% on `arbitrator.py`, 87% on `backend/app.py`).
- **100% pass rate**.

---

## 🛠️ Verification & Benchmark Scripts

Run operational verification and benchmark utilities from `scripts/`:

```bash
# Live server smoke test and analysis verification
python scripts/verify_api_live.py

# Full benchmark evaluation across all test datasets
python scripts/evaluate_dataset.py
```

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

Detailed mathematical proofs, formulas, and paper references are documented in [docs/reports/DeepTrace_AI_Technical_Report.md](docs/reports/DeepTrace_AI_Technical_Report.md) and [planning-with-files/findings.md](planning-with-files/findings.md).
