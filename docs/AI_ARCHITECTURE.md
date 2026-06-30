# AI Integration Architecture

This document describes the software design, sequence dynamics, and architectural flow of the VisiGuard AI local cybersecurity coprocessor.

---

## Modular Component Design

All AI features reside in their own isolated folders, decoupled from the core application logic. This facilitates quick removal or service migration.

```text
apps/backend/src/ai/
├── config/             # Environment parameters
├── controllers/        # HTTP entry controllers
├── middlewares/        # Upload validators & rates
├── routes/             # Route mapping binds
├── services/           # Inference execution pipeline
└── utils/              # Structured JSON event logger
```

```text
apps/frontend/src/ai/
├── components/         # Interactive UI elements
├── hooks/              # Telemetry capture hooks
└── services/           # Axios network endpoints
```

---

## Data Flow Diagrams

### Document Authenticity Verification Flow

```mermaid
sequenceDiagram
    participant Frontend as React UI
    participant Middleware as Multer / Rate Limiter
    participant Backend as Express Controller
    participant Service as DocumentVerificationService
    participant Inference as AIInferenceService
    participant LocalAI as Local AI Node (Ollama/REST)

    Frontend->>Middleware: POST /verify-document (Multipart File)
    Note over Middleware: Checks Size (<10MB) & Mime (PDF/PNG/JPG/JPEG/TIFF)
    Middleware->>Backend: Safe temp file payload
    Backend->>Service: verifyDocument(file)
    Service->>Inference: invokeModel('document', payload)
    Inference->>LocalAI: POST /predict (Axios client call)
    Note over LocalAI: Model inference calculation
    LocalAI-->>Inference: Authentic / Tampered Json
    Note over Inference: Fallback simulator runs if connection refused
    Inference-->>Service: Structured contract response
    Service-->>Backend: Final assessment
    Backend-->>Frontend: 200 OK (authenticity results JSON)
    Note over Middleware: Wipes temporary file from disk uploads
```

---

## typing Dynamics sequence Flow

```mermaid
sequenceDiagram
    participant User as Auditor Keyboard
    participant Hook as useTypingCapture
    participant Frontend as React Dashboard Tab
    participant Backend as Express Controller
    participant Service as TypingAnalysisService
    participant LocalAI as Local AI Node

    User->>Hook: keyDown / keyUp events
    Note over Hook: Computes HoldTime, FlightTime, Speed, Consistency
    Frontend->>Backend: POST /analyze-typing (Telemetry Metrics)
    Backend->>Service: analyzeTyping(metrics)
    Service->>LocalAI: Run model assessment
    LocalAI-->>Service: Bot/Human probability JSON
    Service-->>Backend: risk_level (LOW/MEDIUM/HIGH/VERY_HIGH)
    Backend-->>Frontend: 200 OK
    Note over Frontend: Triggers interlocks if riskLevel HIGH / VERY_HIGH
```
