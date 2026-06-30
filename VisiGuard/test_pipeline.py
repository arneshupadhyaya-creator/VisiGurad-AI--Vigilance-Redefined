"""
VisiGuard AI — Pre-Submission Smoke Test
=========================================
Run this before submitting to verify the full pipeline works end-to-end.

Usage:
    python test_pipeline.py

What it checks:
    1. All imports resolve (no missing packages)
    2. behavioral_layer.py is present and importable
    3. Pipeline instantiates without error (ResNet50 loads)
    4. A synthetic test image passes through all 7 layers
    5. Result dict contains all expected keys
    6. Master trust score is in [0, 100]
    7. Verdict is one of the three expected strings

Exit code 0 = all good, submit with confidence.
Exit code 1 = something is broken, check the output above.
"""

import sys
import os
import traceback
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ── ANSI colours for terminal output ─────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = []
failed = []

def ok(msg):
    print(f"  {GREEN}✓{RESET}  {msg}")
    passed.append(msg)

def fail(msg, exc=None):
    print(f"  {RED}✗  {msg}{RESET}")
    if exc:
        print(f"     {RED}{exc}{RESET}")
    failed.append(msg)

def warn(msg):
    print(f"  {YELLOW}⚠  {msg}{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# HELPER — Create a synthetic document image
# ══════════════════════════════════════════════════════════════════════════════

def make_test_image(path: str, size=(800, 600), label="TEST DOCUMENT"):
    """
    Creates a realistic-looking synthetic document image and saves it.
    Includes text fields, a border, and a fake QR-like region.
    """
    img  = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline=(0, 0, 0), width=3)

    # Header
    draw.rectangle([10, 10, size[0]-10, 70], fill=(30, 30, 100))
    draw.text((20, 25), label, fill=(255, 255, 255))

    # Fake fields
    fields = [
        ("Name",    "RAVI KUMAR SHARMA",      (40, 100)),
        ("DOB",     "15/08/1995",             (40, 140)),
        ("Aadhaar", "1234 5678 9012",         (40, 180)),
        ("PAN",     "ABCDE1234F",             (40, 220)),
        ("Address", "123, MG Road, Kota, RJ", (40, 260)),
        ("Mobile",  "9876543210",             (40, 300)),
        ("PIN",     "324001",                 (40, 340)),
    ]
    for label_txt, value, pos in fields:
        draw.text(pos, f"{label_txt}: {value}", fill=(0, 0, 0))

    # Footer
    draw.text((40, 500), "Issued by: Government of India", fill=(100, 100, 100))

    img.save(path, "JPEG", quality=92)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# TEST 1 — Imports
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{BOLD}[1/5] Checking imports…{RESET}")

required = [
    ("torch",         "PyTorch"),
    ("torchvision",   "torchvision"),
    ("cv2",           "opencv-python"),
    ("PIL",           "Pillow"),
    ("numpy",         "numpy"),
    ("scipy",         "scipy"),
    ("matplotlib",    "matplotlib"),
]
optional = [
    ("piexif",        "piexif",       "Layer 5 metadata — pip install piexif"),
    ("pytesseract",   "pytesseract",  "Layer 6 OCR — pip install pytesseract + apt install tesseract-ocr"),
]

for mod, pkg in required:
    try:
        __import__(mod)
        ok(f"{pkg}")
    except ImportError as e:
        fail(f"{pkg} — MISSING: pip install {pkg}", e)

for mod, pkg, hint in optional:
    try:
        __import__(mod)
        ok(f"{pkg} (optional)")
    except ImportError:
        warn(f"{pkg} not installed — {hint}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST 2 — behavioral_layer.py present and importable
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{BOLD}[2/5] Checking behavioral_layer.py…{RESET}")

bl_path = os.path.join(os.path.dirname(__file__), "behavioral_layer.py")
if os.path.isfile(bl_path):
    ok("behavioral_layer.py found")
else:
    fail("behavioral_layer.py NOT FOUND in same directory as visiguard_pipeline.py")

try:
    from behavioral_layer import BehavioralScoringLayer, get_behavioral_score
    ok("behavioral_layer imports OK")
except Exception as e:
    fail("behavioral_layer import failed", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST 3 — Pipeline instantiation
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{BOLD}[3/5] Instantiating pipeline (loads ResNet50)…{RESET}")

try:
    from visiguard_pipeline import VisiGuardPipeline
    pipeline = VisiGuardPipeline(output_dir="test_output")
    ok("VisiGuardPipeline instantiated — ResNet50 loaded")
except Exception as e:
    fail("Pipeline instantiation failed", traceback.format_exc())
    print(f"\n{RED}{BOLD}Cannot continue — fix instantiation error first.{RESET}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# TEST 4 — End-to-end run on synthetic image
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{BOLD}[4/5] Running end-to-end pipeline on synthetic document…{RESET}")

os.makedirs("test_output", exist_ok=True)
uploaded_path  = "test_output/test_uploaded.jpg"
template_path  = "test_output/test_template.jpg"

make_test_image(uploaded_path, label="UPLOADED DOCUMENT")
make_test_image(template_path, label="OFFICIAL TEMPLATE")

# Synthetic behavioral data
ks_seq = np.random.normal([0.08, 0.12], [0.01, 0.02],
                           size=(30, 2)).astype(np.float32)
ms_seq = np.random.normal([50, 120, 0.5], [10, 25, 0.2],
                           size=(30, 3)).astype(np.float32)

try:
    result = pipeline.run(
        uploaded_path    = uploaded_path,
        template_path    = template_path,
        keystroke_seq    = ks_seq,
        mouse_seq        = ms_seq,
        report_path      = "test_output/test_report.png",
    )
    ok("pipeline.run() completed without exception")
except Exception as e:
    fail("pipeline.run() raised an exception", traceback.format_exc())
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# TEST 5 — Validate result dict
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{BOLD}[5/5] Validating result dict…{RESET}")

REQUIRED_KEYS = [
    "forensic_score", "structural_score", "behavioral_score",
    "metadata_score", "ocr_score",
    "master_trust_score", "verdict", "document_hash", "report_path",
    "ela_verdict", "structural_verdict",
]
VALID_VERDICTS = [
    "LOW RISK", "MEDIUM RISK", "HIGH RISK",
]

for key in REQUIRED_KEYS:
    if key in result:
        ok(f"result['{key}'] = {result[key]!r}")
    else:
        fail(f"result missing key: '{key}'")

trust = result.get("master_trust_score", -1)
if 0 <= trust <= 100:
    ok(f"master_trust_score in [0,100]: {trust}")
else:
    fail(f"master_trust_score out of range: {trust}")

verdict = result.get("verdict", "")
if any(v in verdict for v in VALID_VERDICTS):
    ok(f"verdict is valid: '{verdict}'")
else:
    fail(f"verdict unexpected: '{verdict}'")

if os.path.isfile("test_output/test_report.png"):
    size_kb = os.path.getsize("test_output/test_report.png") / 1024
    ok(f"Report PNG generated ({size_kb:.1f} KB)")
else:
    fail("Report PNG was not generated")

# Verify the result dict is JSON-serialisable via to_json_safe()
# (catches numpy.bool_ / numpy.int64 / numpy.float32 leaks before they
# reach a real API response)
try:
    import json
    from visiguard_pipeline import to_json_safe
    json.dumps(to_json_safe(result))
    ok("result dict is JSON-serialisable via to_json_safe()")
except Exception as e:
    fail("result dict failed JSON serialisation", e)


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*55}")
print(f"  {GREEN}{BOLD}PASSED: {len(passed)}{RESET}   {RED}{BOLD}FAILED: {len(failed)}{RESET}")
print(f"{'═'*55}")

if failed:
    print(f"\n{RED}{BOLD}Failures:{RESET}")
    for f in failed:
        print(f"  • {f}")
    print(f"\n{RED}Fix the above before submitting.{RESET}\n")
    sys.exit(1)
else:
    print(f"\n{GREEN}{BOLD}All checks passed. Ready to submit!{RESET}\n")
    sys.exit(0)
