# Deployment Guide

This document describes how to deploy VisiGuard AI to development, staging, and production environments.

---

## 1. Local Development Setup

### Prerequisites
* Node.js (v18+) & npm
* MongoDB instance (Local or Atlas URI)
* Python 3 with Pillow library:
  ```bash
  pip install Pillow
  ```

### Steps
1. Clone the repository and navigate to the directory.
2. Setup environment variables:
   * Copy `apps/backend/.env.example` to `apps/backend/.env` and fill in credentials.
3. Install backend dependencies:
   ```bash
   cd apps/backend
   npm install
   ```
4. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
5. Run the backend server:
   ```bash
   cd ../backend
   npm start
   ```
6. Run the frontend development server:
   ```bash
   cd ../frontend
   npm run dev
   ```

---

## 2. Production VPS & Nginx Setup

To deploy the app to a virtual private server (VPS) behind an Nginx reverse proxy:

### Nginx Reverse Proxy Configuration
Place the following block in `/etc/nginx/sites-available/visiguard`:

```nginx
server {
    listen 80;
    server_name visiguard.ai;

    # React Frontend static build files
    location / {
        root /var/www/visiguard/apps/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Express API Reverse Proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Statically serve forensic uploads
    location /uploads/ {
        alias /var/www/visiguard/apps/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 3. Containerization (Docker Compose)

Create a root-level `docker-compose.yml` to launch MongoDB, Redis, the Express Backend, and the React Frontend together:

```yaml
version: '3.8'

services:
  database:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./apps/backend
    ports:
      - "5000:5000"
    environment:
      - MONGO_URI=mongodb://database:27017/visiguard
      - REDIS_HOST=redis
      - JWT_SECRET=production_secret_key
    depends_on:
      - database
      - redis
    volumes:
      - uploads-volume:/usr/src/app/uploads

volumes:
  mongo-data:
  uploads-volume:
```
