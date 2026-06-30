# VisiGuard AI - Integration Guide

This guide describes how the Python ML service and the full-stack Node.js backend communicate, detailing data contracts, serialization mappings, and file persistence flows.

---

## 1. System Communication Architecture

VisiGuard AI implements a decoupled **Client-Proxy-Service** structure:

```text
React SPA (Frontend)
       │ (JSON + Multipart File via JWT Auth)
       ▼
Express API (Backend Gateway)
       │ (Axios HTTP Request)
       ▼
FastAPI Server (Python Daemon)
       │ (Loads model weights once into Memory)
       ▼
VisiGuardPipeline (Python ML Engine)
```

The frontend never communicates directly with python scripts. All execution passes through the Express API proxy gateway to enforce authentication, validation, and rate limits.

---

## 2. API Data Mappings

### Document Verification Mappings

1. **Express Upload**: Multer parses the document, saves it to `apps/backend/uploads/` on disk, and passes metadata to `aiInferenceService.js`.
2. **REST Dispatch**: Express calls `POST http://localhost:8000/predict` passing the absolute file paths:
   ```json
   {
     "uploaded_path": "C:\\path\\to\\uploads\\file.jpg",
     "template_path": "C:\\path\\to\\VisiGuard\\data\\official_template.jpg",
     "behavioral_score": 75.0
   }
   ```
3. **Response Serialization**: The Python REST server processes ELA, ResNet50 comparison, and metadata checking, returning the raw metrics.
4. **Data Normalization**: `aiInferenceService.js` transforms the python metrics to match the frontend contract:
   - `authenticity` = `master_trust_score >= 80`
   - `confidence` = `master_trust_score`
   - `risk_score` = `(100 - master_trust_score) / 100`
   - `suspicious_regions` = maps the `ela_region_list` bounding boxes (`[r0, c0, r1, c1]`) to screen overlay boxes (`{x, y, width, height}`).

---

## 3. Keystroke Telemetry Mapping

1. **Capture Hook**: `useTypingCapture.js` measures keystroke hold times and flight variances in the browser.
2. **REST Dispatch**: Express calls `POST http://localhost:8000/predict/typing` passing the stats.
3. **Sequence Reconstruction**: The Python server maps stats back into synthetic sequences of length 30 matching the mean and variance, executing BehaviorLSTM model checks.
4. **Verdict Translation**: Returns human and bot probabilities directly to the client.
