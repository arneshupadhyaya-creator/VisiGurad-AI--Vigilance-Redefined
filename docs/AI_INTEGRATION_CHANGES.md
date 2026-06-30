# AI Integration Changes Log

This file tracks all modifications, additions, and updates made to integrate local AI capabilities into the VisiGuard AI platform.

---

## Change Log

### Phase 1: Shared API Contracts (2026-06-30)
* **Date**: 2026-06-30
* **File Name**: `shared/contracts/ai.contract.js`
* **Line/Function Modified**: Export and definitions block
* **Why the modification was necessary**: Expose schemas for validating document authenticity structures and keystroke dynamics metrics.
* **Previous Behaviour**: Only contained ELA process schemas.
* **New Behaviour**: Contains `documentVerificationResponseSchema`, `typingAnalysisRequestSchema`, and `typingAnalysisResponseSchema` validations.

### Phase 2: Layered Backend AI Module (2026-06-30)
* **Date**: 2026-06-30
* **File Name**: `apps/backend/index.js`
* **Line/Function Modified**: Route mounting
* **Why the modification was necessary**: Mount the new AI router under `/api/ai`.
* **Previous Behaviour**: Mounted only auth and scan routes.
* **New Behaviour**: Mounts `/api/ai` route maps.

* **Date**: 2026-06-30
* **Files Created**:
  * `apps/backend/src/ai/config/ai.config.js`: Central configuration manager.
  * `apps/backend/src/ai/utils/aiLogger.js`: Structured JSON logger.
  * `apps/backend/src/ai/middlewares/aiSecurity.js`: Multer PDF/TIFF upload configuration, cleanup hook, and AI-specific rate limiter.
  * `apps/backend/src/ai/services/monitoringService.js`: Health diagnostics compiler.
  * `apps/backend/src/ai/services/aiInferenceService.js`: Local REST/Ollama connection client with automated fallback simulator.
  * `apps/backend/src/ai/services/documentVerificationService.js`: Verifications service coordinator.
  * `apps/backend/src/ai/services/typingAnalysisService.js`: Keystroke metrics processor.
  * `apps/backend/src/ai/controllers/aiController.js`: Route action handlers.
  * `apps/backend/src/ai/routes/aiRoutes.js`: HTTP endpoints map.

### Phase 3: Frontend Modular Components (2026-06-30)
* **Date**: 2026-06-30
* **File Name**: `apps/frontend/src/pages/dashboard.jsx`
* **Line/Function Modified**: Tab controls and content rendering
* **Why the modification was necessary**: Integrate AI Document verification, keystroke metrics, and coprocessor status interfaces.
* **Previous Behaviour**: Displayed only ELA upload sandboxes and logs.
* **New Behaviour**: Displays interlock typing warnings and mounts new subcomponent tabs.

* **Files Created**:
  * `apps/frontend/src/ai/services/aiClient.js`: Axios request handlers.
  * `apps/frontend/src/ai/hooks/useTypingCapture.js`: Keystroke telemetry capture.
  * `apps/frontend/src/ai/components/DocumentVerifier.jsx`: Upload card.
  * `apps/frontend/src/ai/components/TypingBehaviorMonitor.jsx`: Threat warning layout.
  * `apps/frontend/src/ai/components/AIHealthPanel.jsx`: Visual diagnostic monitor.

---

## Newly Introduced Elements

### Environment Variables
* `AI_MODEL_ENDPOINT`: Endpoint for local REST inference (e.g. `http://localhost:8000/predict`).
* `AI_MODEL_NAME`: The identifier of the loaded local model (e.g. `visiguard-cyber-resnet50`).
* `AI_TIMEOUT`: Inference call timeout in milliseconds.
* `AI_MAX_UPLOAD_SIZE`: Maximum document upload limit in bytes (10MB).
* `AI_CONFIDENCE_THRESHOLD`: Min confidence % to pass authenticity checks.
* `AI_TYPING_BOT_THRESHOLD`: Threat rating above which bot warnings trigger.

### Testing Coverage
* `tests/backend/ai.test.js`: Validates request schemas and ELA fallback simulators.
* `tests/frontend/ai.test.jsx`: Validates key hold and speed calculations.
