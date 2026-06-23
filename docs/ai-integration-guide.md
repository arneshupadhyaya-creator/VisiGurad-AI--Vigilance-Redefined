# AI Integration Guide

This guide explains how to plug custom machine learning or deep learning models (such as PyTorch or TensorFlow) into VisiGuard AI.

---

## AI Connection Flow Architecture

The backend utilizes an abstract service contract wrapper to connect to Python-based ELA operations. This enables seamless connection of local deep learning models.

```text
+-------------------+      (HTTP/Multipart)      +-------------------------+
|  Express Server   | -------------------------> |  Local AI Service       |
|  (Port 5000)      |                            |  (FastAPI on Port 8000) |
|                   | <------------------------- |                         |
+-------------------+      (Standard JSON)       +-------------------------+
```

---

## Expected API Contracts

To connect a new model, create a microservice (e.g. using FastAPI) exposing a POST endpoint that accepts file paths and return the validated JSON schema.

### Request Contract
```json
{
  "imagePath": "apps/backend/uploads/image-1693452.jpg",
  "outputPath": "apps/backend/uploads/ela-image-1693452.png",
  "options": {
    "quality": 90,
    "channels": "RGB"
  }
}
```

### Response Contract
```json
{
  "success": true,
  "threatScore": 42.8,
  "status": "Suspicious",
  "anomaliesCount": 3,
  "modelName": "VisiGuardResNet50",
  "completedAt": "2026-06-24T00:15:00Z"
}
```

---

## Real-Time Streaming (WebSockets)

For heavier image models (like object segmentation or localization networks) that require 1-5 seconds of GPU execution time, we outline a WebSocket event-driven notification flow:

1. **Establish Socket Connection**:
   The frontend connects to the socket endpoint on page initialization:
   `const socket = io('http://localhost:5000');`
2. **Analysis Progress Stream**:
   The backend worker updates client progress iteratively:
   ```json
   {
     "scanId": "64f019bb...",
     "stage": "COMPRESSION_DELTA_GENERATION",
     "progressPercent": 40,
     "timestamp": "2026-06-24T00:15:01Z"
   }
   ```
3. **Completion**:
   Once computation finishes, the worker broadcasts the final scan record, triggering the frontend to render overlays side-by-side.

---

## Security & Privacy Considerations

* **Sovereign Local Execution**: By running model inference locally on VPS/private servers, **no client documents are sent to third-party endpoints** (e.g. OpenAI or cloud processors). This ensures strict GDPR and HIPAA compliance.
* **Input Sanitization**: Block executable payloads or scripts masquerading as images by performing strict magic number byte audits at the Multer validation level.
