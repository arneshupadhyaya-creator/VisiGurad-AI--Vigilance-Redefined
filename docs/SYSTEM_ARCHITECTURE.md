# VisiGuard AI - System Architecture

This document describes the layered architectural design, model lifecycle management, and multimodal trust scoring calculations.

---

## 1. Modular Integration Architecture

VisiGuard AI isolates its cybersecurity ML components from both the Express API and React SPA. This preserves clean code paths and avoids dependency lockups:

```text
┌────────────────────────────────────────────────────────┐
│                        React SPA                       │
└───────────────────────────┬────────────────────────────┘
                            │ (Axios API calls via JWT)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Express Gateway API                  │
├────────────────────────────────────────────────────────┤
│ - Authentication (JWT checks)                          │
│ - Upload Security & Validation (Multer checks)         │
│ - Disk Cleanup Hooks                                   │
└───────────────────────────┬────────────────────────────┘
                            │ (Axios HTTP Request)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI REST Server                  │
├────────────────────────────────────────────────────────┤
│ - Model weight instantiation (ResNet50 / LSTM in memory)│
│ - Multimodal risk scoring execution                    │
└────────────────────────────────────────────────────────┘
```

---

## 2. Model Lifecycle Management

* **Warm Startup**: The FastAPI server instantiates the PyTorch ResNet50 extractor *once* when the uvicorn process starts. Subsequent calls query this instance directly in VRAM/RAM, resulting in fast execution times.
* **Stateless Operations**: No document image data is saved permanently inside the ML service. Output reports and parsed files reside only in backend uploads folders managed by backend cleanup hooks.

---

## 3. Multimodal Scoring Aggregation

The final trust score is calculated as a weighted sum of the active layer results:

$$\text{Trust Score} = w_1 S_{\text{forensic}} + w_2 S_{\text{structural}} + w_3 S_{\text{behavioral}} + w_4 S_{\text{metadata}} + w_5 S_{\text{ocr}}$$

### Weight Distributions
* **With Template**:
  - Forensic: 0.30, Structural: 0.30, Behavioral: 0.15, Metadata: 0.15, OCR: 0.10
* **Without Template** (Structural weight redistributed):
  - Forensic: 0.38, Structural: 0.00, Behavioral: 0.22, Metadata: 0.25, OCR: 0.15
