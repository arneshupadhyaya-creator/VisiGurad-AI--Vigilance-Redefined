"""
Document Forensics Pipeline — OOP Refactor (Logic Unchanged)
=============================================================
All original algorithms, thresholds, formulas, and flow are preserved exactly.
Only change: code is reorganised into classes with a single run() entry point.

Chronological stages:
  1. ImageLoader        — cv2.imread / PIL.Image.open
  2. ImagePreprocessor  — resize, normalize, optional save
  3. FormAligner        — ORB + BF-Hamming + RANSAC homography
  4. BlurDetector       — Laplacian patch-grid
  5. ImageRestorer      — Wiener deconvolution
  6. ELADetector        — ela_raw, ela_deficit, noise_map, struct_diff, combine
  7. ForgeryAnalyzer    — find_regions + verdict (with title-zone logic)
  8. ReportBuilder      — build_report (matplotlib)
  9. ForensicsPipeline  — orchestrator
"""

import io, os, textwrap
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy import ndimage
from scipy.ndimage import gaussian_filter, uniform_filter, laplace
from PIL import Image


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG  (same constants as all three original scripts)
# ══════════════════════════════════════════════════════════════════════════════

# --- Paths ---
SUSPECT_PATH   = "E:/CV/data/text.jpg"
REFERENCE_PATH = "E:/CV/data/text.jpg"        # same-file default from original
SCAN_PATH      = "E:/CV/data/g_train.jpg"
REF_FORM_PATH  = "E:/CV/data/g_format.jpg"
OUTPUT_DIR     = "E:/CV/output"
OUTPUT_PATH    = "E:/CV/docs/image_v3_report.png"

# --- ELA ---
JPEG_QUALITY = 88
AMPLIFY      = 30.0
THRESHOLD    = 0.30
MIN_AREA     = 300
CMAP         = "inferno"
BG, PANEL, TXT, TICK = "#0d0f14", "#13161e", "#dce3f0", "#8a93a8"
SEV = {"HIGH": "#ff3a3a", "MEDIUM": "#ffa500", "LOW": "#ffe033"}

# --- Aligner ---
MAX_NUM_FEATURES = 7000

# --- Blur detector ---
PATCH_SIZE      = 16
BLUR_CUTOFF     = 15.0
BACKGROUND_NOISE = 2.0

# --- Wiener ---
WIENER_K = 0.015


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — ImageLoader
# ══════════════════════════════════════════════════════════════════════════════

class ImageLoader:
    """Wraps cv2.imread and PIL.Image.open with path printing."""

    @staticmethod
    def load_cv2_color(path):
        print(f"Reading image : {path}")
        return cv2.imread(path, cv2.IMREAD_COLOR)

    @staticmethod
    def load_cv2_gray(path):
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    @staticmethod
    def load_pil(path):
        return Image.open(path)

    @staticmethod
    def dimensions(img):
        """Prints and returns resolution info (original snippet logic)."""
        height = img.shape[0]
        width  = img.shape[1]
        channels = img.shape[2] if len(img.shape) > 2 else 1
        print(f"Resolution: {width}x{height}")
        print(f"Channels: {channels}")
        return height, width, channels


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — ImagePreprocessor
# ══════════════════════════════════════════════════════════════════════════════

class ImagePreprocessor:
    """
    Loads, resizes, normalizes, and prepares an image for a CNN.
    Logic taken verbatim from normalize_and_process().
    """

    def __init__(self, image_path, output_folder=None,
                 normalization='minmax', save_as_numpy=False):
        self.image_path    = image_path
        self.output_folder = output_folder
        self.normalization = normalization
        self.save_as_numpy = save_as_numpy

    def process(self):
        # 1. Load
        img = cv2.imread(self.image_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image from: {self.image_path}")

        # 2. Convert to RGB and resize to 224x224
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
        img = img.astype(np.float32)

        # 3. Apply Normalization
        if self.normalization == 'minmax':
            normalized = img / 255.0
        elif self.normalization == 'imagenet':
            from tensorflow.keras.applications.resnet50 import preprocess_input
            normalized = preprocess_input(img)
        else:
            normalized = img / 255.0

        # 4. Optional: Save to disk
        if self.output_folder is not None:
            os.makedirs(self.output_folder, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.image_path))[0]

            if self.save_as_numpy:
                output_path = os.path.join(self.output_folder,
                                           f"{filename}_normalized.npy")
                np.save(output_path, normalized)
                print(f"Saved float array to: {output_path}")
            else:
                if normalized.min() >= 0 and normalized.max() <= 1:
                    save_img = (normalized * 255).astype(np.uint8)
                else:
                    save_img = ((normalized - normalized.min()) /
                                (normalized.max() - normalized.min()) * 255
                                ).astype(np.uint8)
                output_path = os.path.join(self.output_folder,
                                           f"{filename}_visual.jpg")
                cv2.imwrite(output_path,
                            cv2.cvtColor(save_img, cv2.COLOR_RGB2BGR))
                print(f"Saved visual image to: {output_path}")

        print("Array shape for CNN:", normalized.shape)
        print("Array value range:", normalized.min(), "to", normalized.max())
        return normalized


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 — FormAligner
# ══════════════════════════════════════════════════════════════════════════════

class FormAligner:
    """
    ORB keypoint matching + homography warp.
    Logic taken verbatim from the alignment script.
    """

    def __init__(self, ref_path, scan_path, output_dir):
        self.ref_path  = ref_path
        self.scan_path = scan_path
        self.output_dir = output_dir

    def align(self):
        # Step 1: Read
        print("Reading reference image : ", self.ref_path)
        im1 = cv2.imread(self.ref_path,  cv2.IMREAD_COLOR)
        print("Reading image to align : ",  self.scan_path)
        im2 = cv2.imread(self.scan_path, cv2.IMREAD_COLOR)

        # Step 2: Keypoints
        im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

        orb = cv2.ORB_create(MAX_NUM_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(im1_gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2_gray, None)

        im1_display = cv2.drawKeypoints(im1, keypoints1,
            outImage=np.array([]), color=(0, 0, 255),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        im2_display = cv2.drawKeypoints(im2, keypoints2,
            outImage=np.array([]), color=(0, 0, 255),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        cv2.imshow("Detected Keypoints - Original", im1_display)
        cv2.imshow("Detected Keypoints - Scanned",  im2_display)
        cv2.waitKey(0)

        # Step 3: Match
        matcher = cv2.DescriptorMatcher_create(
                      cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = list(matcher.match(descriptors1, descriptors2, None))
        matches.sort(key=lambda x: x.distance, reverse=False)
        numGoodMatches = int(len(matches) * 0.05)
        matches = matches[:numGoodMatches]

        im_matches = cv2.drawMatches(im1, keypoints1, im2, keypoints2,
                                     matches, None)
        cv2.imshow("Feature Matches Across Images", im_matches)
        cv2.waitKey(0)

        # Step 4: Homography
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)
        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt
        h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

        # Step 5: Warp & save
        height, width, channels = im1.shape
        im2_reg = cv2.warpPerspective(im2, h, (width, height))

        cv2.imshow("FINAL ALIGNED IMAGE", im2_reg)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        output_path = os.path.join(self.output_dir, "aligned_output.png")
        cv2.imwrite(output_path, im2_reg)
        print(f"\n[SUCCESS] Aligned form successfully saved to: {output_path}")

        print("Press any key to close all windows and exit.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return output_path


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 4 — BlurDetector
# ══════════════════════════════════════════════════════════════════════════════

class BlurDetector:
    """
    Laplacian patch-grid blur detector.
    Logic taken verbatim from blur detection script.
    """

    def __init__(self, image_path):
        self.image_path = image_path

    def detect(self):
        # 2. Load and convert
        img = cv2.imread(self.image_path)
        if img is None:
            print(f"Error: Could not open or find the image at: {self.image_path}")
            exit()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 3. Laplacian edge map
        laplacian_map = cv2.Laplacian(gray, cv2.CV_64F)

        # 4. Loop through 16x16 grid
        blurry_patches_count  = 0
        total_patches_checked = 0

        for y in range(0, h - PATCH_SIZE, PATCH_SIZE):
            for x in range(0, w - PATCH_SIZE, PATCH_SIZE):
                patch       = laplacian_map[y:y+PATCH_SIZE, x:x+PATCH_SIZE]
                patch_score = patch.var()
                if patch_score > BACKGROUND_NOISE:
                    total_patches_checked += 1
                    if patch_score < BLUR_CUTOFF:
                        blurry_patches_count += 1

        # 5. Percentage
        if total_patches_checked > 0:
            blur_percentage = (blurry_patches_count / total_patches_checked) * 100
        else:
            blur_percentage = 0.0

        # 6. Decision
        if blur_percentage > 1.0:
            verdict = "⚠️ BLURRY (Localized blur detected)"
        else:
            verdict = "✅ SHARP"

        # 7. Print
        filename = os.path.basename(self.image_path)
        print(f"--- Localized Blur Detection Results for {filename} ---")
        print(f"Total Content Patches Evaluated : {total_patches_checked}")
        print(f"Blurry Patches Detected         : {blurry_patches_count}")
        print(f"Blur Density Percentage         : {blur_percentage:.2f}%")
        print(f"Final Verdict                   : {verdict}")

        return verdict


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 5 — ImageRestorer  (Wiener)
# ══════════════════════════════════════════════════════════════════════════════

class ImageRestorer:
    """
    Wiener filter deblur.
    Logic taken verbatim from wiener_filter() function.
    """

    def __init__(self, image_path, output_path='deblurred_wiener.jpg'):
        self.image_path  = image_path
        self.output_path = output_path

    @staticmethod
    def wiener_filter(img, psf, K=0.01):
        img = img.astype(np.float32)

        # 1. FFT of image and PSF
        img_fft = np.fft.fft2(img)
        psf_fft = np.fft.fft2(psf, s=img.shape)

        # 2. Complex conjugate of PSF
        psf_fft_conj = np.conj(psf_fft)

        # 3. Wiener formula: W = H* / (|H|^2 + K)
        psf_fft_mag_sq = np.abs(psf_fft) ** 2
        wiener_kernel  = psf_fft_conj / (psf_fft_mag_sq + K)

        # 4. Apply kernel
        result_fft = img_fft * wiener_kernel

        # 5. Inverse FFT
        result = np.fft.ifft2(result_fft)
        result = np.abs(result)
        return np.clip(result, 0, 255).astype(np.uint8)

    def restore(self):
        blurry_img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)

        # Simulated PSF — same as original
        psf = cv2.getGaussianKernel(5, 1.5)
        psf = np.outer(psf, psf)

        deblurred_img = self.wiener_filter(blurry_img, psf, K=WIENER_K)
        cv2.imwrite(self.output_path, deblurred_img)
        return self.output_path


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 6 — ELADetector
# ══════════════════════════════════════════════════════════════════════════════

class ELADetector:
    """
    All ELA signal functions.
    Logic taken verbatim from ELA V3 script.
    """

    def ela_raw(self, img, q=JPEG_QUALITY):
        rgb  = img.convert("RGB")
        orig = np.asarray(rgb, np.float32)
        buf  = io.BytesIO()
        rgb.save(buf, "JPEG", quality=q)
        buf.seek(0)
        recomp = np.asarray(Image.open(buf).convert("RGB"), np.float32)
        diff   = np.abs(orig - recomp).mean(2)
        return np.clip(diff * AMPLIFY / 255, 0, 1)

    def ela_deficit(self, img):
        ela      = self.ela_raw(img, JPEG_QUALITY)
        loc_mean = uniform_filter(ela, 80)
        deficit  = np.clip(loc_mean - ela, 0, None) / (loc_mean + 0.01)
        mask     = loc_mean > 0.015
        return np.clip(deficit * mask * 2.5, 0, 1)

    def noise_map(self, img, bs=24):
        gray   = np.asarray(img.convert("L"), np.float32) / 255
        lap    = np.abs(laplace(gray))
        H, W   = gray.shape
        result = np.zeros((H, W))
        step   = bs // 2
        noises, coords = [], []
        for r in range(0, H - bs, step):
            for c in range(0, W - bs, step):
                if gray[r:r+bs, c:c+bs].mean() < 0.95:
                    noises.append(lap[r:r+bs, c:c+bs].mean())
                    coords.append((r, c))
        if not noises:
            return result
        noises = np.array(noises)
        med, std = np.median(noises), noises.std() + 1e-9
        for (r, c), n in zip(coords, noises):
            z = (n - med) / std
            if z < 0:
                result[r:r+bs, c:c+bs] = np.maximum(
                    result[r:r+bs, c:c+bs], np.clip(-z / 3, 0, 1))
        return result

    def struct_diff(self, suspect, reference):
        sg = np.asarray(suspect.convert("L"),  np.float32) / 255
        rg = np.asarray(reference.convert("L").resize(
             (sg.shape[1], sg.shape[0]), Image.LANCZOS), np.float32) / 255
        sb = ndimage.binary_dilation((sg < 0.5), iterations=2).astype(np.float32)
        rb = ndimage.binary_dilation((rg < 0.5), iterations=2).astype(np.float32)
        diff = gaussian_filter(np.abs(sb - rb), 5)
        return np.clip(diff / max(diff.max(), 1e-6) * 3, 0, 1)

    def combine(self, ela_d, nm, sd=None):
        if sd is not None:
            return np.clip(0.35*ela_d + 0.20*nm + 0.45*sd, 0, 1)
        return np.clip(0.55*ela_d + 0.45*nm, 0, 1)


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 7 — ForgeryAnalyzer
# ══════════════════════════════════════════════════════════════════════════════

class ForgeryAnalyzer:
    """
    Region detection and location-aware verdict.
    Logic taken verbatim from find_regions() and verdict() in ELA V3.
    """

    def find_regions(self, smap):
        mask   = smap >= THRESHOLD
        struct = ndimage.generate_binary_structure(2, 2)
        dil    = ndimage.binary_dilation(mask, structure=struct, iterations=6)
        labeled, n = ndimage.label(dil, structure=struct)
        regions = []
        for rid in range(1, n + 1):
            comp = labeled == rid
            px   = smap[comp & mask]
            if px.size < MIN_AREA:
                continue
            rows, cols = np.where(comp)
            r0, r1 = int(rows.min()), int(rows.max())
            c0, c1 = int(cols.min()), int(cols.max())
            ms  = float(px.mean())
            mx  = float(px.max())
            sev = "HIGH" if ms >= 0.55 else "MEDIUM" if ms >= 0.38 else "LOW"
            regions.append({"bbox": (r0, c0, r1, c1), "area": int(px.size),
                            "mean": ms, "max": mx, "sev": sev})
        regions.sort(key=lambda r: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r["sev"]])
        return regions

    def verdict(self, regions, img_h, has_ref):
        title_zone_h = img_h * 0.35
        title_regions = [r for r in regions if r["bbox"][0] < title_zone_h]
        body_regions  = [r for r in regions if r["bbox"][0] >= title_zone_h]  # noqa: F841

        # Upgrade title-zone MEDIUM → HIGH
        for r in title_regions:
            if r["sev"] == "MEDIUM":
                r["sev"] = "HIGH"

        n_high   = sum(1 for r in regions if r["sev"] == "HIGH")
        n_medium = sum(1 for r in regions if r["sev"] == "MEDIUM")
        n_low    = sum(1 for r in regions if r["sev"] == "LOW")
        title_flagged = len([r for r in title_regions if r["sev"] == "HIGH"])

        if n_high >= 1:
            label  = "⚠ TAMPERING DETECTED"
            detail = (f"{len(regions)} region(s) flagged: {n_high} HIGH, "
                      f"{n_medium} MEDIUM, {n_low} LOW. "
                      f"{title_flagged} in TITLE ZONE. " +
                      ("Structural comparison with reference confirms content substitution."
                       if has_ref else
                       "ELA deficit + noise pattern indicates digitally inserted content."))
            color  = "#e74c3c"
        elif n_medium >= 2:
            label  = "⚠ LIKELY TAMPERED — REVIEW REQUIRED"
            detail = (f"{len(regions)} region(s) with {n_medium} MEDIUM anomaly scores. "
                      "Consistent with digital text insertion or field overwrite.")
            color  = "#f39c12"
        elif n_medium == 1:
            label  = "⚠ SUSPICIOUS — MANUAL REVIEW"
            detail = "1 MEDIUM region detected. May be editing or scanner artifact. Inspect manually."
            color  = "#f39c12"
        else:
            label  = "✓ LIKELY AUTHENTIC"
            detail = ("No significant localized anomalies. Compression artifacts appear uniform. " +
                      ("Reference comparison found no structural differences." if has_ref else
                       "No reference provided — subtle forgeries could be missed."))
            color  = "#27ae60"

        return label, detail, color


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 8 — ReportBuilder
# ══════════════════════════════════════════════════════════════════════════════

class ReportBuilder:
    """
    Matplotlib forensics report.
    Logic taken verbatim from draw_boxes(), style(), build_report() in ELA V3.
    """

    @staticmethod
    def draw_boxes(ax, regions):
        for i, r in enumerate(regions):
            r0, c0, r1, c1 = r["bbox"]
            col = SEV[r["sev"]]
            ax.add_patch(mpatches.Rectangle((c0, r0), c1-c0, r1-r0,
                linewidth=2.5, edgecolor=col, facecolor="none", zorder=5))
            y_t = r0 - 5 if r0 > 25 else r1 + 5
            ax.text(c0, y_t, f"R{i+1} {r['sev']}\n{r['mean']:.3f}",
                    color=col, fontsize=6.5, fontweight="bold",
                    va="bottom" if r0 > 25 else "top", ha="left", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25",
                              facecolor="#0d0f14", edgecolor=col, alpha=0.9))

    @staticmethod
    def style(ax, title):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=TXT, fontsize=9, fontweight="bold", pad=5)
        for sp in ax.spines.values():
            sp.set_edgecolor("#2a2f3d")
        ax.tick_params(colors=TICK, labelsize=7)

    def build(self, suspect, ela, ela_d, nm, sd, smap, regions,
              outpath, has_ref, label, detail, vcol):
        img  = np.asarray(suspect.convert("RGB"))
        H, W = img.shape[:2]

        fig = plt.figure(figsize=(26, 15), facecolor=BG)
        gs  = gridspec.GridSpec(2, 5, figure=fig, hspace=0.35, wspace=0.06,
                                left=0.02, right=0.98, top=0.91, bottom=0.10)

        # Col 0 — Original
        ax0 = fig.add_subplot(gs[0:2, 0])
        self.style(ax0, "Original Document")
        ax0.imshow(img); ax0.axis("off")

        # Col 1 — Raw ELA
        ax1 = fig.add_subplot(gs[0:2, 1])
        self.style(ax1, f"Raw ELA (Q={JPEG_QUALITY}, ×{AMPLIFY})\nHIGH = real text/artifacts")
        ax1.imshow(ela, cmap=CMAP, vmin=0, vmax=1, interpolation="lanczos")
        ax1.axis("off")
        cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=CMAP),
                          ax=ax1, fraction=0.03, pad=0.02)
        cb.ax.yaxis.set_tick_params(color=TICK, labelsize=7)
        cb.outline.set_edgecolor("#2a2f3d")
        cb.set_label("ELA", color=TICK, fontsize=7)

        # Col 2 — ELA Deficit
        ax2 = fig.add_subplot(gs[0:2, 2])
        self.style(ax2, "ELA Deficit Map\nHIGH = digitally inserted (no JPEG history)")
        ax2.imshow(ela_d, cmap="plasma", vmin=0, vmax=1, interpolation="lanczos")
        ax2.axis("off")

        # Col 3 — Struct diff or noise overlay
        ax3 = fig.add_subplot(gs[0:2, 3])
        if sd is not None:
            self.style(ax3, "Structural Diff vs Reference\nHIGH = content changed here")
            ax3.imshow(sd, cmap="RdYlGn_r", vmin=0, vmax=1, interpolation="lanczos")
        else:
            self.style(ax3, "Scan Noise Inconsistency\nHIGH = too clean = digital origin")
            ax3.imshow(img, alpha=0.4)
            ax3.imshow(nm, cmap="hot", alpha=0.7, vmin=0, vmax=1)
        ax3.axis("off")

        # Col 4 — Combined suspicion map + boxes
        ax4 = fig.add_subplot(gs[0:2, 4])
        self.style(ax4, f"⚠ Combined Suspicion Map\n{len(regions)} region(s) flagged")
        ax4.imshow(img)
        ax4.imshow(smap, cmap=CMAP, alpha=0.55, vmin=0, vmax=1)
        self.draw_boxes(ax4, regions)
        ax4.axis("off")
        title_y = H * 0.35
        ax4.axhline(title_y, color="#00e5ff", linewidth=1.5,
                    linestyle="--", alpha=0.6, zorder=3)
        ax4.text(10, title_y - 8, "Title Zone ↑",
                 color="#00e5ff", fontsize=7, fontweight="bold")
        leg = [mpatches.Patch(facecolor=SEV[k], label=k) for k in SEV]
        ax4.legend(handles=leg, loc="lower right", fontsize=7,
                   facecolor=BG, labelcolor=TXT,
                   title="Severity", title_fontsize=7)

        # Bottom — Histogram
        ax5 = fig.add_subplot(gs[1, 1:4])
        self.style(ax5, "Suspicion Score Distribution")
        flat = smap.ravel()
        cfn  = plt.get_cmap(CMAP)
        n, bins, patches = ax5.hist(flat, bins=100, range=(0, 1),
                                    density=True, edgecolor="none", alpha=0.9)
        for p, b in zip(patches, bins[:-1]):
            p.set_facecolor(cfn(b))
        ax5.axvline(THRESHOLD, color="#00e5ff", lw=1.5, ls="-.",
                    label=f"Threshold {THRESHOLD}")
        ms  = float(smap.mean())
        p95 = float(np.percentile(smap, 95))
        ax5.axvline(ms,  color="#f9ca24", lw=1.2, ls="--", label=f"Mean {ms:.3f}")
        ax5.axvline(p95, color="#f05454", lw=1.2, ls=":",  label=f"P95 {p95:.3f}")
        ax5.legend(fontsize=7, facecolor=PANEL, edgecolor="#2a2f3d", labelcolor=TXT)
        ax5.set_xlabel("Suspicion Score", color=TICK, fontsize=8)
        ax5.set_ylabel("Density",         color=TICK, fontsize=8)
        ax5.set_xlim(0, 1)
        stats = (f"Mean:{ms:.4f}  Std:{smap.std():.4f}  Max:{smap.max():.4f}  "
                 f"P99:{np.percentile(smap,99):.4f}  "
                 f"Hot(>{THRESHOLD}):{(smap>THRESHOLD).mean()*100:.1f}%")
        ax5.text(0.98, 0.97, stats, transform=ax5.transAxes,
                 ha="right", va="top", fontsize=7, color=TXT,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e2230",
                           edgecolor="#2a2f3d", alpha=0.9))

        fig.suptitle("DOCUMENT FORENSICS — V3 ELA Tamper Diagnostics",
                     color=TXT, fontsize=13, fontweight="bold", y=0.975)

        # Region table
        if regions:
            lines = ["  Rg | Severity |    Area   | Mean Score | Max Score | BBox (row,col)"]
            lines.append("  " + "─" * 72)
            for i, r in enumerate(regions[:10]):
                r0, c0, r1, c1 = r["bbox"]
                loc = "[TITLE ZONE]" if r0 < H*0.35 else "[BODY]"
                lines.append(
                    f"  R{i+1:<2} | {r['sev']:<8} | {r['area']:>8}px | "
                    f"{r['mean']:.4f}     | {r['max']:.4f}    | "
                    f"({r0},{c0})→({r1},{c1}) {loc}")
            tab = "\n".join(lines)
        else:
            tab = "  No anomaly regions detected above threshold."

        fig.text(0.02, 0.09, tab, ha="left", va="top", fontsize=7,
                 color="#a0aec0", fontfamily="monospace",
                 bbox=dict(boxstyle="round,pad=0.5",
                           facecolor="#0a0c12", edgecolor="#2a2f3d", alpha=0.95))

        wrapped = textwrap.fill(detail, width=120)
        fig.text(0.5, 0.015, f"VERDICT: {label}   |   {wrapped}",
                 ha="center", va="bottom", fontsize=9, color=vcol,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#13161e",
                           edgecolor=vcol, linewidth=2, alpha=0.97))

        fig.savefig(outpath, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"[✓] Saved: {outpath}")


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 9 — ForensicsPipeline  (orchestrator — same order as original run())
# ══════════════════════════════════════════════════════════════════════════════

class ForensicsPipeline:
    """
    Runs all stages in the original chronological order:
      preprocess → align → blur-check → restore → ELA → analyze → report
    """

    def run(self):
        # ── Stage 1: Load & dimensions ─────────────────────────────────────
        loader = ImageLoader()
        im     = loader.load_cv2_color(SUSPECT_PATH)
        loader.dimensions(im)

        # ── Stage 2: CNN Preprocessing ─────────────────────────────────────
        prep = ImagePreprocessor(
            image_path    = SUSPECT_PATH,
            output_folder = OUTPUT_DIR,
            normalization = 'minmax',
            save_as_numpy = False,
        )
        prep.process()

        # ── Stage 3: Form Alignment ────────────────────────────────────────
        aligner = FormAligner(
            ref_path   = REF_FORM_PATH,
            scan_path  = SCAN_PATH,
            output_dir = OUTPUT_DIR,
        )
        aligner.align()

        # ── Stage 4: Blur Detection ────────────────────────────────────────
        blur = BlurDetector(image_path=SUSPECT_PATH)
        blur.detect()

        # ── Stage 5: Wiener Restoration ───────────────────────────────────
        restorer = ImageRestorer(
            image_path  = SUSPECT_PATH,
            output_path = 'deblurred_wiener.jpg',
        )
        restorer.restore()

        # ── Stage 6 + 7 + 8: ELA → Analyze → Report  (original run() body) ──
        print(f"\n{'='*60}\n  Analyzing: {SUSPECT_PATH}\n{'='*60}")
        suspect = Image.open(SUSPECT_PATH)
        H       = np.asarray(suspect).shape[0]

        sd = None; has_ref = False
        if REFERENCE_PATH and Path(REFERENCE_PATH).exists():
            print(f"  Reference: {REFERENCE_PATH}")
            ref     = Image.open(REFERENCE_PATH)
            ela_det = ELADetector()
            sd      = ela_det.struct_diff(suspect, ref)
            has_ref = True
            print(f"  Struct diff — max:{sd.max():.4f}  mean:{sd.mean():.4f}")

        print("  Computing ELA signals...")
        ela_det = ELADetector()
        ela     = ela_det.ela_raw(suspect)
        ela_d   = ela_det.ela_deficit(suspect)
        nm      = ela_det.noise_map(suspect)
        smap    = ela_det.combine(ela_d, nm, sd)

        print(f"  Suspicion map — max:{smap.max():.4f}  mean:{smap.mean():.4f}")

        analyzer = ForgeryAnalyzer()
        regions  = analyzer.find_regions(smap)
        print(f"  Raw regions found: {len(regions)}")

        lab, det, vcol = analyzer.verdict(regions, H, has_ref)

        print(f"\n  *** VERDICT: {lab} ***")
        for i, r in enumerate(regions):
            loc = "[TITLE]" if r["bbox"][0] < H*0.35 else "[BODY]"
            print(f"  R{i+1}: {r['sev']:8s} {loc}  "
                  f"score={r['mean']:.4f}  bbox={r['bbox']}")

        ReportBuilder().build(
            suspect, ela, ela_d, nm, sd, smap,
            regions, OUTPUT_PATH, has_ref, lab, det, vcol)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ForensicsPipeline().run()
