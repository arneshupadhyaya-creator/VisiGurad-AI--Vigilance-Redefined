# VisiGuard AI - Configuration Guide

This document describes all environmental variables and threshold settings used to fine-tune VisiGuard AI.

---

## 1. Environment variables Reference

Add these variables to `apps/backend/.env`:

* **AI_MODEL_ENDPOINT** (Default: `http://localhost:8000/predict`)
  - The HTTP endpoint of the running Python REST service uvicorn process.
* **AI_MODEL_NAME** (Default: `visiguard-resnet50`)
  - String identifier passed to python.
* **AI_TIMEOUT** (Default: `15000` ms)
  - Network timeout for requests to Python server before calling the local simulator fallback.
* **AI_RETRY_ATTEMPTS** (Default: `3`)
  - Connection retry cycles before declaring the REST server offline.
* **AI_MAX_UPLOAD_SIZE** (Default: `10485760` bytes)
  - Hard cap for Multer upload file stream parsing (10MB).

---

## 2. ML Core Thresholds

Configured inside `VisiGuard/visiguard_pipeline.py` and `behavioral_layer.py`:

* **JPEG_QUALITY** (Default: `88`): Resave quality used in ELA to compute pixel discrepancies.
* **TRUST_HIGH** (Default: `80`): Score boundary above which documents are declared authentic (LOW RISK).
* **TRUST_MEDIUM** (Default: `40`): Score boundary below which manual reviews are flagged (MEDIUM RISK). Below 40 is HIGH RISK (adaptive MFA triggered).
* **SEQ_LENGTH** (Default: `30`): Keystroke dynamics LSTM evaluation window.
