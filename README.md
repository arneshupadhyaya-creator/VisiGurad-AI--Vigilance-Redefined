# VisiGuard AI - Vigilance Redefined

VisiGuard AI is a production-grade digital forensics and image tamper-detection platform. Organised as a modern full-stack monorepo, it uses a multi-layered trust scoring system powered by local AI and computer vision models to identify compression deltas, evaluate metadata indicators, run OCR scans, and analyze user biometrics to flag forged documents.

---

## 1. Project Overview & Features

VisiGuard AI provides real-time forensic assessment of identity documents (Aadhaar, PAN cards, invoices) utilizing local computer vision (CV) and deep learning models:

* **Layered Forensic ELA**: Exposes digital modifications by evaluating pixel compression anomalies (Error Level Analysis).
* **ResNet50 Structural Analysis**: Compares uploaded document structures against official templates to detect structural forgeries.
* **Passive Keystroke Biometrics**: Evaluates user typing intervals invisibly (hold time, flight deltas, variance) using a trained `BehaviorLSTM` model to identify automated bot scripting.
* **Metadata Integrity Sweeps**: Highlights software modifications (Photoshop, GIMP), timestamp conflicts, and hardware metadata anomalies.
* **OCR Consistency Scanner**: Inspects format matching for Aadhaar (12 digits), PAN (AAAAA9999A), Mobile numbers, and DOB fields.
* **Dynamic Trust scoring**: Aggregates all model signals into a Master Trust Score (0-100) with automatic weight adjustments when templates are missing.

---

## 2. Technology Stack

* **Frontend**: React.js 19, Vite, Tailwind CSS v4, Lucide Icons, Context Session Authentication.
* **Backend**: Node.js, Express.js v5 (layered controller architecture), Multer, Mongoose, Zod validations, Express Rate Limit.
* **Database**: MongoDB for persistent audit history logging.
* **AI/ML Service**: Python 3.14 (FastAPI, Uvicorn, PyTorch ResNet50, BehaviorLSTM, PIL, OpenCV, NumPy, SciPy, Matplotlib).

---

## 3. Folder Structure Map

```text
VisiGurad-AI/
├── apps/
│   ├── backend/             # Node.js/Express.js REST Gateway
│   └── frontend/            # React/Vite/Tailwind CSS Dashboard
├── shared/
│   └── contracts/           # Shared Zod request/response validation schemas
├── VisiGuard/
│   ├── server.py            # FastAPI Python ML REST Service wrapper
│   ├── visiguard_pipeline.py# 7-layer Document Verification Pipeline
│   ├── behavioral_layer.py  # Behavioral LSTM timing analysis model
│   └── requirements.txt     # Python system packages
├── docs/                    # Architectural manuals & integration guides
└── tests/                   # Jest (Backend) and Vitest (Frontend) suites
```

---

## 4. Development Setup & Installation

### Step 1: System Binary Prerequisites
Install OCR and PDF parsing tools:
* **Windows**: Download and install Tesseract-OCR and Poppler. Add their binary paths to your system Environment PATH.
* **Linux**: `sudo apt update && sudo apt install -y tesseract-ocr poppler-utils`

### Step 2: Setup Python Virtual Environment
```bash
# Create venv using MSC python
& "C:\Users\Sanskar Sahu\AppData\Local\Python\bin\python.exe" -m venv VisiGuard/venv

# Install ML dependencies
.\VisiGuard\venv\Scripts\pip.exe install -r VisiGuard/requirements.txt fastapi uvicorn psutil
```

### Step 3: Setup Node Gateway Services
```bash
# Install backend packages
cd apps/backend
npm install

# Install frontend packages
cd ../frontend
npm install
```

---

## 5. Running the Application

### 1. Launch the Python REST Service
```bash
.\VisiGuard\venv\Scripts\python.exe VisiGuard/server.py
```
Exposes FastAPI server on `http://127.0.0.1:8000`.

### 2. Launch the Express Gateway Server
Ensure you copy and populate `apps/backend/.env.example` as `apps/backend/.env`.
```bash
cd apps/backend
npm start
```
Launches server on `http://localhost:5000`.

### 3. Launch the React Client
```bash
cd apps/frontend
npm run dev
```
Launches local dashboard on `http://localhost:5173`.

---

## 6. Environment Variables Reference

Create `apps/backend/.env`:
* `PORT`: Node server port (e.g. `5000`).
* `MONGO_URI`: MongoDB connection string (e.g. `mongodb://localhost:27017/visiguard`).
* `JWT_SECRET`: Token signature secret.
* `AI_MODEL_ENDPOINT`: Python server predict endpoint (e.g. `http://localhost:8000/predict`).
* `AI_TIMEOUT`: Connection timeout in milliseconds (e.g. `15000`).

---

## 7. Troubleshooting

* **Pip fails to download PyTorch**: This is caused by using MSYS2/MinGW Python instead of MSC Python. Recreate `venv` pointing directly to the official Python.exe install.
* **Tesseract not found**: Ensure the Tesseract-OCR folder is correctly configured in system Environment PATH. Restart command prompts to apply.
* **CORS Blocked**: Express gateway contains configured CORS filters. Set `VITE_API_BASE_URL` inside frontend variables.

---

## 8. Contributors & License
* Preserve original contributors: Arnesh Upadhyaya, Ashvind, Tejaswini, Sanskar Sahu, Bhavya.
* Preserve original license: MIT License.
