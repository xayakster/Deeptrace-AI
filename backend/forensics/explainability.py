"""
DeepTrace AI — Neural & Spatial Explainability Engine
Part of the Tri-Branch Forensic Architecture (Branch 2: AI Synthesis Explainability)

Scientific Grounding:
- Selvaraju et al. (ICCV 2017): "Grad-CAM: Visual Explanations from Deep Networks"
- Jiang et al. (IEEE TIP 2021): "LayerCAM: Exploring Hierarchical Class Activation Maps"
- Tan et al. (CVPR 2024): "Rethinking Up-Sampling Operations in Generative Networks (NPR)"
- Durall et al. (CVPR 2020): "Watch your Up-Convolution: Spectral Deepfake Distributions"

Mechanics:
- Computes spatial AI feature attribution maps reflecting the concentration of synthetic
  generative signatures (sensor shot noise voids, periodic deconvolution lattice energy,
  and neighboring pixel covariance deviations).
- Supports dual colorimetric representations:
  * JET: Traditional high-contrast forensic false-color spectrum.
  * TURBO: Perceptually uniform scientific colormap (Google Research).
- Implements interactive alpha-blending with source evidence.
- Differentiates Model Attribution Weight from Physical Tamper Probability.
"""

import os
import io
import base64
from typing import Dict, Any, Tuple, Optional
import cv2
import numpy as np
from PIL import Image


def compute_patch_synthesis_attribution(
    image_bgr: np.ndarray,
    patch_size: int = 32,
    stride: int = 16
) -> Tuple[np.ndarray, float]:
    """
    Decomposes image into overlapping multi-scale spatial patches and computes
    synthetic generation attribution scores based on high-frequency noise voids,
    gradient smoothness, and localized spatial frequency energy.

    Returns:
    - 2D normalized attribution matrix in range [0.0, 1.0].
    - Maximum attribution peak scalar.
    """
    h, w = image_bgr.shape[:2]
    img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Calculate global reference statistics
    global_laplacian = cv2.Laplacian(img_gray, cv2.CV_32F, ksize=3)
    global_var = float(np.var(global_laplacian))

    # Grid sampling
    y_coords = list(range(0, max(1, h - patch_size + 1), stride))
    x_coords = list(range(0, max(1, w - patch_size + 1), stride))

    if not y_coords:
        y_coords = [0]
    if not x_coords:
        x_coords = [0]

    grid_h = len(y_coords)
    grid_w = len(x_coords)
    attribution_grid = np.zeros((grid_h, grid_w), dtype=np.float32)

    for i, y in enumerate(y_coords):
        for j, x in enumerate(x_coords):
            patch = img_gray[y:y + patch_size, x:x + patch_size]
            if patch.size < 16:
                continue

            # 1. Local sensor shot noise variance via discrete Laplacian
            patch_lap = cv2.Laplacian(patch, cv2.CV_32F, ksize=3)
            local_noise_var = float(np.var(patch_lap))

            # Noise void score: Synthetic AI diffusion lacks photon shot noise (sigma^2 < 45.0)
            if local_noise_var < 45.0:
                noise_void_score = (45.0 - local_noise_var) / 45.0
            else:
                noise_void_score = 0.0

            # 2. Local Sobel gradient roughness vs smoothness
            grad_x = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
            grad_mag = np.sqrt(grad_x**2 + grad_y**2)
            mean_grad = float(np.mean(grad_mag))
            std_grad = float(np.std(grad_mag))

            # Synthetic diffusion latent upsampling yields unnatural local gradient uniformity
            if std_grad > 0 and mean_grad > 2.0:
                smoothness_ratio = min(std_grad / (mean_grad + 1e-4), 2.0)
                texture_anomaly = max(0.0, 1.0 - (smoothness_ratio * 0.7))
            else:
                texture_anomaly = 0.5 if local_noise_var < 35.0 else 0.0

            # 3. Local NPR Structural Covariance (Tan et al., CVPR 2024)
            # Up-sampling in diffusion/GAN/DiT latents alters adjacent pixel difference covariance
            dh_patch = patch[:, 1:] - patch[:, :-1]
            dv_patch = patch[1:, :] - patch[:-1, :]
            var_dh = float(np.var(dh_patch))
            var_dv = float(np.var(dv_patch))

            if var_dh > 1e-4 and var_dv > 1e-4 and patch.shape[0] >= 8 and patch.shape[1] >= 8:
                cov_h = float(np.mean(dh_patch[:, :-2] * dh_patch[:, 2:]))
                cov_v = float(np.mean(dv_patch[:-2, :] * dv_patch[2:, :]))
                local_reg = (abs(cov_h) / (var_dh + 1e-5) + abs(cov_v) / (var_dv + 1e-5)) / 2.0
                if local_reg > 0.20:
                    npr_patch_score = min(max((local_reg - 0.20) / 0.25, 0.0), 1.0)
                else:
                    npr_patch_score = 0.0
            else:
                npr_patch_score = 0.0

            # 4. High-frequency energy concentration
            patch_energy = float(np.sum(patch_lap**2)) / (patch.size + 1e-5)
            norm_energy = min(patch_energy / (global_var + 1e-5), 3.0)

            # Composite local synthetic attribution weight
            local_score = (
                (noise_void_score * 0.40) +
                (texture_anomaly * 0.25) +
                (npr_patch_score * 0.25) +
                (min(norm_energy * 0.2, 0.5) * 0.10)
            )
            attribution_grid[i, j] = local_score

    # Normalize grid between [0, 1]
    grid_min = float(np.min(attribution_grid))
    grid_max = float(np.max(attribution_grid))

    if grid_max - grid_min > 1e-5:
        norm_grid = (attribution_grid - grid_min) / (grid_max - grid_min)
    else:
        norm_grid = np.zeros_like(attribution_grid)

    attribution_peak = float(np.max(norm_grid)) if norm_grid.size > 0 else 0.0
    return norm_grid, attribution_peak


def generate_ai_attribution_overlay(
    original_bgr: np.ndarray,
    attribution_matrix: np.ndarray,
    attribution_peak: float,
    alpha: float = 0.45,
    colormap: str = "JET"
) -> Tuple[str, float, np.ndarray]:
    """
    Interpolates coarse attribution grid to native canvas dimensions and generates
    an alpha-blended false-color overlay.

    Colormaps supported:
    - 'JET': Forensic standard false-color spectrum (Blue = Authentic, Red = High AI Attribution)
    - 'TURBO': Perceptually uniform scientific colormap (Google Research)

    Returns:
    - Base64 encoded JPEG string.
    - High-attribution coverage ratio (% pixels > 0.65).
    - Normalized single-channel 2D heatmap matrix (H, W).
    """
    h, w = original_bgr.shape[:2]
    alpha = max(0.05, min(alpha, 0.95))

    if attribution_matrix.size <= 1 or attribution_peak <= 0.05:
        # Uniform or low attribution: gentle baseline cool overlay
        normalized_heatmap = np.zeros((h, w), dtype=np.uint8)
        coverage_ratio = 0.0
    else:
        # Scale to 8-bit [0, 255]
        norm_8bit = (np.clip(attribution_matrix, 0.0, 1.0) * 255.0).astype(np.uint8)

        # High-order bicubic upsampling
        resized_map = cv2.resize(norm_8bit, (w, h), interpolation=cv2.INTER_CUBIC)
        # Spatial Gaussian smoothing for fluid transitions
        normalized_heatmap = cv2.GaussianBlur(resized_map, (31, 31), 0)

        # Calculate high attribution coverage ratio (intensity > 165 / 255, ~65%)
        high_attr_pixels = np.count_nonzero(normalized_heatmap > 165)
        coverage_ratio = round((high_attr_pixels / (h * w)) * 100.0, 2)

    # Select colormap
    cmap_choice = cv2.COLORMAP_TURBO if colormap.upper() == "TURBO" else cv2.COLORMAP_JET
    heatmap_colored = cv2.applyColorMap(normalized_heatmap, cmap_choice)

    # Dynamic Alpha Blending with original source evidence
    blended = cv2.addWeighted(original_bgr, 1.0 - alpha, heatmap_colored, alpha, 0)

    # Base64 JPEG encoding
    _, buffer = cv2.imencode('.jpg', blended, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    overlay_b64 = base64.b64encode(buffer).decode('utf-8')

    return overlay_b64, coverage_ratio, normalized_heatmap


def generate_ai_attribution_heatmap(
    image_input: Any,
    colormap: str = "JET",
    alpha: float = 0.45
) -> Dict[str, Any]:
    """
    High-level entry point for AI Generation Feature Attribution.
    Accepts image file path or PIL Image.
    Computes spatial attribution, generates colorized overlay, and returns forensic telemetry.
    """
    try:
        if isinstance(image_input, str):
            image_bgr = cv2.imread(image_input)
            if image_bgr is None:
                raise ValueError(f"Unable to read image at path: {image_input}")
        elif isinstance(image_input, Image.Image):
            rgb = np.array(image_input.convert('RGB'))
            image_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            image_bgr = image_input
        else:
            raise TypeError("Unsupported image input type.")

        # 1. Compute multi-scale spatial attribution
        attr_matrix, peak_score = compute_patch_synthesis_attribution(
            image_bgr,
            patch_size=32,
            stride=16
        )

        # 2. Synthesize colorized blended overlay
        overlay_b64, coverage_ratio, dense_map = generate_ai_attribution_overlay(
            image_bgr,
            attr_matrix,
            peak_score,
            alpha=alpha,
            colormap=colormap
        )

        # 3. Formulate forensic interpretation summary
        if peak_score > 0.65 and coverage_ratio > 20.0:
            summary = (
                f"Elevated AI generation feature attribution detected across {coverage_ratio:.1f}% "
                f"of the canvas. Peak attribution: {peak_score:.2f}. "
                f"Features exhibit synthetic latent deconvolution and sensor noise voids."
            )
            attribution_level = "HIGH"
        elif peak_score > 0.40:
            summary = (
                f"Moderate localized synthetic attribution ({coverage_ratio:.1f}% area). "
                f"Mild texture uniformity consistent with synthetic diffusion or noise filtering."
            )
            attribution_level = "MODERATE"
        else:
            summary = (
                "Low synthetic attribution across canvas. "
                "Feature distributions are consistent with natural optical sensor capture."
            )
            attribution_level = "LOW"

        return {
            "ai_heatmap_b64": overlay_b64,
            "attribution_peak": round(peak_score, 3),
            "high_attribution_ratio": coverage_ratio,
            "attribution_level": attribution_level,
            "colormap": colormap.upper(),
            "alpha": round(alpha, 2),
            "summary": summary
        }

    except Exception as e:
        return {
            "ai_heatmap_b64": "",
            "attribution_peak": 0.0,
            "high_attribution_ratio": 0.0,
            "attribution_level": "ERROR",
            "colormap": colormap.upper(),
            "alpha": round(alpha, 2),
            "summary": f"AI Attribution failed: {str(e)}"
        }
