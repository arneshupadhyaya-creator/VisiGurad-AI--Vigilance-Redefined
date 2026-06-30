"""
VisiGuard AI — Integrated Document Verification Pipeline  (Final Clean Version)
=================================================================================
Layers:
  0. CV Preprocessing      (ImageLoader → FormAligner → BlurDetector → ImageRestorer)
  1. ELA Forensics         (ELADetector → ForgeryAnalyzer → forensic_score)
  2. Structural Analysis   (ResNet50Extractor → SimilarityEngine → structural_score)
  3. Integrity Hashing     (SHA-256 fingerprint)
  4. Behavioral Scoring    (BehavioralScoringLayer → behavioral_score)   ← behavioral_layer.py
  5. Metadata Verification (MetadataVerifier → metadata_score)
  6. OCR Consistency       (OCRConsistencyChecker → ocr_score)
  7. Risk Engine           (MultiModalRiskEngine → 5-signal Trust Score → verdict)

Usage
-----
# Option A — pass pre-computed behavioral score (e.g. from a live frontend session):
  pipeline = VisiGuardPipeline(output_dir="output")
  result   = pipeline.run(
      uploaded_path    = "data/uploaded_doc.jpg",
      template_path    = "data/official_template.jpg",
      behavioral_score = 82.0,
  )

# Option B — pass raw biometric sequences and let the pipeline score them:
  import numpy as np
  result = pipeline.run(
      uploaded_path  = "data/doc.jpg",
      template_path  = "data/template.jpg",
      keystroke_seq  = np.array([[0.08, 0.12], ...]),   # (T, 2)
      mouse_seq      = np.array([[50, 120, 1], ...]),   # (T, 3)
      behavior_model = "behavioral_model.pt",
  )
"""

import io
import os
import hashlib
import warnings

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from PIL import Image
from scipy import ndimage
from scipy.ndimage import gaussian_filter, uniform_filter, laplace
from torchvision import models, transforms

# Behavioral scoring layer (behavioral_layer.py must be in the same directory)
try:
    from behavioral_layer import BehavioralScoringLayer, get_behavioral_score
    _BEHAVIORAL_AVAILABLE = True
except ImportError:
    _BEHAVIORAL_AVAILABLE = False

warnings.filterwarnings("ignore")


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

JPEG_QUALITY     = 88
AMPLIFY          = 30.0
ELA_THRESHOLD    = 0.30
ELA_THRESHOLD_HI = 0.42        # raised threshold for heavily pre-compressed JPEGs
MIN_AREA         = 300
CMAP             = "inferno"
BG, PANEL, TXT, TICK = "#0d0f14", "#13161e", "#dce3f0", "#8a93a8"
SEV_COLORS       = {"HIGH": "#ff3a3a", "MEDIUM": "#ffa500", "LOW": "#ffe033"}

MAX_NUM_FEATURES = 7000
PATCH_SIZE       = 16
BLUR_CUTOFF      = 15.0
BACKGROUND_NOISE = 2.0
IMG_SIZE         = 512          # ResNet50 input resolution
IMAGENET_MEAN    = [0.485, 0.456, 0.406]
IMAGENET_STD     = [0.229, 0.224, 0.225]
N_AUGMENTS       = 3            # crops used for structural score confidence interval

# Supported input formats
# PIL handles all of these natively; PDF needs pdf2image (optional)
SUPPORTED_RASTER  = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif",
                     ".webp", ".gif", ".ppm", ".pgm", ".pbm"}
SUPPORTED_PDF     = {".pdf"}
SUPPORTED_FORMATS = SUPPORTED_RASTER | SUPPORTED_PDF

# Trust score thresholds (aligned with flowchart)
TRUST_HIGH   = 80   # Document Verified        (>80)
TRUST_MEDIUM = 40   # Manual Review            (40-79)
                    # HIGH RISK / MFA           (<40)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 0 — CV PREPROCESSING
# ══════════════════════════════════════════════════════════════════════════════

class ImageLoader:
    """
    Format-aware image loader.

    Supported formats
    -----------------
    Raster : JPEG, PNG, BMP, TIFF, WEBP, GIF (first frame), PPM/PGM/PBM
    PDF    : first page rendered at 200 DPI via pdf2image (requires poppler)
             Falls back gracefully if pdf2image is not installed.
    RGBA   : alpha channel stripped — composited onto white background
             so downstream ELA and ResNet50 always receive clean RGB.

    All outputs are normalised to BGR (for cv2) or RGB (for PIL).
    """

    # Extensions that cv2.imread handles natively
    _CV2_NATIVE = {".jpg", ".jpeg", ".png", ".bmp",
                   ".tiff", ".tif", ".ppm", ".pgm", ".pbm", ".webp"}

    @staticmethod
    def _pdf_to_pil(path: str) -> Image.Image:
        """Render the first page of a PDF to a PIL Image."""
        try:
            from pdf2image import convert_from_path
            pages = convert_from_path(path, dpi=200, first_page=1, last_page=1)
            if not pages:
                raise ValueError("PDF produced no pages")
            print("  PDF rendered at 200 DPI (first page)")
            return pages[0].convert("RGB")
        except ImportError:
            raise ImportError(
                "pdf2image not installed — cannot process PDF files. "
                "Install: pip install pdf2image. "
                "System: sudo apt install poppler-utils (Linux) "
                "or brew install poppler (macOS)"
            )

    @staticmethod
    def _strip_alpha(pil_img: Image.Image) -> Image.Image:
        """Composite RGBA/LA onto a white background → RGB."""
        if pil_img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", pil_img.size, (255, 255, 255))
            mask = pil_img.split()[-1]          # alpha channel
            bg.paste(pil_img.convert("RGB"), mask=mask)
            return bg
        if pil_img.mode == "P":                 # palette mode (e.g. GIF)
            return pil_img.convert("RGB")
        return pil_img.convert("RGB")

    @classmethod
    def load_pil(cls, path: str) -> Image.Image:
        """Load any supported format → clean RGB PIL Image."""
        ext = os.path.splitext(path)[1].lower()
        if ext in SUPPORTED_PDF:
            return cls._pdf_to_pil(path)
        try:
            img = Image.open(path)
            # For GIF/APNG take only the first frame
            if hasattr(img, "n_frames") and img.n_frames > 1:
                img.seek(0)
            return cls._strip_alpha(img)
        except Exception as e:
            raise ValueError(f"Cannot open image '{path}': {e}")

    @classmethod
    def load_cv2_color(cls, path: str) -> np.ndarray:
        """Load any supported format → BGR cv2 array."""
        ext = os.path.splitext(path)[1].lower()
        if ext in SUPPORTED_PDF:
            pil = cls._pdf_to_pil(path)
            return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)

        # cv2.imread with IMREAD_UNCHANGED preserves all channels,
        # then we normalise to BGR explicitly.
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            # Fallback: PIL can open formats cv2 struggles with (e.g. WEBP on
            # some platforms, 16-bit TIFF)
            pil = cls.load_pil(path)
            return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)

        # Handle alpha (BGRA → BGR, composited on white)
        if img.ndim == 3 and img.shape[2] == 4:
            alpha = img[:, :, 3:4].astype(np.float32) / 255.0
            bgr   = img[:, :, :3].astype(np.float32)
            white = np.ones_like(bgr) * 255.0
            img   = (bgr * alpha + white * (1 - alpha)).astype(np.uint8)
        elif img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Normalise 16-bit to 8-bit (e.g. TIFF scans)
        if img.dtype != np.uint8:
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        return img

    @staticmethod
    def dimensions(img: np.ndarray):
        h, w = img.shape[:2]
        c = img.shape[2] if img.ndim > 2 else 1
        print(f"  Resolution: {w}×{h}  Channels: {c}")
        return h, w, c


class FormAligner:
    """ORB + BF-Hamming + RANSAC homography alignment."""

    def __init__(self, max_features: int = MAX_NUM_FEATURES):
        self.max_features = max_features

    def align(self, reference: np.ndarray, scan: np.ndarray) -> np.ndarray:
        """Return scan warped onto the reference frame. Returns scan unchanged on failure."""
        ref_gray  = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        scan_gray = cv2.cvtColor(scan,      cv2.COLOR_BGR2GRAY)

        orb = cv2.ORB_create(self.max_features)
        kp1, des1 = orb.detectAndCompute(ref_gray,  None)
        kp2, des2 = orb.detectAndCompute(scan_gray, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            print("  [WARN] FormAligner: not enough keypoints — skipping warp.")
            return scan

        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = sorted(matcher.match(des1, des2, None),
                         key=lambda m: m.distance)
        good = matches[:max(4, int(len(matches) * 0.05))]

        pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

        H_mat, _ = cv2.findHomography(pts2, pts1, cv2.RANSAC)
        if H_mat is None:
            print("  [WARN] FormAligner: homography failed — skipping warp.")
            return scan

        h, w = reference.shape[:2]
        return cv2.warpPerspective(scan, H_mat, (w, h))


class BlurDetector:
    """
    Laplacian patch-grid blur scorer.
    Accepts a cv2 BGR array directly (avoids re-reading from disk after alignment).
    Returns blur_pct (0–100).
    """

    def detect_array(self, img_bgr: np.ndarray) -> float:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        lap  = cv2.Laplacian(gray, cv2.CV_64F)
        h, w = gray.shape

        blurry = total = 0
        for y in range(0, h - PATCH_SIZE, PATCH_SIZE):
            for x in range(0, w - PATCH_SIZE, PATCH_SIZE):
                score = lap[y:y+PATCH_SIZE, x:x+PATCH_SIZE].var()
                if score > BACKGROUND_NOISE:
                    total += 1
                    if score < BLUR_CUTOFF:
                        blurry += 1

        pct = (blurry / total * 100) if total else 0.0
        print(f"  Blur density: {pct:.1f}%  ({'BLURRY' if pct > 1 else 'SHARP'})")
        return pct


class ImageRestorer:
    """
    Non-Local Means denoising for blur/noise reduction.

    Why NLM over Wiener:
    - Wiener assumes a Gaussian PSF — almost never true for phone camera
      motion blur or out-of-focus shots, producing ringing artefacts.
    - NLM is patch-based and noise-aware: it averages similar patches
      across the image without assuming any blur kernel shape.
    - Critically for forensics: NLM preserves edges and text sharpness
      (important for ELA), whereas Wiener smears them.

    Parameters (tunable):
      h         — filter strength. Higher = more smoothing, less noise.
                  10 is a safe default for moderate blur.
      templateWindowSize — patch size for comparison (odd, default 7).
      searchWindowSize   — search area (odd, default 21).
    """

    def restore_array(self, img_bgr: np.ndarray,
                      h: int = 10,
                      template_window: int = 7,
                      search_window: int = 21) -> np.ndarray:
        """
        Apply Non-Local Means denoising to a BGR array.
        Returns a denoised BGR array — no disk I/O.
        """
        return cv2.fastNlMeansDenoisingColored(
            img_bgr,
            None,
            h,               # luminance filter strength
            h,               # colour filter strength (same as luma)
            template_window,
            search_window,
        )


def _is_heavily_compressed(img: Image.Image, source_ext: str = ".jpg") -> bool:
    """
    Heuristic: save as JPEG Q=95 and measure mean ELA.
    High mean ELA → image has been JPEG-compressed multiple times.

    Lossless formats (PNG, BMP, TIFF, WEBP) always produce high ELA when
    first converted to JPEG — that is expected, not suspicious.
    We return False for them so the ELA threshold stays at the standard level.
    """
    _LOSSLESS = {".png", ".bmp", ".tiff", ".tif", ".webp", ".ppm",
                 ".pgm", ".pbm", ".gif", ".pdf"}
    if source_ext.lower() in _LOSSLESS:
        return False   # lossless source — not pre-compressed

    buf  = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95)
    buf.seek(0)
    rec  = np.asarray(Image.open(buf).convert("RGB"), np.float32)
    orig = np.asarray(img.convert("RGB"),             np.float32)
    mean_err = np.abs(orig - rec).mean()
    return bool(mean_err > 6.0)   # empirical threshold — cast to native bool


class CVPreprocessor:
    """
    Orchestrates the full CV pre-processing chain.
    All intermediate work is done in-memory; no temp files created here.
    Returns (clean PIL image, blur_pct, is_compressed flag).
    """

    def __init__(self, template_path: str | None = None):
        self.template_path = template_path

    def run(self, uploaded_path: str) -> tuple[Image.Image, float, bool]:
        loader   = ImageLoader()
        uploaded = loader.load_cv2_color(uploaded_path)
        loader.dimensions(uploaded)

        # Perspective alignment (only when template supplied)
        if self.template_path:
            template = loader.load_cv2_color(self.template_path)
            work_arr = FormAligner().align(template, uploaded)
            print("  Perspective alignment applied.")
        else:
            work_arr = uploaded

        # Blur detection directly on the array
        blur_pct = BlurDetector().detect_array(work_arr)

        # NLM restoration if blurry
        if blur_pct > 5.0:
            work_arr = ImageRestorer().restore_array(work_arr)
            print("  Non-Local Means restoration applied.")

        # Convert to PIL for downstream layers
        pil_img = Image.fromarray(cv2.cvtColor(work_arr, cv2.COLOR_BGR2RGB))

        # Detect multi-compression (affects ELA threshold)
        source_ext = os.path.splitext(uploaded_path)[1].lower()
        compressed = _is_heavily_compressed(pil_img, source_ext=source_ext)
        if compressed:
            print("  [INFO] Heavy JPEG compression detected — ELA threshold raised.")

        return pil_img, blur_pct, compressed, source_ext


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — ELA FORENSICS  →  forensic_score
# ══════════════════════════════════════════════════════════════════════════════

class ELADetector:

    def ela_raw(self, img: Image.Image, q: int = JPEG_QUALITY,
                source_ext: str = ".jpg") -> np.ndarray:
        """
        Error Level Analysis.

        For JPEG source images: re-compress at known quality and diff.
        For lossless formats (PNG, BMP, TIFF, WEBP): re-compress to JPEG
        once to introduce a baseline, then diff against that — this is the
        standard ELA approach for lossless sources and still reveals
        copy-paste regions (which re-compress differently from the rest).

        Note: ELA on truly lossless PNG with no prior JPEG compression will
        show near-zero error everywhere — that is the correct result.
        """
        rgb  = img.convert("RGB")
        orig = np.asarray(rgb, np.float32)
        buf  = io.BytesIO()
        # Always save as JPEG for the re-compression step — this is correct
        # ELA methodology regardless of source format.
        rgb.save(buf, "JPEG", quality=q)
        buf.seek(0)
        rec  = np.asarray(Image.open(buf).convert("RGB"), np.float32)
        diff = np.abs(orig - rec).mean(axis=2)
        return np.clip(diff * AMPLIFY / 255, 0, 1)

    def ela_deficit(self, img: Image.Image) -> np.ndarray:
        ela      = self.ela_raw(img)
        loc_mean = uniform_filter(ela, 80)
        deficit  = np.clip(loc_mean - ela, 0, None) / (loc_mean + 0.01)
        mask     = loc_mean > 0.015
        return np.clip(deficit * mask * 2.5, 0, 1)

    def noise_map(self, img: Image.Image, bs: int = 24) -> np.ndarray:
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
        arr      = np.array(noises)
        med, std = np.median(arr), arr.std() + 1e-9
        for (r, c), n in zip(coords, arr):
            z = (n - med) / std
            if z < 0:
                result[r:r+bs, c:c+bs] = np.maximum(
                    result[r:r+bs, c:c+bs], np.clip(-z / 3, 0, 1))
        return result

    def struct_diff(self, suspect: Image.Image, reference: Image.Image) -> np.ndarray:
        sg  = np.asarray(suspect.convert("L"),  np.float32) / 255
        rg  = np.asarray(reference.convert("L").resize(
              (sg.shape[1], sg.shape[0]), Image.LANCZOS), np.float32) / 255
        sb  = ndimage.binary_dilation((sg < 0.5), iterations=2).astype(np.float32)
        rb  = ndimage.binary_dilation((rg < 0.5), iterations=2).astype(np.float32)
        diff = gaussian_filter(np.abs(sb - rb), 5)
        return np.clip(diff / max(diff.max(), 1e-6) * 3, 0, 1)

    def combine(self, ela_d: np.ndarray, nm: np.ndarray,
                sd: np.ndarray | None = None) -> np.ndarray:
        if sd is not None:
            return np.clip(0.35*ela_d + 0.20*nm + 0.45*sd, 0, 1)
        return np.clip(0.55*ela_d + 0.45*nm, 0, 1)


class ForgeryAnalyzer:

    def find_regions(self, smap: np.ndarray,
                     threshold: float = ELA_THRESHOLD) -> list[dict]:
        mask       = smap >= threshold
        struct     = ndimage.generate_binary_structure(2, 2)
        dil        = ndimage.binary_dilation(mask, structure=struct, iterations=6)
        labeled, n = ndimage.label(dil, structure=struct)
        regions    = []
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

    def verdict(self, regions: list[dict], img_h: int,
                has_ref: bool) -> tuple[str, str, str]:
        title_h  = img_h * 0.35
        title_r  = [r for r in regions if r["bbox"][0] < title_h]
        for r in title_r:
            if r["sev"] == "MEDIUM":
                r["sev"] = "HIGH"   # title-zone severity upgrade

        n_high    = sum(1 for r in regions if r["sev"] == "HIGH")
        n_medium  = sum(1 for r in regions if r["sev"] == "MEDIUM")
        n_low     = sum(1 for r in regions if r["sev"] == "LOW")
        t_flagged = sum(1 for r in title_r if r["sev"] == "HIGH")

        if n_high >= 1:
            label  = "⚠ TAMPERING DETECTED"
            detail = (f"{len(regions)} region(s): {n_high} HIGH, {n_medium} MEDIUM, "
                      f"{n_low} LOW. {t_flagged} in TITLE ZONE. " +
                      ("Structural diff confirms substitution." if has_ref else
                       "ELA deficit + noise indicates digital insertion."))
            color  = "#e74c3c"
        elif n_medium >= 2:
            label  = "⚠ LIKELY TAMPERED"
            detail = f"{n_medium} MEDIUM regions — consistent with digital text insertion."
            color  = "#f39c12"
        elif n_medium == 1:
            label  = "⚠ SUSPICIOUS"
            detail = "1 MEDIUM region detected. Could be scanner artifact — inspect manually."
            color  = "#f39c12"
        else:
            label  = "✓ LIKELY AUTHENTIC"
            detail = ("No significant anomalies. Compression artifacts appear uniform. " +
                      ("Reference comparison found no structural differences." if has_ref else
                       "No reference provided — subtle forgeries could be missed."))
            color  = "#27ae60"
        return label, detail, color

    def ela_to_forensic_score(self, regions: list[dict],
                              smap: np.ndarray) -> float:
        """100 = completely clean, 0 = heavy tampering."""
        if not regions:
            hot_pct = float((smap > ELA_THRESHOLD).mean())
            return round(max(0, 100 - hot_pct * 500), 2)
        severity_weights = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.2}
        penalty = sum(severity_weights[r["sev"]] * (r["mean"] / 0.55)
                      for r in regions)
        return round(max(0.0, 100.0 - penalty * 25), 2)


class ELAForensicsLayer:
    """Full ELA layer — returns (forensic_score, detail_dict)."""

    def run(self, suspect: Image.Image,
            reference: Image.Image | None = None,
            is_compressed: bool = False) -> tuple[float, dict]:

        # Raise threshold for multi-compressed images to reduce false positives
        threshold = ELA_THRESHOLD_HI if is_compressed else ELA_THRESHOLD

        ela_det = ELADetector()
        has_ref = reference is not None
        H       = np.asarray(suspect).shape[0]

        sd    = ela_det.struct_diff(suspect, reference) if has_ref else None
        ela   = ela_det.ela_raw(suspect)
        ela_d = ela_det.ela_deficit(suspect)
        nm    = ela_det.noise_map(suspect)
        smap  = ela_det.combine(ela_d, nm, sd)

        analyzer = ForgeryAnalyzer()
        regions  = analyzer.find_regions(smap, threshold=threshold)
        label, detail, vcol = analyzer.verdict(regions, H, has_ref)
        forensic_score = analyzer.ela_to_forensic_score(regions, smap)

        print(f"  ELA → {label}  |  forensic_score: {forensic_score}  "
              f"(threshold={'HI' if is_compressed else 'STD'}={threshold})")
        return forensic_score, {
            "ela_verdict":   label,
            "ela_detail":    detail,
            "ela_color":     vcol,
            "ela_regions":   len(regions),
            "ela_region_list": regions,      # passed to ReportBuilder for bbox drawing
            "ela_smap":      smap,
            "ela_raw":       ela,
            "ela_deficit":   ela_d,
            "noise_map":     nm,
            "struct_diff":   sd,
        }


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — STRUCTURAL ANALYSIS  →  structural_score
# Pretrained ResNet50 as a fixed feature extractor (no training needed).
# 2048-d L2-normalised embeddings compared via cosine similarity.
# N_AUGMENTS random crops produce a mean ± std confidence interval.
# ══════════════════════════════════════════════════════════════════════════════

class ResNet50Extractor:
    """
    Pretrained ResNet50 — classification head removed, all weights frozen.
    No dataset or fine-tuning required.
    Automatically uses CUDA GPU if available, else falls back to CPU.
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"  [ResNet50] Running on: {self.device}")

        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        for p in self.backbone.parameters():
            p.requires_grad = False
        self.backbone.eval()
        self.backbone.to(self.device)

    @property
    def _base_transform(self):
        return transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    @property
    def _aug_transform(self):
        return transforms.Compose([
            transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
            transforms.RandomCrop(IMG_SIZE),
            transforms.ColorJitter(brightness=0.05, contrast=0.05),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def embed(self, pil_img: Image.Image,
              augmented: bool = False) -> torch.Tensor:
        """Returns a (1, 2048) L2-normalised feature tensor on CPU."""
        t = self._aug_transform(pil_img) if augmented else \
            self._base_transform(pil_img)
        t = t.unsqueeze(0).to(self.device)
        with torch.no_grad():
            feat = self.backbone(t)
            feat = feat.view(feat.size(0), -1)
            feat = F.normalize(feat, p=2, dim=1)
        return feat.cpu()   # always return on CPU for downstream numpy ops


class SimilarityEngine:

    @staticmethod
    def cosine_similarity(e1: torch.Tensor, e2: torch.Tensor) -> float:
        return float(F.cosine_similarity(e1, e2).item())

    @staticmethod
    def euclidean_distance(e1: torch.Tensor, e2: torch.Tensor) -> float:
        return float(F.pairwise_distance(e1, e2).item())

    @staticmethod
    def structural_score(cosine: float) -> float:
        """
        Remap [0.5, 1.0] → [0, 100].
        Pretrained ResNet50 on same-type documents typically yields cosine 0.75-0.98,
        so raw * 100 compresses everything into 75-98 and loses discrimination.
        Values below 0.5 (very different doc types) clamp to 0.
        """
        remapped = (cosine - 0.5) / 0.5
        return round(max(0.0, min(remapped * 100, 100.0)), 2)

    @staticmethod
    def verdict(cosine: float) -> str:
        if cosine >= 0.92:
            return "AUTHENTIC"
        if cosine >= 0.78:
            return "SUSPICIOUS"
        return "POSSIBLE FORGERY"


class StructuralLayer:
    """
    ResNet50 structural comparison with confidence interval.
    Runs N_AUGMENTS augmented passes in addition to the base pass
    and reports mean ± std over all passes.

    Accepts a pre-built ResNet50Extractor so the model is only
    loaded once per pipeline lifetime (not once per document).
    """

    def __init__(self, extractor: ResNet50Extractor):
        self.extractor = extractor
        self.sim       = SimilarityEngine()

    def run(self, uploaded: Image.Image,
            template: Image.Image | None = None) -> tuple[float, dict]:

        if template is None:
            print("  Structural: no template supplied — defaulting to 70 (neutral).")
            return 70.0, {
                "structural_verdict":    "UNVERIFIED (no template)",
                "cosine_similarity":     None,
                "cosine_std":            None,
                "euclidean_distance":    None,
                "embedding_dim":         2048,
            }

        # Base embeddings
        e_up  = self.extractor.embed(uploaded,  augmented=False)
        e_ref = self.extractor.embed(template,  augmented=False)

        # Augmented passes for confidence interval
        cosines = [self.sim.cosine_similarity(e_up, e_ref)]
        for _ in range(N_AUGMENTS):
            au = self.extractor.embed(uploaded,  augmented=True)
            ar = self.extractor.embed(template,  augmented=True)
            cosines.append(self.sim.cosine_similarity(au, ar))

        mean_cos = float(np.mean(cosines))
        std_cos  = float(np.std(cosines))
        dist     = self.sim.euclidean_distance(e_up, e_ref)
        score    = self.sim.structural_score(mean_cos)
        verd     = self.sim.verdict(mean_cos)

        if mean_cos < 0.5:
            print(f"  [WARN] Structural: cosine={mean_cos:.4f} < 0.5 — "
                  "possible wrong document type uploaded.")

        print(f"  Structural → {verd}  cosine={mean_cos:.4f}±{std_cos:.4f}  "
              f"dist={dist:.4f}  structural_score={score}")
        return score, {
            "structural_verdict":  verd,
            "cosine_similarity":   mean_cos,
            "cosine_std":          std_cos,
            "euclidean_distance":  dist,
            "embedding_dim":       2048,
        }


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — INTEGRITY HASHING
# ══════════════════════════════════════════════════════════════════════════════

class IntegrityHasher:
    """SHA-256 fingerprint of the verified (pre-processed) image."""

    @staticmethod
    def hash_pil(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return hashlib.sha256(buf.getvalue()).hexdigest()

    @staticmethod
    def hash_file(path: str) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()




# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 — METADATA VERIFICATION
# Extracts EXIF/XMP metadata and flags anomalies:
#   - Stripped EXIF (common in edited/re-saved images)
#   - Suspicious software tags (Photoshop, GIMP, etc.)
#   - Timestamp inconsistency (modification date before creation date)
#   - Missing camera hardware info (phone cameras always embed this)
# Returns metadata_score (0-100) and detail dict.
# Dependencies: piexif, python-xmp-toolkit (optional — graceful fallback)
# ══════════════════════════════════════════════════════════════════════════════

class MetadataVerifier:
    """
    EXIF/XMP metadata forensics.

    Scoring logic (penalty-based, starts at 100):
      -30  EXIF completely absent          (highly suspicious for a phone photo)
      -25  Editing software tag present    (Photoshop, GIMP, Snapseed, etc.)
      -20  Modification timestamp < creation timestamp (physically impossible)
      -10  GPS present but coordinates are (0,0) — common copy-paste artefact
      - 5  Camera make/model absent but DateTimeOriginal present (inconsistent)

    If the document is a scanned PDF or PNG export, missing EXIF is expected
    and the penalty is halved.
    """

    # Software strings that indicate post-processing / editing
    EDITING_SOFTWARE = [
        "photoshop", "gimp", "lightroom", "snapseed", "pixlr",
        "canva", "affinity", "paint", "illustrator", "inkscape",
        "acrobat", "preview", "imagemagick", "pil", "pillow",
    ]

    def verify(self, image_path: str, source_ext: str = ".jpg") -> tuple[float, dict]:
        try:
            import piexif
            _piexif = piexif
        except ImportError:
            print("  [WARN] piexif not installed — metadata check skipped.")
            return 70.0, {"metadata_note": "piexif not installed — skipped"}

        detail: dict = {}
        penalties   = 0.0
        is_scan     = source_ext in (".png", ".tiff", ".tif", ".bmp", ".pdf")

        try:
            exif_dict = _piexif.load(image_path)
        except Exception:
            exif_dict = {}

        zeroth  = exif_dict.get("0th",  {})
        exif_tb = exif_dict.get("Exif", {})
        gps     = exif_dict.get("GPS",  {})

        # ── 1. EXIF absent ───────────────────────────────────────────────────
        has_exif = bool(zeroth or exif_tb)
        detail["exif_present"] = has_exif
        if not has_exif:
            p = 15.0 if is_scan else 30.0
            penalties += p
            detail["exif_flag"] = f"EXIF absent (penalty -{p})"

        # ── 2. Editing software ──────────────────────────────────────────────
        software_tag = zeroth.get(305, b"")   # tag 305 = Software
        if isinstance(software_tag, bytes):
            software_tag = software_tag.decode("utf-8", errors="ignore")
        software_tag = software_tag.lower().strip()
        detail["software"] = software_tag or "absent"
        if any(s in software_tag for s in self.EDITING_SOFTWARE):
            penalties += 25.0
            detail["software_flag"] = f"Editing software detected: '{software_tag}' (penalty -25)"

        # ── 3. Timestamp consistency ─────────────────────────────────────────
        dt_orig = exif_tb.get(36867)    # DateTimeOriginal
        dt_mod  = zeroth.get(306)       # DateTime (last modified)
        if dt_orig and dt_mod:
            try:
                def _parse(b):
                    s = b.decode("utf-8") if isinstance(b, bytes) else b
                    from datetime import datetime
                    return datetime.strptime(s.strip(), "%Y:%m:%d %H:%M:%S")
                t_orig = _parse(dt_orig)
                t_mod  = _parse(dt_mod)
                detail["datetime_original"] = str(t_orig)
                detail["datetime_modified"] = str(t_mod)
                if t_mod < t_orig:
                    penalties += 20.0
                    detail["timestamp_flag"] = (
                        f"Modified ({t_mod}) before Original ({t_orig}) — impossible (penalty -20)")
            except Exception:
                detail["timestamp_flag"] = "Could not parse timestamps"

        # ── 4. GPS (0,0) anomaly ─────────────────────────────────────────────
        if gps:
            lat = gps.get(2)
            lon = gps.get(4)
            if lat and lon:
                def _to_dec(coord):
                    d, m, s = coord
                    return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600
                try:
                    lat_d = _to_dec(lat)
                    lon_d = _to_dec(lon)
                    detail["gps"] = f"{lat_d:.4f}, {lon_d:.4f}"
                    if abs(lat_d) < 0.001 and abs(lon_d) < 0.001:
                        penalties += 10.0
                        detail["gps_flag"] = "GPS (0,0) — likely metadata copy-paste (penalty -10)"
                except Exception:
                    pass

        # ── 5. Missing camera make/model ─────────────────────────────────────
        make  = zeroth.get(271, b"")
        model = zeroth.get(272, b"")
        if isinstance(make,  bytes): make  = make.decode("utf-8",  errors="ignore").strip()
        if isinstance(model, bytes): model = model.decode("utf-8", errors="ignore").strip()
        detail["camera_make"]  = make  or "absent"
        detail["camera_model"] = model or "absent"
        if (not make and not model) and dt_orig and has_exif and not is_scan:
            penalties += 5.0
            detail["camera_flag"] = "DateTimeOriginal present but no camera make/model (penalty -5)"

        score = round(max(0.0, 100.0 - penalties), 2)
        detail["metadata_penalties"] = penalties
        print(f"  Metadata → score={score}  penalties={penalties}  "
              f"software='{detail['software']}'  exif={'yes' if has_exif else 'no'}")
        return score, detail


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 5 — OCR CONSISTENCY CHECK
# Extracts text from the document and validates field formats:
#   - Aadhaar number  : 12 digits (XXXX XXXX XXXX)
#   - PAN number      : AAAAA9999A format
#   - DOB             : DD/MM/YYYY or DD-MM-YYYY
#   - Mobile numbers  : 10 digits starting with 6-9
#   - Pincode         : 6 digits
# Returns ocr_score (0-100) and extracted fields dict.
# Dependencies: pytesseract + tesseract-ocr system package
# ══════════════════════════════════════════════════════════════════════════════

import re as _re

class OCRConsistencyChecker:
    """
    Runs Tesseract OCR on the document and validates key field formats.

    Scoring:
      Starts at 100. Each detected field that FAILS its format check
      subtracts points. Fields not found are neutral (no penalty —
      the document type may not contain them).

      -25  Aadhaar number found but invalid format
      -25  PAN number found but invalid format
      -15  DOB found but invalid date format
      -10  Mobile number found but invalid format
      - 5  Pincode found but invalid format

    A clean document with no detectable fields scores 100 (neutral).
    A document with fields that all pass validation also scores 100.
    Only format mismatches penalise the score.
    """

    # Aadhaar: 12 digits, optionally grouped as XXXX XXXX XXXX
    _RE_AADHAAR = _re.compile(r'\b(\d{4}\s?\d{4}\s?\d{4})\b')
    # PAN: 5 letters, 4 digits, 1 letter
    _RE_PAN     = _re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b')
    # DOB: DD/MM/YYYY or DD-MM-YYYY
    _RE_DOB     = _re.compile(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b')
    # Indian mobile: 10 digits starting with 6-9
    _RE_MOBILE  = _re.compile(r'\b([6-9]\d{9})\b')
    # Pincode: 6 digits (not part of a longer number)
    _RE_PIN     = _re.compile(r'(?<!\d)(\d{6})(?!\d)')

    def check(self, img: Image.Image) -> tuple[float, dict]:
        try:
            import pytesseract
        except ImportError:
            print("  [WARN] pytesseract not installed — OCR check skipped.")
            return 70.0, {"ocr_note": "pytesseract not installed — skipped"}

        try:
            # PSM 6 = assume uniform block of text (good for documents)
            text = pytesseract.image_to_string(
                img, lang="eng",
                config="--psm 6 --oem 3")
        except Exception as e:
            print(f"  [WARN] OCR failed: {e}")
            return 70.0, {"ocr_note": f"OCR error: {e}"}

        penalties = 0.0
        detail: dict = {"ocr_text_length": len(text)}

        # ── Aadhaar ──────────────────────────────────────────────────────────
        aadhaar_matches = self._RE_AADHAAR.findall(text)
        if aadhaar_matches:
            # Valid if exactly 12 digits when stripped
            raw = aadhaar_matches[0].replace(" ", "")
            valid = len(raw) == 12 and raw.isdigit()
            detail["aadhaar_found"]   = aadhaar_matches[0]
            detail["aadhaar_valid"]   = valid
            if not valid:
                penalties += 25.0
                detail["aadhaar_flag"] = "Aadhaar number found but invalid format (penalty -25)"

        # ── PAN ──────────────────────────────────────────────────────────────
        pan_matches = self._RE_PAN.findall(text)
        if pan_matches:
            pan   = pan_matches[0]
            valid = (pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha())
            detail["pan_found"] = pan
            detail["pan_valid"] = valid
            if not valid:
                penalties += 25.0
                detail["pan_flag"] = f"PAN '{pan}' failed format check (penalty -25)"

        # ── DOB ──────────────────────────────────────────────────────────────
        dob_matches = self._RE_DOB.findall(text)
        if dob_matches:
            from datetime import datetime
            dob_str = dob_matches[0]
            try:
                sep = "/" if "/" in dob_str else "-"
                d, m, y = dob_str.split(sep)
                dob_dt  = datetime(int(y), int(m), int(d))
                valid   = 1900 < dob_dt.year < 2025
                detail["dob_found"] = dob_str
                detail["dob_valid"] = valid
                if not valid:
                    penalties += 15.0
                    detail["dob_flag"] = f"DOB '{dob_str}' outside plausible range (penalty -15)"
            except Exception:
                penalties += 15.0
                detail["dob_flag"] = f"DOB '{dob_str}' could not be parsed (penalty -15)"

        # ── Mobile ───────────────────────────────────────────────────────────
        mob_matches = self._RE_MOBILE.findall(text)
        if mob_matches:
            mob   = mob_matches[0]
            valid = len(mob) == 10 and mob[0] in "6789"
            detail["mobile_found"] = mob
            detail["mobile_valid"] = valid
            if not valid:
                penalties += 10.0
                detail["mobile_flag"] = f"Mobile '{mob}' failed format check (penalty -10)"

        # ── Pincode ──────────────────────────────────────────────────────────
        pin_matches = self._RE_PIN.findall(text)
        if pin_matches:
            pin   = pin_matches[0]
            valid = len(pin) == 6 and pin.isdigit()
            detail["pincode_found"] = pin
            detail["pincode_valid"] = valid
            if not valid:
                penalties += 5.0
                detail["pincode_flag"] = f"Pincode '{pin}' failed check (penalty -5)"

        score = round(max(0.0, 100.0 - penalties), 2)
        detail["ocr_penalties"] = penalties
        n_found = sum(1 for k in detail if k.endswith("_found"))
        print(f"  OCR → score={score}  penalties={penalties}  "
              f"fields_detected={n_found}  text_length={len(text)}")
        return score, detail


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 6 — MULTIMODAL RISK ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class MultiModalRiskEngine:
    """
    Weighted aggregation of three layer scores → Master Trust Score.

    When no structural template is available, the structural weight (0.45)
    is redistributed to forensic and behavioral rather than being applied
    to a meaningless hardcoded neutral score.

    Default weights (with template):
      forensic=0.35  structural=0.45  behavioral=0.20

    Adapted weights (no template):
      forensic=0.57  structural=0.00  behavioral=0.43
      (proportionally scaled from 0.35 and 0.20, summing to 1.0)
    """

    # Weights — 7 signals, sum to 1.0
    # forensic(ELA) + structural(ResNet) are the heaviest:
    # they directly assess pixel-level and format-level authenticity.
    # metadata, ocr, qr are supplementary corroborating signals.
    _WEIGHTS_FULL = {
        "forensic":   0.30,
        "structural": 0.30,
        "behavioral": 0.15,
        "metadata":   0.15,
        "ocr":        0.10,
    }

    # When no structural template provided: redistribute structural weight
    # proportionally across remaining signals.
    _WEIGHTS_NO_TEMPLATE = {
        "forensic":   0.38,
        "structural": 0.00,
        "behavioral": 0.22,
        "metadata":   0.25,
        "ocr":        0.15,
    }

    def __init__(self, weights: dict | None = None):
        self._custom_weights = weights  # None = auto-select based on template

    def _select_weights(self, has_template: bool) -> dict:
        if self._custom_weights:
            return self._custom_weights
        return self._WEIGHTS_FULL if has_template else self._WEIGHTS_NO_TEMPLATE

    def calculate_trust_score(
        self,
        forensic: float, structural: float, behavioral: float,
        metadata: float, ocr: float,
        has_template: bool,
    ) -> float:
        w = self._select_weights(has_template)
        return round(
            forensic     * w["forensic"]
            + structural * w["structural"]
            + behavioral * w["behavioral"]
            + metadata   * w["metadata"]
            + ocr        * w["ocr"],
            2,
        )

    def classify(self, trust: float) -> str:
        if trust >= TRUST_HIGH:
            return "LOW RISK — Document Verified ✓"
        if trust >= TRUST_MEDIUM:
            return "MEDIUM RISK — Flagged for Manual Review ⚠"
        return "HIGH RISK — Adaptive MFA Triggered 🔒"

    def evaluate(
        self,
        forensic: float, structural: float, behavioral: float,
        metadata: float = 70.0, ocr: float = 70.0,
        has_template: bool = True,
    ) -> dict:
        w       = self._select_weights(has_template)
        trust   = self.calculate_trust_score(
                      forensic, structural, behavioral,
                      metadata, ocr, has_template)
        verdict = self.classify(trust)
        return {
            "forensic_score":     forensic,
            "structural_score":   structural,
            "behavioral_score":   behavioral,
            "metadata_score":     metadata,
            "ocr_score":          ocr,
            "master_trust_score": trust,
            "verdict":            verdict,
            "weights_used":       w,
            "template_available": has_template,
        }


# ══════════════════════════════════════════════════════════════════════════════
# REPORT BUILDER
# ══════════════════════════════════════════════════════════════════════════════

class ReportBuilder:

    @staticmethod
    def _draw_boxes(ax, regions: list[dict]):
        """Draw coloured bounding boxes on the Combined Suspicion Map panel."""
        for i, r in enumerate(regions):
            r0, c0, r1, c1 = r["bbox"]
            col = SEV_COLORS[r["sev"]]
            ax.add_patch(mpatches.Rectangle(
                (c0, r0), c1-c0, r1-r0,
                linewidth=2.5, edgecolor=col, facecolor="none", zorder=5))
            y_t = r0 - 5 if r0 > 25 else r1 + 5
            ax.text(c0, y_t, f"R{i+1} {r['sev']}\n{r['mean']:.3f}",
                    color=col, fontsize=6.5, fontweight="bold",
                    va="bottom" if r0 > 25 else "top", ha="left", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25",
                              facecolor="#0d0f14", edgecolor=col, alpha=0.9))

    @staticmethod
    def _style(ax, title: str):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=TXT, fontsize=9, fontweight="bold", pad=5)
        for sp in ax.spines.values():
            sp.set_edgecolor("#2a2f3d")
        ax.tick_params(colors=TICK, labelsize=7)

    def build(self, suspect: Image.Image, ela_data: dict,
              risk_result: dict, out_path: str):
        img     = np.asarray(suspect.convert("RGB"))
        ela     = ela_data["ela_raw"]
        ela_d   = ela_data["ela_deficit"]
        nm      = ela_data["noise_map"]
        sd      = ela_data["struct_diff"]
        smap    = ela_data["ela_smap"]
        regions = ela_data["ela_region_list"]    # ← was hardcoded [] before

        fig = plt.figure(figsize=(26, 16), facecolor=BG)
        gs  = gridspec.GridSpec(3, 5, figure=fig, hspace=0.40, wspace=0.06,
                                left=0.02, right=0.98, top=0.91, bottom=0.10)

        def _s(ax, t): self._style(ax, t)

        # ── Row 0-1: ELA panels ──────────────────────────────────────────────
        ax0 = fig.add_subplot(gs[0:2, 0]); _s(ax0, "Original Document")
        ax0.imshow(img); ax0.axis("off")

        ax1 = fig.add_subplot(gs[0:2, 1]); _s(ax1, f"Raw ELA (Q={JPEG_QUALITY})")
        ax1.imshow(ela, cmap=CMAP, vmin=0, vmax=1, interpolation="lanczos")
        ax1.axis("off")
        cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=CMAP),
                          ax=ax1, fraction=0.03, pad=0.02)
        cb.ax.yaxis.set_tick_params(color=TICK, labelsize=7)

        ax2 = fig.add_subplot(gs[0:2, 2]); _s(ax2, "ELA Deficit Map")
        ax2.imshow(ela_d, cmap="plasma", vmin=0, vmax=1); ax2.axis("off")

        ax3 = fig.add_subplot(gs[0:2, 3])
        if sd is not None:
            _s(ax3, "Structural Diff vs Template")
            ax3.imshow(sd, cmap="RdYlGn_r", vmin=0, vmax=1); ax3.axis("off")
        else:
            _s(ax3, "Noise Inconsistency Map")
            ax3.imshow(img, alpha=0.4)
            ax3.imshow(nm, cmap="hot", alpha=0.7, vmin=0, vmax=1); ax3.axis("off")

        ax4 = fig.add_subplot(gs[0:2, 4])
        _s(ax4, f"Combined Suspicion Map\n{ela_data['ela_verdict']}")
        ax4.imshow(img)
        ax4.imshow(smap, cmap=CMAP, alpha=0.55, vmin=0, vmax=1)
        self._draw_boxes(ax4, regions)          # ← bboxes now actually drawn
        ax4.axis("off")

        # ── Row 2: Risk score summary ────────────────────────────────────────
        ax5 = fig.add_subplot(gs[2, :])
        ax5.set_facecolor("#13161e")
        for sp in ax5.spines.values():
            sp.set_edgecolor("#2a2f3d")
        ax5.axis("off")

        rr   = risk_result
        cstd = rr.get("cosine_std")
        ci   = f"  cosine_std={cstd:.4f}" if cstd is not None else ""
        ela_v  = rr.get("ela_verdict", "N/A")
        cnn_v  = rr.get("structural_verdict", "N/A")
        summary = (
            f"  Master Trust Score: {rr['master_trust_score']:.1f} / 100"
            f"   |   Forensic: {rr['forensic_score']:.1f}"
            f"   |   Structural: {rr['structural_score']:.1f}{ci}"
            f"   |   Behavioral: {rr['behavioral_score']:.1f}"
            f"\n  VERDICT: {rr['verdict']}"
            f"\n  ELA Verdict: {ela_v}    |    CNN Verdict: {cnn_v}"
            f"\n  SHA-256: {rr.get('document_hash', 'N/A')[:48]}…"
        )
        vcol_map = {
            "LOW RISK":    "#27ae60",
            "MEDIUM RISK": "#f39c12",
            "HIGH RISK":   "#e74c3c",
        }
        vcol = next((v for k, v in vcol_map.items()
                     if k in rr["verdict"]), "#dce3f0")
        ax5.text(0.5, 0.5, summary, transform=ax5.transAxes,
                 ha="center", va="center", fontsize=10, color=vcol,
                 fontfamily="monospace",
                 bbox=dict(boxstyle="round,pad=0.6", facecolor="#0a0c12",
                           edgecolor=vcol, linewidth=2, alpha=0.97))

        fig.suptitle("VisiGuard AI — Document Forensics Report",
                     color=TXT, fontsize=14, fontweight="bold", y=0.975)
        fig.savefig(out_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  [✓] Report saved: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MASTER ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

class VisiGuardPipeline:
    """
    Single entry-point wiring all CV and ML layers together.

    The ResNet50 model is loaded once at __init__ time and reused
    across multiple run() calls (no per-document reload).

    Parameters (run)
    ----------------
    uploaded_path    : path to the document image submitted by the user
    template_path    : path to the official template (DigiLocker etc.)
                       Pass None to skip structural comparison.
    behavioral_score : pre-computed 0-100 score from the frontend LSTM layer.
                       If provided, keystroke_seq / mouse_seq are ignored.
                       Defaults to 75 (neutral) when nothing is supplied.
    keystroke_seq    : np.ndarray (T, 2) — [[hold_time, flight_time], ...]
                       Used to compute behavioral_score when not pre-supplied.
    mouse_seq        : np.ndarray (T, 3) — [[distance, velocity, clicks], ...]
                       Used alongside keystroke_seq.
    behavior_model   : path to saved BehaviorLSTM weights (.pt file).
                       Ignored if behavioral_score is pre-supplied.
    output_dir       : where the final report PNG is saved.
    report_path      : override report filename (optional).
    """

    # Minimum image dimensions the pipeline can meaningfully analyse
    _MIN_WIDTH  = 100   # pixels
    _MIN_HEIGHT = 100   # pixels
    _MAX_BYTES  = 50 * 1024 * 1024   # 50 MB hard cap

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Load ResNet50 once — reused for every document
        print("[INIT] Loading pretrained ResNet50…")
        self._extractor    = ResNet50Extractor()
        # StructuralLayer is stateless beyond the extractor — init once too
        self._struct_layer = StructuralLayer(extractor=self._extractor)
        print("[INIT] Ready.\n")

    # ── Image validation ──────────────────────────────────────────────────────

    def _validate_image(self, path: str, label: str = "image") -> None:
        """
        Defensive checks before the image enters the pipeline.
        Raises a clear exception so the caller can show a meaningful error
        instead of a cryptic numpy/PIL/torch traceback.

        Checks:
          1. File exists and is non-empty
          2. File size within 50 MB hard cap
          3. PIL can open and decode it (catches corrupt/truncated files)
          4. Image large enough for ELA and ResNet50 (>=100x100 px)
          5. Pixel array is non-empty
        """
        # 0. Extension check
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(
                f"{label} has unsupported format '{ext}'. "
                f"Supported: {sorted(SUPPORTED_FORMATS)}"
            )

        # 1. Exists and non-empty
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{label} not found: {path}")
        size_bytes = os.path.getsize(path)
        if size_bytes == 0:
            raise ValueError(f"{label} is an empty file: {path}")

        # 2. Size cap
        if size_bytes > self._MAX_BYTES:
            raise ValueError(
                f"{label} exceeds 50 MB limit "
                f"({size_bytes / 1024 / 1024:.1f} MB): {path}"
            )

        # 3. PIL can decode it (catches corrupt / truncated files)
        try:
            img = Image.open(path)
            img.verify()
        except Exception as e:
            raise ValueError(f"{label} is corrupt or not a valid image: {e}")

        # Re-open after verify() — PIL leaves file pointer unusable after verify
        try:
            img = Image.open(path).convert("RGB")
            w, h = img.size
        except Exception as e:
            raise ValueError(f"{label} could not be decoded: {e}")

        # 4. Minimum resolution
        if w < self._MIN_WIDTH or h < self._MIN_HEIGHT:
            raise ValueError(
                f"{label} is too small ({w}x{h} px). "
                f"Minimum: {self._MIN_WIDTH}x{self._MIN_HEIGHT} px."
            )

        # 5. Non-empty pixel data
        arr = np.asarray(img)
        if arr.size == 0 or arr.ndim < 2:
            raise ValueError(f"{label} produced an empty pixel array.")

        print(f"  [OK] {label} validated: {w}x{h} px  ({size_bytes / 1024:.1f} KB)")

    def run(
        self,
        uploaded_path:    str,
        template_path:    str   | None        = None,
        behavioral_score: float | None        = None,
        keystroke_seq:    "np.ndarray | None" = None,
        mouse_seq:        "np.ndarray | None" = None,
        behavior_model:   str   | None        = None,
        report_path:      str   | None        = None,
    ) -> dict:

        # ── Input validation ─────────────────────────────────────────────────
        self._validate_image(uploaded_path, label="Uploaded document")
        if template_path:
            self._validate_image(template_path, label="Template")
        print(f"\n{'═'*62}")
        print(f"  VisiGuard AI — {os.path.basename(uploaded_path)}")
        print(f"{'═'*62}")

        # ── Layer 0: CV Preprocessing ────────────────────────────────────────
        print("\n[LAYER 0] CV Preprocessing…")
        cv_prep = CVPreprocessor(template_path=template_path)
        clean_img, blur_pct, is_compressed, source_ext = cv_prep.run(uploaded_path)

        template_pil = ImageLoader.load_pil(template_path) \
                       if template_path else None

        # ── Layer 1: ELA Forensics ───────────────────────────────────────────
        print("\n[LAYER 1] ELA Forensics…")
        forensic_score, ela_data = ELAForensicsLayer().run(
            clean_img, template_pil, is_compressed=is_compressed)

        if blur_pct > 20:
            penalty = round(min(15.0, blur_pct * 0.3), 2)
            forensic_score = round(max(0.0, forensic_score - penalty), 2)
            print(f"  Blur penalty: -{penalty}  → forensic_score={forensic_score}")

        # ── Layer 2: Structural Analysis ─────────────────────────────────────
        print("\n[LAYER 2] Structural Analysis (pretrained ResNet50)…")
        structural_score, struct_data = self._struct_layer.run(clean_img, template_pil)

        # ── Layer 3: Integrity Hashing ───────────────────────────────────────
        print("\n[LAYER 3] SHA-256 Integrity Fingerprint…")
        doc_hash = IntegrityHasher.hash_pil(clean_img)
        print(f"  SHA-256: {doc_hash[:48]}…")

        # ── Layer 4: Behavioral Scoring ──────────────────────────────────────
        print("\n[LAYER 4] Behavioral Scoring…")
        behavioral_score = self._resolve_behavioral_score(
            behavioral_score, keystroke_seq, mouse_seq, behavior_model)

        # ── Layer 5: Metadata Verification ───────────────────────────────────
        print("\n[LAYER 5] Metadata Verification…")
        metadata_score, metadata_data = MetadataVerifier().verify(uploaded_path, source_ext=source_ext)

        # ── Layer 6: OCR Consistency Check ───────────────────────────────────
        print("\n[LAYER 6] OCR Consistency Check…")
        ocr_score, ocr_data = OCRConsistencyChecker().check(clean_img)

        # ── Layer 7: Risk Engine ─────────────────────────────────────────────
        print("\n[LAYER 7] Multimodal Risk Engine (5 signals)…")
        has_template = template_path is not None
        if not has_template:
            print("  [INFO] No template — structural weight redistributed.")
        risk_result = MultiModalRiskEngine().evaluate(
            forensic_score, structural_score, behavioral_score,
            metadata_score, ocr_score,
            has_template=has_template)
        risk_result["document_hash"]  = doc_hash
        risk_result["blur_pct"]       = blur_pct
        risk_result["is_compressed"]  = is_compressed

        risk_result.update({k: v for k, v in ela_data.items()
                             if not isinstance(v, np.ndarray)})
        risk_result.update(struct_data)
        risk_result.update(metadata_data)
        risk_result.update(ocr_data)

        print(f"\n{'═'*62}")
        print(f"  MASTER TRUST SCORE : {risk_result['master_trust_score']}")
        print(f"  VERDICT            : {risk_result['verdict']}")
        print(f"  ── Layer Verdicts ─────────────────────────────────────")
        print(f"  ELA (Forensic)      : {risk_result.get('ela_verdict', 'N/A')}  "
              f"(score={risk_result['forensic_score']})")
        print(f"  CNN (Structural)    : {risk_result.get('structural_verdict', 'N/A')}  "
              f"(score={risk_result['structural_score']})")
        print(f"  SHA-256            : {doc_hash[:48]}…")
        print(f"{'═'*62}\n")

        # ── Report ───────────────────────────────────────────────────────────
        if report_path is None:
            base = os.path.splitext(os.path.basename(uploaded_path))[0]
            report_path = os.path.join(self.output_dir, f"{base}_report.png")
        ReportBuilder().build(clean_img, ela_data, risk_result, report_path)
        risk_result["report_path"] = report_path

        return risk_result

    # ── Behavioral score resolver ─────────────────────────────────────────────

    def _resolve_behavioral_score(
        self,
        behavioral_score: float | None,
        keystroke_seq:    "np.ndarray | None",
        mouse_seq:        "np.ndarray | None",
        behavior_model:   str | None,
    ) -> float:
        """
        Priority order:
          1. Pre-computed behavioral_score  (passed directly — fastest)
          2. Raw keystroke + mouse sequences → scored by BehavioralScoringLayer
          3. Fallback neutral score of 75   (when nothing is available)
        """
        # Priority 1: pre-supplied score
        if behavioral_score is not None:
            try:
                score = max(0.0, min(float(behavioral_score), 100.0))
                print(f"  Using pre-supplied behavioral_score: {score}")
                return score
            except (TypeError, ValueError):
                print("  [WARN] behavioral_score invalid — falling through.")

        # Priority 2: compute from raw sequences
        if keystroke_seq is not None and mouse_seq is not None:
            if not _BEHAVIORAL_AVAILABLE:
                print("  [WARN] behavioral_layer.py not found — "
                      "defaulting to neutral 75.")
                return 75.0
            score = get_behavioral_score(
                keystroke_seq, mouse_seq, model_path=behavior_model)
            print(f"  Behavioral score from LSTM: {score}")
            return score

        # Priority 3: neutral fallback
        print("  [WARN] No behavioral data supplied — defaulting to neutral 75.")
        return 75.0


# ══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════════════════════════════

def to_json_safe(obj):
    """
    Recursively converts numpy scalar types (bool_, int64, float32, etc.)
    and numpy arrays into native Python types so the result is safe to pass
    to json.dumps().

    This is needed because numpy comparisons (e.g. `mean_err > 6.0`) return
    numpy.bool_ rather than Python's bool, and json.dumps() does not know
    how to serialise numpy types even though they look identical when printed.

    Usage:
        result = pipeline.run(...)
        json.dumps(to_json_safe(result), indent=2)
    """
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return None   # arrays (e.g. ELA heatmaps) are not meant for JSON output
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj


if __name__ == "__main__":
    import json

    # Instantiate once — ResNet50 loads here
    pipeline = VisiGuardPipeline(output_dir="output")

    # ── Option A: pass pre-computed behavioral score ──────────────────────────
    result = pipeline.run(
        uploaded_path    = "data/uploaded_doc.jpg",
        template_path    = "data/official_template.jpg",  # or None
        behavioral_score = 82.0,
    )

    # ── Option B: pass raw biometric sequences ────────────────────────────────
    # ks = np.array([[0.08, 0.12]] * 30, dtype=np.float32)   # (30, 2)
    # ms = np.array([[50, 120, 1]] * 30, dtype=np.float32)   # (30, 3)
    # result = pipeline.run(
    #     uploaded_path  = "data/uploaded_doc.jpg",
    #     template_path  = "data/official_template.jpg",
    #     keystroke_seq  = ks,
    #     mouse_seq      = ms,
    #     behavior_model = "behavioral_model.pt",
    # )

    # JSON-serialisable output (strip numpy arrays + convert numpy scalars)
    api_response = to_json_safe(result)
    print(json.dumps(api_response, indent=2))