# AI Module Security Protocols

This document details the security constraints, input filtering, and resource cleanup filters implemented for VisiGuard AI.

---

## 1. Input Sanitization & validations

* **MIME and Extension Checks**: 
  We validate both MIME types and file extensions using anchored regular expressions in `aiSecurity.js`:
  ```javascript
  const allowedExtensions = /pdf|png|jpg|jpeg|tiff/;
  ```
  This prevents malicious upload bypasses (e.g. uploading `script.sh` disguised as `image.png`).
* **Upload Size Boundaries**:
  Standard upload payload sizes are restricted via Multer options to `<= 10MB` in bytes to defend against Denial of Service (DoS) disk-exhaustion attacks.

---

## 2. Resource Cleanup Filters

To prevent disk memory leaks:
* We configure a custom Express cleanup middleware (`cleanupTempFile`).
* This registers a listener on the response `finish` stream.
* Once request evaluation completes (either on successful 200 OK or on express error catches), the temporary file is deleted from disk uploads.

---

## 3. Rate Throttling

* **IP Throttling**:
  We apply a dedicated `aiLimiter` middleware via `express-rate-limit` blocking clients exceeding 30 requests per 15 minutes.
* **Exclusion of Endpoint exposure**:
  The frontend client never calls the local AI server endpoint directly. The model server sits isolated behind our Express proxy which strips credentials and checks authorization JWTs.
