# VisiGuard AI - ML Integration Bug Report

This document records the compatibility bugs, configuration traps, and environment issues discovered during the integration of the Python ML module into the full-stack system.

---

## Bug Index

### Bug ID: BUG_001
* **Severity**: CRITICAL
* **Description**: MSYS2/MinGW Python Wheel Incompatibility
* **Location**: `VisiGuard/venv` creation step
* **Root Cause**: The developer environment's default Python interpreter is MinGW-based (`GCC UCRT 14.2.0`). Standard PyPI repositories do not distribute compiled wheels of heavy ML libraries (`torch`, `torchvision`, `opencv-python`) for the MinGW ABI, leading to `No matching distribution found` installation failures.
* **Suggested Fix**: Force venv initialization using the official Windows MSVC Python interpreter path (`C:\Users\Sanskar Sahu\AppData\Local\Python\bin\python.exe`).
* **Status**: FIXED
* **Risk Level**: HIGH

---

### Bug ID: BUG_002
* **Severity**: HIGH
* **Description**: Numpy Serialisation JSON Failures
* **Location**: `visiguard_pipeline.py` & `VisiGuard/server.py`
* **Root Cause**: Python's native `json.dumps()` and FastAPI's standard json encoders do not serialize numpy-specific data types (e.g. `numpy.bool_`, `numpy.float32`, `numpy.int64`). Since ELA math comparisons return these types, requests fail with serialisation type errors.
* **Suggested Fix**: Implement a recursive helper `to_json_safe()` converting all numpy scalar data types to standard Python primitives before JSON serialization.
* **Status**: FIXED
* **Risk Level**: MEDIUM

---

### Bug ID: BUG_003
* **Severity**: MEDIUM
* **Description**: Pytesseract Binary System Dependency
* **Location**: `visiguard_pipeline.py` (Layer 6 OCR)
* **Root Cause**: `pytesseract` is a thin Python wrapper over the Tesseract CLI engine. If the `tesseract` system binary is missing from the environment PATH, the OCR step crashes.
* **Suggested Fix**: Wrap PyTesseract image calls in a try-except block, logging warning telemetry and falling back gracefully without crash-locking the pipeline.
* **Status**: FIXED
* **Risk Level**: LOW

---

### Bug ID: BUG_004
* **Severity**: MEDIUM
* **Description**: Perspective Homography Keypoint Deficit
* **Location**: `visiguard_pipeline.py` (Layer 0 FormAligner)
* **Root Cause**: If the uploaded document is highly blurred or contains no text, the ORB descriptor fails to extract the minimum 4 keypoints required for homography calculation, causing perspective wrapping to crash.
* **Suggested Fix**: Add safety checks `len(kp1) < 4 or len(kp2) < 4`. Fallback to the original unwarped scan array gracefully.
* **Status**: FIXED
* **Risk Level**: LOW
