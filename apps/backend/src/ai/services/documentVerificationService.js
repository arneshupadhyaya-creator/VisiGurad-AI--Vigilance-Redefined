const aiInferenceService = require('./aiInferenceService');
const aiLogger = require('../utils/aiLogger');
const { ValidationError } = require('../../utils/customErrors');
const fs = require('fs');

/**
 * Document Verification Service Interface
 * Purpose: Expose document authenticity checking routines.
 * Responsibility: Enforce limits, structure inputs, and execute AI inference.
 */
class DocumentVerificationService {
  /**
   * Evaluates document integrity.
   * @param {object} file Multer file structure
   */
  async verifyDocument(file) {
    if (!file) {
      throw new ValidationError('A document file is required for verification.');
    }

    aiLogger.info('UPLOAD_COMPLETED', 'Successfully parsed document file parameters', {
      originalName: file.originalname,
      sizeBytes: file.size,
      tempPath: file.path
    });

    // Structure input payload expected by local AI contract
    const payload = {
      originalName: file.originalname,
      sizeBytes: file.size,
      tempPath: file.path,
      mimetype: file.mimetype
    };

    try {
      const response = await aiInferenceService.invokeModel('document', payload);
      return response;
    } catch (err) {
      aiLogger.error('VERIFICATION_PIPELINE_ERROR', 'Inference flow failed to verify document', {
        file: file.originalname,
        error: err.message
      });
      throw err;
    }
  }
}

module.exports = new DocumentVerificationService();
