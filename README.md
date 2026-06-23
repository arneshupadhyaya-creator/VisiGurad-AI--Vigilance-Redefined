# VisiGuard AI - Vigilance Redefined

VisiGuard AI is a production-grade digital forensics and image tamper-detection platform. Built using the **MERN Stack** (MongoDB, Express, React, Node) organized as a modern monorepo, it uses **Error Level Analysis (ELA)** to identify compression deltas in digital assets, highlighting tampered regions.

The design of the application follows a developer-first, high-contrast, premium dark aesthetic inspired by Stripe.

---

## Repository Monorepo Structure

```text
VisiGuard-AI/
├── apps/
│   ├── backend/             # Express server layered architecture
│   └── frontend/            # React + Vite + Tailwind CSS SPA
├── shared/
│   └── contracts/           # API request/response validation contracts (Zod)
├── docs/                    # Extensive technical documentation
├── tests/                   # Jest & Vitest testing suite templates
└── ML/                      # Python ML CLI wrapper (Forensic ELA Core)
```

For detailed architecture descriptions, reference the [Technical Architecture Guide](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/architecture.md).

---

## Tech Stack

### Frontend
* **React.js 19** with **Vite** build runner.
* **Tailwind CSS v4** styling framework.
* **Axios** client for network requests.
* **Context API** for global JWT session state.
* **Lucide React** icons.

### Backend
* **Node.js** with **Express.js v5** web framework.
* **Multer** multi-part file parser.
* **Mongoose ODM** for MongoDB.
* **Bcryptjs** password encryption.
* **JSONWebTokens (JWT)** stateless security sessions.
* **Express Rate Limit** brute-force blocking.
* **Zod** schema validations.

### Database
* **MongoDB** for persistent audit histories and user credentials.

---

## Quick Start Setup Guide

### 1. Prerequisites
Ensure you have the following installed:
* Node.js (v18+)
* MongoDB Server (local instance or cloud Atlas URI)
* Python 3 with the Pillow package:
  ```bash
  pip install Pillow
  ```

### 2. Backend Installation
Configure your backend env parameters. Copy the example template to `.env`:
```bash
cp apps/backend/.env.example apps/backend/.env
```
Install dependencies and boot up the server:
```bash
cd apps/backend
npm install
npm start
```
The backend server runs on `http://localhost:5000`.

### 3. Frontend Installation
Install packages and start the Vite development server:
```bash
cd apps/frontend
npm install
npm run dev
```
The React application will launch in your browser at `http://localhost:5173`.

---

## Detailed Technical Documentation
The following documents are located in the `/docs` directory:
* [Architecture Guide](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/architecture.md)
* [Authentication Notes](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/authentication-notes.md)
* [Security & Hardening Notes](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/security-notes.md)
* [API References](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/backend-api.md)
* [OpenAPI Spec](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/openapi.json)
* [Swagger Config](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/swagger.yaml)
* [AI Integration Guide](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/ai-integration-guide.md)
* [Database Design](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/database-design.md)
* [Deployment Guide](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/deployment-guide.md)
* [File Upload System Guide](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/file-upload-guide.md)
* [Environment Variables Reference](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/environment-variables.md)
* [Project Directory Structure Map](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/project-structure.md)
* [Future Roadmaps](file:///C:/Users/Sanskar%20Sahu/.gemini/antigravity/scratch/VisiGurad-AI--Vigilance-Redefined/docs/future-roadmap.md)
