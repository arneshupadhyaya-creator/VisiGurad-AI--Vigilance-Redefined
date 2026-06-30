# VisiGuard AI - Troubleshooting Guide

This guide provides operational workarounds and troubleshooting actions for common deployment issues.

---

## 1. Python Server Issues

### Issue: "No matching distribution found for torch"
* **Symptom**: Virtual environment pip install fails on PyTorch download.
* **Reason**: MinGW/MSYS2 python interpreter is active, which is incompatible with PyTorch standard win_amd64 wheels.
* **Solution**: Ensure you execute `venv` creation using the official Windows MSC python interpreter:
  `& "C:\Users\Sanskar Sahu\AppData\Local\Python\bin\python.exe" -m venv VisiGuard/venv`

### Issue: "Model loading failures / PyTorch out of memory"
* **Symptom**: FastAPI server crashes during startup.
* **Reason**: CUDA GPU driver conflicts or insufficient system RAM to load ResNet50 weights.
* **Solution**: Force PyTorch to run on CPU by configuring the system variables or checking `torch.device("cpu")` outputs. (The VisiGuard pipeline contains auto-fallbacks that target CPU when CUDA is missing).

---

## 2. API & File Upload Issues

### Issue: "Upload fails on size limitations"
* **Symptom**: HTTP 400 bad request returns `File size exceeds the 10MB upload threshold.`
* **Reason**: Document is larger than the 10MB limit in Multer security parameters.
* **Solution**: Downscale the scan resolution or adjust `AI_MAX_UPLOAD_SIZE` inside `apps/backend/.env`.

### Issue: "Temporary files clogging storage"
* **Symptom**: Backend disk space filling up.
* **Reason**: Cleanup middleware failing to delete temp files.
* **Solution**: Check that the Node process has read/write permissions inside `apps/backend/uploads/` and verify the `cleanupTempFile` response finish hook executes.
