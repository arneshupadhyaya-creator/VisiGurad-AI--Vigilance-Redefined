# VisiGuard AI - API Reference

This document catalogs the REST API interfaces connecting the full-stack system and the Python REST server.

---

## 1. Backend Proxy Endpoints (Exposed to Frontend)

### POST /api/ai/verify-document
* **Purpose**: Evaluate document authenticity.
* **Headers**: `Authorization: Bearer <JWT>`, `Content-Type: multipart/form-data`
* **Request Payload**:
  - `file`: Document file binary (PDF, PNG, JPG, JPEG, TIFF; <= 10MB)
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "authenticity": true,
      "confidence": 92.5,
      "risk_score": 0.075,
      "suspicious_regions": [],
      "explanation": [
        "No significant anomalies detected.",
        "OCR layout format consistency rating: 100/100.",
        "Metadata layer signature score: 95/100."
      ],
      "metadata_analysis": {
        "software": "Canon Scan Utility",
        "modifyDate": "2026-06-30T10:12:00Z",
        "format": "jpg"
      },
      "tampering_detected": false
    }
  }
  ```

---

## 2. Python REST Server Endpoints (Internal Gateway)

### POST http://localhost:8000/predict
* **Purpose**: Run full multimodal ELA and ResNet50 analysis.
* **Request JSON**:
  ```json
  {
    "uploaded_path": "C:\\Users\\Sanskar Sahu\\...\\apps\\backend\\uploads\\temp_doc.jpg",
    "template_path": "C:\\Users\\Sanskar Sahu\\...\\VisiGuard\\data\\official_template.jpg",
    "behavioral_score": 75.0
  }
  ```

### POST http://localhost:8000/predict/typing
* **Purpose**: Reconstruct timing parameters into sequences and evaluate Behavioral LSTM score.
* **Request JSON**:
  ```json
  {
    "holdTime": 120,
    "flightTime": 50,
    "digraphLatency": 170,
    "trigraphLatency": 290,
    "typingSpeed": 300,
    "wpm": 60,
    "burstSpeed": 350,
    "variance": 15,
    "consistency": 80,
    "backspaceFrequency": 2,
    "idleTime": 0,
    "errorRate": 0.05,
    "pasteDetected": false,
    "autoFillDetected": false
  }
  ```

### GET http://localhost:8000/status
* **Purpose**: Retrieve memory footprint, latency, and average CPU parameters.
