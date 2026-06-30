import os
import sys
import time
import psutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import numpy as np

# Ensure the parent directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visiguard_pipeline import VisiGuardPipeline, to_json_safe

app = FastAPI(title="VisiGuard AI Inference Server", version="1.0.0")

# Global pipeline instance (loads ResNet50 once on startup)
print("[SERVER] Initializing VisiGuard ML pipeline...")
pipeline_instance = None
start_time = time.time()
total_processed = 0
latency_sum = 0.0

try:
    pipeline_instance = VisiGuardPipeline(output_dir="apps/backend/uploads")
    print("[SERVER] ML pipeline initialized successfully.")
except Exception as e:
    print(f"[SERVER_ERROR] Failed to initialize ML pipeline: {e}")

class PredictRequest(BaseModel):
    uploaded_path: str
    template_path: Optional[str] = None
    behavioral_score: Optional[float] = 75.0

class TypingRequest(BaseModel):
    holdTime: float
    flightTime: float
    digraphLatency: float
    trigraphLatency: float
    typingSpeed: float
    wpm: float
    burstSpeed: float
    variance: float
    consistency: float
    backspaceFrequency: int
    idleTime: float
    errorRate: float
    pasteDetected: bool
    autoFillDetected: bool

@app.post("/predict")
def predict(payload: PredictRequest):
    global total_processed, latency_sum
    if not pipeline_instance:
        raise HTTPException(status_code=503, detail="VisiGuard ML Pipeline is currently offline.")

    if not os.path.exists(payload.uploaded_path):
        raise HTTPException(status_code=400, detail=f"Uploaded file not found: {payload.uploaded_path}")

    if payload.template_path and not os.path.exists(payload.template_path):
        # Fallback to default template if the custom one is missing
        payload.template_path = None

    t0 = time.time()
    try:
        result = pipeline_instance.run(
            uploaded_path=payload.uploaded_path,
            template_path=payload.template_path,
            behavioral_score=payload.behavioral_score
        )
        latency = (time.time() - t0) * 1000.0  # ms
        total_processed += 1
        latency_sum += latency

        # Return json-serializable output
        return {
            "success": True,
            "latency_ms": round(latency, 2),
            "data": to_json_safe(result)
        }
    except Exception as e:
        print(f"[PREDICT_ERROR] Failed to run pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Inference execution failed: {str(e)}")

@app.post("/predict/typing")
def predict_typing(payload: TypingRequest):
    global total_processed, latency_sum
    t0 = time.time()
    try:
        from behavioral_layer import get_behavioral_score

        # Reconstruct mean hold_time and flight_time (converted to seconds if in ms)
        h_mean = payload.holdTime / 1000.0
        f_mean = payload.flightTime / 1000.0
        h_std = (payload.variance ** 0.5) / 1000.0 if payload.variance > 0 else 0.01

        # Generate synthetic sequence based on input stats
        rng = np.random.default_rng(42)
        ks_seq = rng.normal(loc=[h_mean, f_mean], scale=[h_std, 0.03], size=(30, 2)).astype(np.float32)
        # Default mouse parameters
        ms_seq = rng.normal(loc=[50.0, 120.0, 0.5], scale=[15.0, 30.0, 0.3], size=(30, 3)).astype(np.float32)
        
        # If paste or autofill detected, skew coordinates to trigger anomaly
        if payload.pasteDetected or payload.autoFillDetected:
            ks_seq = rng.normal(loc=[0.30, 0.50], scale=[0.15, 0.20], size=(30, 2)).astype(np.float32)
            ms_seq = rng.normal(loc=[300.0, 600.0, 5.0], scale=[100.0, 200.0, 3.0], size=(30, 3)).astype(np.float32)

        # Look for model file
        model_file = "VisiGuard/behavioral_model.pt"
        if not os.path.exists(model_file):
            model_file = "behavioral_model.pt"

        score = get_behavioral_score(ks_seq, ms_seq, model_path=model_file)

        # Translate score to probability
        # higher score (80-100) -> normal -> human (0.80 - 1.0)
        # lower score (0-40) -> anomalous -> bot
        human_probability = score / 100.0
        
        # Apply hard overrides for autofill/paste to match the security interlocks
        if payload.autoFillDetected:
            human_probability = 0.01
        elif payload.pasteDetected:
            human_probability = 0.15

        bot_probability = 1.0 - human_probability
        
        risk_level = "LOW"
        if bot_probability >= 0.85: risk_level = "VERY_HIGH"
        elif bot_probability >= 0.60: risk_level = "HIGH"
        elif bot_probability >= 0.30: risk_level = "MEDIUM"

        explanation = "Key stroke speeds and flight latencies indicate human typing pattern."
        if payload.autoFillDetected:
            explanation = "Auto-fill action detected on document forms."
        elif payload.pasteDetected:
            explanation = "Simultaneous block paste action detected on credential text fields."
        elif bot_probability > 0.60:
            explanation = "Consistent speed dynamics and lack of flight variance suggests automated robotic inputs."

        latency = (time.time() - t0) * 1000.0  # ms
        total_processed += 1
        latency_sum += latency

        return {
            "success": True,
            "data": {
                "human_probability": round(human_probability, 3),
                "bot_probability": round(bot_probability, 3),
                "risk_level": risk_level,
                "explanation": explanation,
                "confidence": int(score)
            }
        }
    except Exception as e:
        print(f"[TYPING_ERROR] Failed to analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def status():
    # Calculate CPU & memory consumption
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_used_mb = memory_info.rss / (1024 * 1024)
    
    avg_latency = (latency_sum / total_processed) if total_processed > 0 else 0.0

    return {
        "status": "success",
        "data": {
            "aiAvailable": pipeline_instance is not None,
            "modelLoaded": "ResNet50 + BehaviorLSTM (VisiGuard AI)",
            "memoryUsage": {
                "usedMB": round(memory_used_mb, 2),
                "totalMB": round(psutil.virtual_memory().total / (1024 * 1024), 2),
                "percentage": round(process.memory_percent(), 2)
            },
            "averageResponseTime": round(avg_latency, 2),
            "queueSize": 0,
            "totalProcessed": total_processed,
            "version": "1.0.0"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
