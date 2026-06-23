# Future Extensibility Roadmap

Future development directions and scaling improvements planned for VisiGuard AI.

---

## 1. Local AI/ML Engine Enhancements
* **PyTorch Integration**: Replace the Error Level Analysis (ELA) Pillow manipulation script with deep neural network inference (e.g. ResNet50 or MobileNetV3 classifiers trained on tampered image datasets).
* **Region of Interest (RoI) Heatmaps**: Render bounding box coordinates in the API response to overlay bounding frames on the client dashboard.

---

## 2. Notification & Alerts Layer
* **Email Alerts**: Configure SMTP integrations (e.g. NodeMailer, SendGrid) to email security administrators immediately when standard threat scores cross the `75%` (Critical) threshold.
* **Webhook Dispatches**: Allow third-party systems to register Webhook URLs. VisiGuard will POST JSON payloads containing audit records upon scan completion.

---

## 3. Queue & Microservice Migration
* BullMQ with Redis to isolate the CPU-heavy image processing.
* Move the `ML` directory to a standalone Python container running FastAPI/Gunicorn.

---

## 4. Multi-Role Permissions
* Introduce role-based access controls (RBAC) in `authMiddleware`:
  * `User`: Upload files, view own logs.
  * `Security_Auditor`: Access full dashboard history, run comparative threat indices.
  * `Admin`: Delete scan histories, revoke user access, update model options.
