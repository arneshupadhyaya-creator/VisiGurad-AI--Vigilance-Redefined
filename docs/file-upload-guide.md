# File Upload System Guide

VisiGuard AI incorporates a modular storage provider layer to isolate local disk operations and support cloud migrations.

---

## Upload & Forensic Lifecycle Flow

```text
  [ Client Selects File ] 
             |
             v  (Frontend Zod check: JPEG/PNG & Max 10MB)
  [ Send API POST /scan ]
             |
             v  (Multer limits and mimetype filter check)
  [ Save Original File ]  --> Saves file to apps/backend/uploads/
             |
             v  (Execute ELA Python process/simulation)
  [ Generate ELA Map ]    --> Saves heatmap.png to uploads/
             |
             v  (MongoDB writes scan document details)
  [ Log Scan to Database ]
             |
             v  (Auditor receives side-by-side images)
  [ Render in Dashboard ]
```

---

## File Upload Validation Process

### 1. Frontend validation
* Checks file type: `image/jpeg` or `image/png`.
* Checks file size limit: strictly `<= 10MB`.

### 2. Backend validation (Multer filter)
* Validates file extensions and MIME types:
  ```javascript
  const filetypes = /jpeg|jpg|png/;
  const mimetype = filetypes.test(file.mimetype);
  const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
  ```
* Rejects any non-image uploads instantly with `ValidationError`.

---

## Future Cloud Migration Strategies

Our backend is designed with a decoupled **StorageProvider** class interface. To migrate file storage to cloud architectures (e.g. AWS S3, Google Cloud Storage, or Azure Blob Storage), update the service registration in `scanService.js` to instantiate the appropriate provider:

```javascript
// apps/backend/src/services/scanService.js
// Swap:
// const storage = new LocalStorageProvider();
// To:
// const storage = new S3StorageProvider('my-s3-bucket-name');
```

No changes to controller actions, route bindings, or business logic are required because all storage interactions use the uniform `saveFile()` and `deleteFile()` methods defined in the abstract interface.
