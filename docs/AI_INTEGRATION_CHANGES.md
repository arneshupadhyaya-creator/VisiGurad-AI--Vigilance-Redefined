# VisiGuard AI - ML Integration Changes Log

This file tracks all modifications, configuration shifts, and wrapper introductions made to integrate the Python ML module into the full-stack system.

---

## 1. Mappings of System Changes

### Change ID: CHG_001
* **File Modified**: `apps/backend/src/ai/services/aiInferenceService.js`
* **Reason for Change**: Connect Express backend to the real Python REST API server uvicorn instance, mapping pipeline metrics back to standard frontend schemas.
* **Previous Behaviour**: Threw offline error and defaulted to local simulator when calling `http://localhost:8000`.
* **New Behaviour**: Dispatches requests to `POST http://localhost:8000/predict` and `POST http://localhost:8000/predict/typing`, translating ELA regions, trust scores, and diagnostics.
* **Impact**: Full-stack E2E automation with real Python ML model scoring.
* **Rollback Procedure**: Revert to mock simulator return logic in `aiInferenceService.js`.

---

### Change ID: CHG_002
* **File Modified**: `apps/backend/src/ai/controllers/aiController.js`
* **Reason for Change**: Route the dashboard's AI Diagnostics status indicators to query real CPU/memory metrics from the running Python process.
* **Previous Behaviour**: Returned only host system OS CPU/memory stats.
* **New Behaviour**: Calls `getPythonServiceStatus()`, returning the Python uvicorn memory allocation and loaded models metadata.
* **Impact**: Accurate diagnostics tracking in client-side system control screens.
* **Rollback Procedure**: Revert `getStatus` to report local Node OS memory metrics.

---

### Change ID: CHG_003
* **File Created**: `VisiGuard/server.py`
* **Reason for Change**: Create a high-performance Python REST service daemon wrapping `visiguard_pipeline.py` and `behavioral_layer.py`.
* **Previous Behaviour**: Python files could only be run from the command line on one-off files, reloading ResNet50 model weights every time.
* **New Behaviour**: Launches FastAPI/Uvicorn server hosting ResNet50 in memory, reducing evaluation latency to sub-second durations.
* **Impact**: Clean integration layer that decouples backend JS from Python logic.
* **Rollback Procedure**: Delete `VisiGuard/server.py`.
