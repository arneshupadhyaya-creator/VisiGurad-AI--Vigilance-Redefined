# AI Deployment Guide

This document describes how to deploy the VisiGuard AI coprocessor node locally in production environments.

---

## 1. Hosting Local Models (Ollama Example)

To serve model weights locally on on-premise infrastructure:

1. **Install Ollama**:
   Follow instructions on [Ollama's website](https://ollama.com) to run the CLI locally.
2. **Download Target Weights**:
   ```bash
   ollama pull llama3
   ```
3. **Run Ollama Service**:
   Ollama exposes an HTTP REST server by default on port `11434`:
   `http://localhost:11434/api/generate`

---

## 2. Deploying Custom REST Inference Servers (FastAPI Example)

To deploy deep learning models (e.g. PyTorch ResNet50 pixel manipulation checkers):

1. **Setup Python Environment**:
   ```bash
   pip install fastapi uvicorn torch torchvision Pillow
   ```
2. **Launch Server**:
   Write a small FastAPI app hosting the model weights and exposing predictions. Start via:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. **Configure env settings in VisiGuard**:
   Update backend `.env` parameters to point to your FastAPI port:
   `AI_MODEL_ENDPOINT=http://localhost:8000/predict`

---

## 3. Fallback Simulator Recovery

* If the local AI GPU server experiences downtime or crashes, VisiGuard's internal **AIInferenceService** catches the connection error and triggers the built-in **Inference Fallback Simulator**.
* This executes deterministic logic based on standard document headers and metadata properties, keeping the console fully active and protecting the system from cascading crashes.
