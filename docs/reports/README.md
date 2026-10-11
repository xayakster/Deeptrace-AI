# DeepTrace-AI Project Reports & Investigation Archive

This directory contains the comprehensive technical, architectural, and scientific investigation reports authored for the **DeepTrace-AI** project.

---

## 📑 Reports Index

| Report File | Topic & Scope | Key Insights & Architectural Decisions |
|---|---|---|
| [**`DeepTrace_AI_Accuracy_Consistency_Reliability_Report.md`**](DeepTrace_AI_Accuracy_Consistency_Reliability_Report.md) | **Accuracy, Consistency & Reliability Investigation** | Analyzes failure modes of heuristic thresholds and proves that training deep models from scratch causes shortcut learning (~51% accuracy on unseen generators). Formulates the 4-tier hardening roadmap: Adaptive JPEG quantization, Non-Overlapping Lag-2 NPR Covariance, TruFor Texture Reliability Masking, and Conformal Prediction (95% coverage guarantee). |
| [**`DeepTrace_AI_Detection_and_Manipulation_Investigation_Report.md`**](DeepTrace_AI_Detection_and_Manipulation_Investigation_Report.md) | **Deep Forensic Investigation: AI Generation & Photoshop Tampering** | Investigates state-of-the-art tools, open-source models (UnivFD, NPR, TruFor, CAT-Net v2), and academic literature across 9 key areas. Establishes the Tri-Branch Hybrid Architecture separating Provenance (Branch 1), Spectral AI Screening (Branch 2), and Tamper Localization (Branch 3). |
| [**`DeepTrace_AI_GradCAM_Feasibility_Study.md`**](DeepTrace_AI_GradCAM_Feasibility_Study.md) | **Grad-CAM Heatmap Feasibility Study** | Evaluates the viability of Grad-CAM for visual manipulation heatmaps. Proves that Grad-CAM produces coarse attribution maps ($7\times7$ to $14\times14$) rather than pixel-level tamper masks and is inapplicable to non-differentiable pipelines. Recommends and establishes the Hybrid Dual-Representation Architecture separating Physical Tamper Heatmaps (Branch 3) from AI Feature Attribution (Explainability). |
| [**`DeepTrace_AI_Technical_Report.md`**](DeepTrace_AI_Technical_Report.md) | **Technical Architecture & Benchmark Calibration Report** | Original codebase audit and forensic threshold calibration report based on 22 seminal research papers. Specifies Laplacian sensor noise variance ($\sigma^2 < 45.0$), spatial $Z$-score thresholds ($Z > 3.2$), and the three-tier classification boundaries (Authentic, Inconclusive, Tampered). |
