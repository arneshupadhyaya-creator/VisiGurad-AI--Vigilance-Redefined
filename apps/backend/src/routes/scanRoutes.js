const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const scanController = require('../controllers/scanController');
const { protect } = require('../middlewares/authMiddleware');
const { scanLimiter } = require('../middlewares/rateLimiter');

const router = express.Router();

// Define uploads path relative to backend root (apps/backend/uploads)
const uploadsDir = path.resolve(__dirname, '..', '..', 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Multer Storage Configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname);
    cb(null, file.fieldname + '-' + uniqueSuffix + ext);
  }
});

// Multer limits & filter
const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const filetypes = /jpeg|jpg|png/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    
    if (mimetype && extname) {
      return cb(null, true);
    }
    cb(new Error('Only JPEG, JPG, and PNG image files are allowed.'));
  }
});

/**
 * Forensic Scan Routes
 * Purpose: Route mapping for document forensic check-ups and audit removals.
 */

router.post('/scan', protect, scanLimiter, upload.single('image'), scanController.createScan);
router.get('/scans', protect, scanController.getScanHistory);
router.delete('/scans/:id', protect, scanController.deleteScan);

module.exports = router;
