# VisiGuard AI - Integration Test Report

This document records the test cases, execution details, expected results, and actual results of the full-stack system and Python ML server integration.

---

## 1. Test Execution Scope

Verification covers:
* **End-to-End File Upload**: Frontend file uploading via Express Gateway to Python REST API server.
* **Multimodal Risk Classification**: Execution of ELA and ResNet50 comparison on synthetic and custom document templates.
* **Keystroke dynamics**: Dispatching timing statistics arrays, generating synthetic sequences, and running Behavioral LSTM scoring.
* **Offline Resiliency**: Correct simulator fallbacks when uvicorn daemon is offline.

---

## 2. Integration Test Cases

| Case ID | Feature under Test | Test Input / Action | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC_001** | Python Server Boot | Launch `server.py` | FastAPI app starts on port 8000. ResNet50 loads once. | App starts, ResNet50 loads successfully. | **PASS** |
| **TC_002** | ELA & ResNet Verification | Upload `uploaded_doc.JPG` against `official_template.jpg` | Returns Master Trust Score, ela_regions, metadata details, and report PNG path. | Returns valid JSON with ELA regions and trust score. | **PASS** |
| **TC_003** | Keystroke Biometrics | Submit keystroke statistics to `/api/ai/analyze-typing` | Python reconstructs sequence of 30, evaluates LSTM model, and returns bot risk level. | Bot probability returned with risk rating (e.g. LOW). | **PASS** |
| **TC_004** | OCR Graceful Fallback | Upload image without pytesseract binary installed | Logs warning and falls back to a neutral ocr_score (70) without crashing. | Handled gracefully. System logs OCR warning. | **PASS** |
| **TC_005** | Offline Gateway Fallback | Query `/api/ai/verify-document` with Python server killed | Express catches connection failure, calls local simulator, and returns mock response. | Connection failure caught. Simulator serves correct JSON. | **PASS** |
| **TC_006** | File Upload Constraints | Upload 12MB PNG file | Express Multer middleware intercepts file size and blocks request with HTTP 400. | Blocked at gateway level. Size warning rendered. | **PASS** |
| **TC_007** | Disk Cleanup Verification | Complete document analysis request | Check `apps/backend/uploads/` directory for uploaded file. | Temp upload file deleted from directory instantly. | **PASS** |
