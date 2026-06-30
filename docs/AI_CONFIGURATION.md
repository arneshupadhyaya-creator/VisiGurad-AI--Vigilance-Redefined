# AI Module Configuration reference

All AI module options are fully configurable and read directly from environment variables.

---

## Environmental Parameters

Copy these variables into your `apps/backend/.env` file:

```env
# AI Model Endpoint
AI_MODEL_ENDPOINT=http://localhost:8000/predict
AI_MODEL_NAME=visiguard-cyber-resnet50

# Request Options
AI_TIMEOUT=10000
AI_RETRY_ATTEMPTS=3
AI_CACHE_ENABLED=false

# Upload Boundaries
AI_MAX_UPLOAD_SIZE=10485760 # 10MB in bytes

# Risk Assessment Thresholds
AI_CONFIDENCE_THRESHOLD=80.0
AI_TYPING_BOT_THRESHOLD=0.70

# Typing Severity Thresholds
AI_TYPING_SEVERITY_MEDIUM=0.30
AI_TYPING_SEVERITY_HIGH=0.60
AI_TYPING_SEVERITY_VERY_HIGH=0.85

# Structured Logger Level
AI_LOGGING_LEVEL=info
```

---

## Settings Reference

* **AI_TIMEOUT**: The maximum duration in milliseconds the service will wait for the local model endpoint to return a response before triggering auto-retry loops.
* **AI_RETRY_ATTEMPTS**: The total network retry cycles attempted before activating the fallback simulator.
* **AI_TYPING_BOT_THRESHOLD**: The probability value (0 to 1) computed for bot behavior above which alerts or locks trigger.
