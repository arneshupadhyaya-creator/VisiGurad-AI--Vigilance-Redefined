const multer = require('multer');
const path = require('path');
const fs = require('fs');
const rateLimit = require('express-rate-limit');
const aiConfig = require('../config/ai.config');
const aiLogger = require('../utils/aiLogger');
const { RateLimitError, ValidationError } = require('../../utils/customErrors');

// Ensure uploads folder exists
const uploadsDir = path.resolve(__dirname, '..', '..', '..', 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Multer storage engine configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, 'ai-' + uniqueSuffix + ext);
  }
});

// Multer upload configurations with strict MIME and Extension validation
const aiUpload = multer({
  storage: storage,
  limits: { fileSize: aiConfig.maxUploadSize }, // 10MB default
  fileFilter: (req, file, cb) => {
    aiLogger.info('UPLOAD_STARTED', 'Received document file upload attempt', {
      originalName: file.originalname,
      mimeType: file.mimetype
    });

    const allowedExtensions = /pdf|png|jpg|jpeg|tiff/;
    const allowedMimeTypes = /pdf|png|jpeg|jpg|tiff/;

    const extname = allowedExtensions.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedMimeTypes.test(file.mimetype.toLowerCase());

    if (extname && mimetype) {
      return cb(null, true);
    }

    aiLogger.warn('INVALID_FILE', 'File type rejected due to validation failure', {
      originalName: file.originalname,
      mimeType: file.mimetype
    });
    cb(new ValidationError('Invalid file format. Supported formats: PDF, PNG, JPG, JPEG, TIFF.'));
  }
});

// Custom Rate Limiter specific for AI Verify Queries
const aiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 30, // Limit each IP to 30 requests per window
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res, next) => {
    aiLogger.warn('RATE_LIMIT_EXCEEDED', 'Inference request blocked by rate limiter', {
      ip: req.ip,
      route: req.originalUrl
    });
    next(new RateLimitError('Too many requests to cybersecurity AI services. Please try again later.'));
  }
});

// Middleware hook to handle temp file deletion on route finish/failure
const cleanupTempFile = (req, res, next) => {
  res.on('finish', () => {
    if (req.file && fs.existsSync(req.file.path)) {
      try {
        fs.unlinkSync(req.file.path);
        aiLogger.info('TEMP_FILE_CLEANUP', 'Successfully cleaned up uploaded file', {
          path: req.file.path
        });
      } catch (err) {
        aiLogger.error('TEMP_FILE_CLEANUP_ERROR', 'Failed to delete temporary document file', {
          path: req.file.path,
          error: err.message
        });
      }
    }
  });
  next();
};

module.exports = {
  aiUpload,
  aiLimiter,
  cleanupTempFile
};
