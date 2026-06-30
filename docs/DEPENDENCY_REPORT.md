# VisiGuard AI - Dependency Compatibility Report

This document maps all core Python and Node.js dependencies, verifying their version alignments, installation order, and known ABI compatibility constraints.

---

## 1. Python Environment Dependencies
All Python dependencies are pinned and run under an official Windows MSC-compiled virtual environment (`Python 3.14.3 64-bit`).

| Package | Version | Layer Utilised | Role |
| :--- | :--- | :--- | :--- |
| `torch` | `2.12.1` | Layer 2 Structural | Deep learning tensor math engine for ResNet50 |
| `torchvision` | `0.27.1` | Layer 2 Structural | Pretrained ResNet50 model weights provider |
| `opencv-python` | `4.13.0.92` | Layer 0 Preprocessing | Advanced image loading, warping, and NLM denoising |
| `Pillow` | `12.2.0` | Core Image I/O | Platform-independent image buffers |
| `scipy` | `1.18.0` | Layer 1 ELA | Uniform and Laplacian filtering |
| `matplotlib` | `3.10.0` | Report Builder | Forensic comparison report rendering |
| `piexif` | `1.1.3` | Layer 5 Metadata | EXIF extraction and software checking |
| `pytesseract` | `0.3.10` | Layer 6 OCR | Document text parsing |
| `fastapi` | `0.138.2` | REST API Server | Fast, Pydantic-validated REST framework |
| `uvicorn` | `0.49.0` | Server Wrapper | High-performance ASGI server |

---

## 2. Node.js Backend Dependencies
Managed inside `apps/backend/package.json`.

| Package | Version | Role |
| :--- | :--- | :--- |
| `express` | `^5.0.0` | Core routing framework |
| `axios` | `^1.18.1` | HTTP dispatch client wrapping Python server |
| `multer` | `^1.4.5` | Document multipart file upload stream parser |
| `zod` | `^4.4.3` | Request validator enforcing contract integrity |
| `express-rate-limit` | `^7.1.0` | Safeguards endpoints against denial-of-service |

---

## 3. Installation Flow Order

1. **System Binaries (Optional)**:
   - Install Tesseract-OCR CLI binary (adds Layer 6 OCR capabilities).
   - Install Poppler CLI binary (adds PDF document parsing).
2. **Backend Services**:
   - `cd apps/backend && npm install`
3. **Python REST Service**:
   - Run `python -m venv VisiGuard/venv` using MSC Python 3.14.3.
   - Run `.\VisiGuard\venv\Scripts\pip.exe install -r VisiGuard/requirements.txt fastapi uvicorn`
