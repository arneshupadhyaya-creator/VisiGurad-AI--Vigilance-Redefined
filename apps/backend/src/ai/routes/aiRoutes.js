const express = require('express');
const aiController = require('../controllers/aiController');
const { protect } = require('../../middlewares/authMiddleware');
const { aiUpload, aiLimiter, cleanupTempFile } = require('../middlewares/aiSecurity');

const router = express.Router();

/**
 * AI Module Route Mapping
 * Purpose: Declares HTTP router mappings for Document Verification, Typing Analysis, and Health Status.
 * Responsibility: Apply security, upload configurations, rate limiting, and cleanup filters.
 */

router.post(
  '/verify-document',
  protect,
  aiLimiter,
  aiUpload.single('file'),
  cleanupTempFile,
  aiController.verifyDocument
);

router.post(
  '/analyze-typing',
  protect,
  aiLimiter,
  aiController.analyzeTyping
);

router.get(
  '/status',
  protect,
  aiController.getStatus
);

module.exports = router;
