# DeepTrace-AI Test & Evaluation Image Dataset

This directory contains standardized, curated digital image assets used for benchmarking, regression testing, and evaluation of the **DeepTrace-AI Tri-Branch Forensic Workstation**.

---

## 📁 Directory Structure & Taxonomy

```
test_images/
├── README.md                     # Documentation and forensic catalog (this file)
├── real_images/                  # Authentic, unmanipulated optical camera photographs
│   ├── authentic_photo.jpg       # Natural portrait capture with optical photon shot noise
│   └── authentic_landscape.jpg   # Natural landscape with continuous gradient dynamics
├── edited_images/                # Digital image manipulations & Photoshop forgeries
│   ├── spliced_tampered.jpg      # Spliced composition with block compression discrepancy
│   └── copy_move_tampered.jpg    # Duplicated region forgery with quantization mismatch
└── ai_generated_images/          # Generative AI & diffusion synthetic media
    ├── ai_synthetic.jpg          # Full-canvas diffusion synthesis asset
    └── ai_diffusion_portrait.jpg # Latent upsampled synthesis exhibiting NPR covariance
```

---

## 🔬 Forensic Asset Catalog & Expected Baseline Values

### 1. Real Images (`real_images/`)
Assets in this category represent authentic physical reality captured by optical camera hardware.

| Filename | Dimensions | Ground Truth | Expected Verdict | Expected Conformal Set | Key Physical Signatures |
|---|---|---|---|---|---|
| `authentic_photo.jpg` | $512 \times 512$ | Authentic Optical Capture | **AUTHENTIC** ($< 20\%$) | `[ AUTHENTIC_CAPTURE ]` (95% Singleton) | Laplacian noise variance $\sigma^2 \ge 115.0$; low spatial $Z \le 1.5$; NPR covariance $< 0.15$; uniform compression table. |
| `authentic_landscape.jpg` | $512 \times 512$ | Authentic Optical Capture | **AUTHENTIC** ($< 25\%$) | `[ AUTHENTIC_CAPTURE ]` (95% Singleton) | Healthy Poisson shot noise ($\sigma^2 > 130.0$); steep negative 2D-FFT decay slope; zero periodic lattice spikes. |

### 2. Edited Images (`edited_images/`)
Assets in this category contain localized image manipulations (splicing, inpainting, copy-move).

| Filename | Dimensions | Ground Truth | Expected Verdict | Expected Conformal Set | Key Physical Signatures |
|---|---|---|---|---|---|
| `spliced_tampered.jpg` | $512 \times 512$ | Localized Splicing | **TAMPERED** ($> 65\%$) | `[ AUTHENTIC_CAPTURE, SYNTHETIC_OR_TAMPERED ]` | Localized spatial $Z$-score $> 3.2$; block anomaly coverage $\approx 15-25\%$; TruFor texture reliability discount applied. |
| `copy_move_tampered.jpg` | $512 \times 512$ | Copy-Move Forgery | **TAMPERED** ($> 65\%$) | `[ AUTHENTIC_CAPTURE, SYNTHETIC_OR_TAMPERED ]` | Multi-scale grid anomaly at $16\times16$ and $32\times32$; dual-compression quantization residual mismatch. |

### 3. AI-Generated Images (`ai_generated_images/`)
Assets in this category represent full-canvas synthetic imagery created by generative AI models (Diffusion, DiTs, GANs).

| Filename | Dimensions | Ground Truth | Expected Verdict | Expected Conformal Set | Key Physical Signatures |
|---|---|---|---|---|---|
| `ai_synthetic.jpg` | $512 \times 512$ | Diffusion Synthesis | **AI GENERATED** ($> 85\%$) | `[ AI_GENERATION ]` (95% Singleton) | Sensor noise void ($\sigma^2_{\text{Lap}} < 45.0$); periodic 2D-FFT spectral lattice peak $> 0.50$; NPR covariance regularity $> 0.65$. |
| `ai_diffusion_portrait.jpg` | $512 \times 512$ | Latent DiT Upsampling | **AI GENERATED** ($> 80\%$) | `[ AI_GENERATION ]` (95% Singleton) | Non-overlapping lag-2 covariance spike ($> 0.35$); absence of physical camera photon shot noise; smooth spatial ELA variance. |

---

## 🚀 Running Automated Evaluations on the Dataset

To test and evaluate the entire test suite against the live running DeepTrace-AI instance (`http://localhost:8501`), run:

```bash
# Execute automated evaluation across all categorized test images
python -c "
import os, glob, urllib.request, json, io

BASE_DIR = 'test_images'
for category in ['real_images', 'edited_images', 'ai_generated_images']:
    folder = os.path.join(BASE_DIR, category)
    for img_name in os.listdir(folder):
        if not img_name.endswith('.jpg'): continue
        path = os.path.join(folder, img_name)
        boundary = '----WebKitBoundary123'
        body = io.BytesIO()
        body.write(b'--' + boundary.encode() + b'\r\n')
        body.write(f'Content-Disposition: form-data; name=\"file\"; filename=\"{img_name}\"\r\n'.encode())
        body.write(b'Content-Type: image/jpeg\r\n\r\n')
        with open(path, 'rb') as f: body.write(f.read())
        body.write(b'\r\n--' + boundary.encode() + b'--\r\n')
        req = urllib.request.Request('http://localhost:8501/analyze', data=body.getvalue(), headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        print(f'[{category}] {img_name} -> Verdict: {data[\"verdict\"]} ({data[\"score\"]}%) | Set: {data[\"conformal_prediction\"][\"prediction_set\"]}')
"
```
