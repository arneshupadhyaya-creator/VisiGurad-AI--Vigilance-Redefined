# VisiGuard AI - Deployment Guide

This guide describes how to configure, set up, and deploy VisiGuard AI in both development and production environments.

---

## 1. Prerequisites

* **Operating System**: Windows 10/11 or Linux (Ubuntu 20.04+).
* **Node.js**: Version 20.x or newer.
* **Python**: Version 3.12+ (MSC/MSVC-compiled version required on Windows).
* **System Packages**:
  - **Tesseract OCR**: Required for Layer 6 OCR text checking.
  - **Poppler Utilities**: Required for Layer 0 PDF document rasterization.

---

## 2. Development Setup

### Step 1: Install System Packages
* **Windows**:
  - Download and install Tesseract OCR from standard installers. Add `C:\Program Files\Tesseract-OCR` to your system Environment PATH.
  - Download Poppler and extract it. Add its `bin/` folder to the system PATH.
* **Linux**:
  ```bash
  sudo apt update
  sudo apt install -y tesseract-ocr poppler-utils
  ```

### Step 2: Set Up Python Virtual Environment
Navigate to the project root and initialize a virtual environment:
```bash
# Windows (PowerShell with MSC Python)
& "C:\Users\Sanskar Sahu\AppData\Local\Python\bin\python.exe" -m venv VisiGuard/venv

# Activate and Install
.\VisiGuard\venv\Scripts\pip.exe install --upgrade pip
.\VisiGuard\venv\Scripts\pip.exe install -r VisiGuard/requirements.txt fastapi uvicorn psutil
```

### Step 3: Configure Env Settings
Create `apps/backend/.env`:
```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/visiguard
JWT_SECRET=supersecrettoken
AI_MODEL_ENDPOINT=http://localhost:8000/predict
AI_MODEL_NAME=visiguard-resnet50
```

---

## 3. Production Deployment

### Process Management
Use **PM2** (Node.js) and **Systemd** or **PM2-Python** (Python daemon) to keep processes active:

1. **Start Python Service**:
   ```bash
   # Run server daemon in background on port 8000
   .\VisiGuard\venv\Scripts\python.exe VisiGuard/server.py
   ```
2. **Start Backend Service**:
   ```bash
   cd apps/backend
   npm run start
   ```
3. **Build Frontend Static Assets**:
   ```bash
   cd apps/frontend
   npm run build
   ```
   Static files in `apps/frontend/dist` can be served using Nginx or Node's static middleware.
