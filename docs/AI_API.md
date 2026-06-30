# AI Module API Reference

This document catalogs the REST API endpoints exposed by the isolated VisiGuard AI module.

---

## 1. Verify Document Authenticity
* **Method**: `POST`
* **Route**: `/api/ai/verify-document`
* **Headers**:
  * `Authorization: Bearer <JWT>`
  * `Content-Type: multipart/form-data`
* **Request Payload**:
  * `file`: Binary file upload (PDF, PNG, JPG, JPEG, TIFF; <= 10MB)
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "authenticity": true,
      "confidence": 98.2,
      "risk_score": 0.04,
      "suspicious_regions": [],
      "explanation": [
        "All pixel regions exhibit consistent compression curves.",
        "Document metadata matches standard specs."
      ],
      "metadata_analysis": {
        "software": "Canon Scanner Software v2",
        "format": "pdf"
      },
      "tampering_detected": false
    }
  }
  ```

---

## 2. Analyze Typing Behavior Metrics
* **Method**: `POST`
* **Route**: `/api/ai/analyze-typing`
* **Headers**:
  * `Authorization: Bearer <JWT>`
  * `Content-Type: application/json`
* **Request Payload (Zod validated)**:
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
    "idleTime: 0,
    "errorRate": 0.05,
    "pasteDetected": false,
    "autoFillDetected": false
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "human_probability": 0.95,
      "bot_probability": 0.05,
      "risk_level": "LOW",
      "explanation": "Key stroke speeds and flight latencies indicate human typing pattern.",
      "confidence": 97
    }
  }
  ```

---

## 3. Get AI Health status
* **Method**: `GET`
* **Route**: `/api/ai/status`
* **Headers**: `Authorization: Bearer <JWT>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "aiAvailable": true,
      "modelLoaded": "visiguard-cyber-resnet50",
      "memoryUsage": {
        "usedMB": 8240,
        "totalMB": 16384,
        "percentage": 50.3
      },
      "averageResponseTime": 124.5,
      "queueSize": 0,
      "totalProcessed": 142,
      "version": "1.2.0-cybersecurity-core"
    }
  }
  ```
