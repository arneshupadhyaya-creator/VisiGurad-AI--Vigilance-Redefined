# Backend API Documentation

Detailed reference of all available VisiGuard AI endpoints, request bodies, query constraints, and responses.

---

## Base API URL
All routes are prefixed with:
`http://localhost:5000/api`

---

## Authentication Endpoints

### 1. Register Account
* **Method**: `POST`
* **Route**: `/auth/register`
* **Description**: Registers a new auditor account.
* **Headers**: `Content-Type: application/json`
* **Request Body**:
  ```json
  {
    "email": "sanskar@visiguard.ai",
    "password": "Password123"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "status": "success",
    "message": "Account registered successfully.",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "64eff4b3d8f8...",
      "email": "sanskar@visiguard.ai",
      "role": "Security_Auditor",
      "createdAt": "2026-06-24T00:00:00.000Z"
    }
  }
  ```
* **Errors**:
  * `400 Bad Request`: Validation failure (weak password, missing fields).
  * `400 Bad Request`: Email already registered.

### 2. Login User
* **Method**: `POST`
* **Route**: `/auth/login`
* **Description**: Verifies credentials and returns session token.
* **Headers**: `Content-Type: application/json`
* **Request Body**:
  ```json
  {
    "email": "sanskar@visiguard.ai",
    "password": "Password123"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "Logged in successfully.",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "64eff4b3d8f8...",
      "email": "sanskar@visiguard.ai",
      "role": "Security_Auditor",
      "createdAt": "2026-06-24T00:00:00.000Z"
    }
  }
  ```
* **Errors**:
  * `401 Unauthorized`: Invalid email or password.
  * `429 Too Many Requests`: Too many failed attempts.

### 3. Get Active Profile
* **Method**: `GET`
* **Route**: `/auth/me`
* **Description**: Returns profile details for the authenticated user.
* **Headers**: `Authorization: Bearer <JWT>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "user": {
      "id": "64eff4b3d8f8...",
      "email": "sanskar@visiguard.ai",
      "role": "Security_Auditor",
      "createdAt": "2026-06-24T00:00:00.000Z"
    }
  }
  ```

---

## Forensic Scan Endpoints

### 1. Upload and Analyze Image
* **Method**: `POST`
* **Route**: `/scan`
* **Description**: Uploads a JPEG/PNG document to run ELA compression anomalies test.
* **Headers**:
  * `Authorization: Bearer <JWT>`
  * `Content-Type: multipart/form-data`
* **Request Body**:
  * `image`: Binary file (JPEG/PNG, Max 10MB)
* **Response (201 Created)**:
  ```json
  {
    "status": "success",
    "message": "Analysis completed successfully.",
    "scan": {
      "_id": "64f019bb8d...",
      "userId": "64eff4b3d8f8...",
      "originalName": "passport.jpg",
      "originalPath": "/uploads/image-1693452.jpg",
      "elaPath": "/uploads/ela-image-1693452.png",
      "fileSize": 104230,
      "dimensions": "Standard",
      "threatScore": 42.5,
      "status": "Suspicious",
      "createdAt": "2026-06-24T00:10:00.000Z"
    },
    "simulated": false,
    "warning": ""
  }
  ```

### 2. Fetch Scan History
* **Method**: `GET`
* **Route**: `/scans`
* **Description**: Retrieves history list.
* **Headers**: `Authorization: Bearer <JWT>`
* **Response (200 OK)**: Array of scan records.

### 3. Delete Scan Record
* **Method**: `DELETE`
* **Route**: `/scans/:id`
* **Description**: Removes database record and associated storage files.
* **Headers**: `Authorization: Bearer <JWT>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "Scan history and files deleted successfully."
  }
  ```
