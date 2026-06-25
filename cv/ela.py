"""
ELA Document Forgery Detector — Field-Level Edition (Script Automation version)
==============================================================================
Detects tampering in scanned documents using Error Level Analysis, 
with automatic detection of SPECIFIC EDITED REGIONS.

Configured to run directly within your IDE without requiring command-line/bash arguments.
"""

import io
import os
import sys
import textwrap
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless-safe generation of the report
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy import ndimage  # For connected-component labelling
from PIL import Image


# ─────────────────────────────────────────────────────────────────────────────
# 0. DIRECT RUN CONFIGURATION (No Bash Needed!)
# ─────────────────────────────────────────────────────────────────────────────

# Change this path to the image you want to analyze:
IMAGE_PATH = "sample_document.jpg"

# Tweak processing parameters here directly instead of command-line flags:
JPEG_QUALITY = 95       # JPEG re-save quality (1-99)
AMPLIFY_FACTOR = 15.0   # ELA amplification multiplier
HOT_THRESHOLD = 0.40    # Brightness cutoff for suspicious pixels (0.0 to 1.0)
MIN_BLOB_AREA = 80      # Minimum cluster pixel size to register as a tampered area
COLORMAP_NAME = "inferno"  # Heatmap style (e.g., 'inferno', 'magma', 'jet', 'hot')
AUTO_OPEN_REPORT = True    # Automatically open the generated image when finished


# ─────────────────────────────────────────────────────────────────────────────
# 1. CORE ELA (Fixed Absolute Normalization)
# ─────────────────────────────────────────────────────────────────────────────

def run_ela(image: Image.Image, quality: int = 95) -> np.ndarray:
    """
    Compute raw, absolute per-pixel difference averaged across color channels.
    Leaves values on their true 0-255 scale to preserve absolute intensity.
    """
    original_rgb = image.convert("RGB")
    orig_arr     = np.asarray(original_rgb, dtype=np.float32)

    buf = io.BytesIO()
    original_rgb.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    recomp_arr = np.asarray(Image.open(buf).convert("RGB"), dtype=np.float32)

    # Absolute difference between original and re-compressed representation
    diff = np.abs(orig_arr - recomp_arr).mean(axis=2)   # H×W matrix [0.0, 255.0]
    return diff


def amplify_ela(ela_map: np.ndarray, factor: float = 15.0) -> np.ndarray:
    """
    Amplify absolute differences and normalize to [0, 1] relative to 
    the maximum possible 8-bit value (255.0).
    """
    return np.clip((ela_map * factor) / 255.0, 0.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 2. REGION / FIELD-LEVEL DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def find_tampered_regions(
    ela_amp: np.ndarray,
    threshold: float = 0.40,
    min_area:  int   = 80,
    dilate_px: int   = 6,
) -> list[dict]:
    """Identify localized anomalies via thresholding and spatial clustering."""
    hot_mask = ela_amp >= threshold

    # Dilate to merge close-by pixels into uniform fields
    struct = ndimage.generate_binary_structure(2, 2)  # 8-connectivity layout
    if dilate_px > 0:
        dilated = ndimage.binary_dilation(hot_mask, structure=struct, iterations=dilate_px)
    else:
        dilated = hot_mask

    labeled_arr, num_features = ndimage.label(dilated, structure=struct)

    regions = []
    for region_id in range(1, num_features + 1):
        component_mask = (labeled_arr == region_id)

        # Slice original data safely to compute internal evaluation statistics
        original_pixels = ela_amp[component_mask & hot_mask]
        
        # Guard clause: check size structure to prevent empty array runtime warnings
        if original_pixels.size == 0 or original_pixels.size < min_area:
            continue

        rows, cols = np.where(component_mask)
        r_min, r_max = int(rows.min()), int(rows.max())
        c_min, c_max = int(cols.min()), int(cols.max())

        mean_ela = float(original_pixels.mean())
        max_ela  = float(original_pixels.max())

        if   mean_ela >= 0.70: severity = "HIGH"
        elif mean_ela >= 0.50: severity = "MEDIUM"
        else:                  severity = "LOW"

        regions.append({
            "label"   : region_id,
            "bbox"    : (r_min, c_min, r_max, c_max),
            "area"    : int(original_pixels.size),
            "mean_ela": mean_ela,
            "max_ela" : max_ela,
            "severity": severity,
            "cx"      : (c_min + c_max) / 2,
            "cy"      : (r_min + r_max) / 2,
        })

    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    regions.sort(key=lambda r: (severity_order[r["severity"]], -r["mean_ela"]))
    return regions


# ─────────────────────────────────────────────────────────────────────────────
# 3. STATS & EVALUATION HEURISTICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_statistics(ela_map: np.ndarray, threshold: float) -> dict:
    return {
        "mean"        : float(ela_map.mean()),
        "std"         : float(ela_map.std()),
        "max"         : float(ela_map.max()),
        "p95"         : float(np.percentile(ela_map, 95)),
        "p99"         : float(np.percentile(ela_map, 99)),
        "hot_fraction": float((ela_map > threshold).mean()),
    }


def interpret_tampering(stats: dict, regions: list[dict]) -> tuple[str, str]:
    n_high   = sum(1 for r in regions if r["severity"] == "HIGH")
    n_medium = sum(1 for r in regions if r["severity"] == "MEDIUM")
    score    = stats["mean"] * 4 + stats["std"] * 2 + stats["hot_fraction"] * 10

    if n_high >= 1 or score >= 0.6:
        label = "TAMPERING DETECTED"
        explanation = (
            f"{len(regions)} suspicious region(s) found ({n_high} HIGH, {n_medium} MEDIUM). "
            "Targeted heat signature bounding boxes mark anomalous pixel distributions with "
            "mismatched compression origins. Modifications are localized here."
        )
    elif n_medium >= 1 or score >= 0.25:
        label = "SUSPICIOUS — REVIEW REQUIRED"
        explanation = (
            f"{len(regions)} regions showing moderate variance thresholds. Could denote secondary "
            "compression lifecycle steps, scan-line edge compression artifacts, or high-contrast font edges."
        )
    else:
        label = "LIKELY AUTHENTIC"
        explanation = (
            "Uniform distribution of compression artifacts across image grid cells. "
            "No field-level localized anomaly boundaries detected."
        )
    return label, explanation


# ─────────────────────────────────────────────────────────────────────────────
# 4. VISUALIZATION DASHBOARD GENERATION
# ─────────────────────────────────────────────────────────────────────────────

SEV_COLORS = {"HIGH": "#ff3a3a", "MEDIUM": "#ffa500", "LOW": "#ffe033"}

def draw_region_boxes(ax, regions: list[dict], show_labels: bool = True):
    for i, reg in enumerate(regions):
        r_min, c_min, r_max, c_max = reg["bbox"]
        w, h = c_max - c_min, r_max - r_min
        color = SEV_COLORS[reg["severity"]]

        rect = mpatches.Rectangle(
            (c_min, r_min), w, h,
            linewidth=1.8, edgecolor=color, facecolor="none", zorder=5
        )
        ax.add_patch(rect)

        if show_labels:
            badge_text = f"R{i+1} {reg['severity']}\n{reg['mean_ela']:.2f}"
            y_text = r_min - 4 if r_min > 20 else r_max + 4
            va     = "bottom" if r_min > 20 else "top"
            ax.text(
                c_min, y_text, badge_text, color=color, fontsize=6.5, fontweight="bold",
                va=va, ha="left", zorder=6,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#0d0f14", edgecolor=color, alpha=0.85)
            )


def build_report(original: Image.Image, ela_map_amp: np.ndarray, regions: list[dict], output_path: str):
    stats = compute_statistics(ela_map_amp, HOT_THRESHOLD)
    verdict_label, verdict_text = interpret_tampering(stats, regions)
    img_rgb = np.asarray(original.convert("RGB"))

    PANEL_BG, TICK_COLOR, TEXT_COLOR, ACCENT = "#13161e", "#8a93a8", "#dce3f0", "#f05454"

    fig = plt.figure(figsize=(20, 13), facecolor="#0d0f14")
    gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.38, wspace=0.08, left=0.03, right=0.97, top=0.91, bottom=0.13)

    ax_orig  = fig.add_subplot(gs[0:2, 0:2])
    ax_heat  = fig.add_subplot(gs[0:2, 2:4])
    ax_annot = fig.add_subplot(gs[2,   0:2])
    ax_hist  = fig.add_subplot(gs[2,   2:4])

    def style(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.set_title(title, color=TEXT_COLOR, fontsize=9.5, fontweight="bold", pad=5)
        for sp in ax.spines.values(): sp.set_edgecolor("#2a2f3d")
        ax.tick_params(colors=TICK_COLOR, labelsize=7)

    style(ax_orig, "Original Document")
    ax_orig.imshow(img_rgb)
    ax_orig.axis("off")

    style(ax_heat, f"ELA Heatmap (quality={JPEG_QUALITY}, amplify×{AMPLIFY_FACTOR})")
    ax_heat.imshow(ela_map_amp, cmap=COLORMAP_NAME, vmin=0, vmax=1, interpolation="lanczos")
    ax_heat.axis("off")
    cbar = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=COLORMAP_NAME), ax=ax_heat, fraction=0.03, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=TICK_COLOR, labelsize=7)
    cbar.outline.set_edgecolor("#2a2f3d")
    cbar.set_label("ELA Magnitude", color=TICK_COLOR, fontsize=8)

    style(ax_annot, f"Localization Diagnostics ({len(regions)} region(s) flagged)")
    ax_annot.imshow(img_rgb)
    ax_annot.imshow(ela_map_amp, cmap=COLORMAP_NAME, alpha=0.30, vmin=0, vmax=1, interpolation="lanczos")
    draw_region_boxes(ax_annot, regions)
    ax_annot.axis("off")
    legend_handles = [mpatches.Patch(facecolor=SEV_COLORS[k], label=f"{k} severity") for k in SEV_COLORS]
    ax_annot.legend(handles=legend_handles, loc="lower right", fontsize=7, facecolor="#0d0f14", labelcolor=TEXT_COLOR)

    style(ax_hist, "Pixel Distribution Profiles")
    flat = ela_map_amp.ravel()
    cmap_fn = plt.get_cmap(COLORMAP_NAME)
    n, bins, patches = ax_hist.hist(flat, bins=100, range=(0, 1), density=True, edgecolor="none", alpha=0.9)
    for patch, bl in zip(patches, bins[:-1]): patch.set_facecolor(cmap_fn(bl))

    ax_hist.axvline(HOT_THRESHOLD, color="#00e5ff", lw=1.4, linestyle="-.", label=f"Threshold {HOT_THRESHOLD:.2f}")
    ax_hist.axvline(stats["mean"], color="#f9ca24", lw=1.2, linestyle="--", label=f'Mean {stats["mean"]:.3f}')
    ax_hist.axvline(stats["p95"],  color=ACCENT,    lw=1.2, linestyle=":",  label=f'P95  {stats["p95"]:.3f}')
    ax_hist.legend(fontsize=7, facecolor=PANEL_BG, edgecolor="#2a2f3d", labelcolor=TEXT_COLOR)
    ax_hist.set_xlabel("ELA Magnitude", color=TICK_COLOR, fontsize=8)
    ax_hist.set_ylabel("Density", color=TICK_COLOR, fontsize=8)
    ax_hist.set_xlim(0, 1)

    stat_text = f"Mean: {stats['mean']:.4f}   Std: {stats['std']:.4f}\nMax:  {stats['max']:.4f}   P99: {stats['p99']:.4f}"
    ax_hist.text(0.98, 0.97, stat_text, transform=ax_hist.transAxes, ha="right", va="top", fontsize=7, color=TEXT_COLOR,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e2230", edgecolor="#2a2f3d", alpha=0.9))

    fig.suptitle("DOCUMENT FORENSICS · Automated ELA Structural Tamper Diagnostics", color=TEXT_COLOR, fontsize=13, fontweight="bold", y=0.975)

    if regions:
        lines = ["  Rg  |  Severity  |   Area   |  Mean ELA  |  Max ELA  |  BBox Boundaries"]
        lines.append("  " + "─" * 75)
        for i, r in enumerate(regions[:12]):
            r0, c0, r1, c1 = r["bbox"]
            lines.append(f"  R{i+1:<3}  {r['severity']:<10}  {r['area']:>7}px    {r['mean_ela']:.4f}    {r['max_ela']:.4f}    ({r0},{c0})→({r1},{c1})")
        summary = "\n".join(lines)
    else:
        summary = "  No local anomaly regions isolated above configuration parameters."

    fig.text(0.03, 0.11, summary, ha="left", va="top", fontsize=7, color="#a0aec0", fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#0a0c12", edgecolor="#2a2f3d", alpha=0.95))

    wrapped = textwrap.fill(verdict_text, width=120)
    verdict_color = "#27ae60" if "AUTHENTIC" in verdict_label else "#f39c12" if "SUSPICIOUS" in verdict_label else "#e74c3c"
    fig.text(0.5, 0.025, f"VERDICT: {verdict_label}   |   {wrapped}", ha="center", va="bottom", fontsize=8.5, color=verdict_color,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#13161e", edgecolor=verdict_color, linewidth=1.8, alpha=0.97))

    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[✓] Analysis metrics complete. Report asset compiled to: {output_path}")
    return stats, verdict_label


# ─────────────────────────────────────────────────────────────────────────────
# 5. ENTRY EXECUTION CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    img_path = Path(IMAGE_PATH)
    if not img_path.exists():
        sys.exit(f"[✗] Verification Failure: Target asset not located at '{img_path.resolve()}'. Please verify file initialization path string.")

    output_report_path = str(img_path.with_suffix("")) + "_ela_report.png"

    print(f"[...] Initializing source asset matrix map: {img_path.name}")
    original_img = Image.open(img_path)

    print(f"[...] Running Absolute Scale Error Level Analysis sweeps...")
    ela_raw = run_ela(original_img, quality=JPEG_QUALITY)
    ela_amp = amplify_ela(ela_raw, factor=AMPLIFY_FACTOR)

    print(f"[...] Scanning structural data arrays for localized spatial mutations...")
    detected_regions = find_tampered_regions(ela_amp, threshold=HOT_THRESHOLD, min_area=MIN_BLOB_AREA)

    print(f"[...] Compilation tracking: generating presentation diagnostic layouts ({len(detected_regions)} fields matching signature patterns)...")
    stats, verdict = build_report(
        original=original_img,
        ela_map_amp=ela_amp,
        regions=detected_regions,
        output_path=output_report_path
    )

    # Automatically open presentation files on execution completion cleanly
    if AUTO_OPEN_REPORT:
        try:
            import subprocess, platform
            sys_name = platform.system()
            if sys_name == "Windows":
                os.startfile(output_report_path)
            elif sys_name == "Darwin":
                subprocess.call(["open", output_report_path])
            elif sys_name == "Linux":
                subprocess.call(["xdg-open", output_report_path])
        except Exception:
            pass  # Silently drop open calls if terminal context does not map an active visual server environment


if __name__ == "__main__":
    main()                      please explain me this code step by step,i only know python as languge
