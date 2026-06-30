const documentVerificationService = require('../services/documentVerificationService');
const typingAnalysisService = require('../services/typingAnalysisService');
const monitoringService = require('../services/monitoringService');

/**
 * AI Module Controller
 * Purpose: Exposes HTTP controllers mapping AI routes.
 * Responsibility: Forward request parameters to appropriate services, catching any thrown exceptions.
 */
class AIController {
  async verifyDocument(req, res, next) {
    try {
      const result = await documentVerificationService.verifyDocument(req.file);
      res.status(200).json({
        status: 'success',
        data: result
      });
    } catch (err) {
      next(err);
    }
  }

  async analyzeTyping(req, res, next) {
    try {
      const result = await typingAnalysisService.analyzeTyping(req.body);
      res.status(200).json({
        status: 'success',
        data: result
      });
    } catch (err) {
      next(err);
    }
  }

  async getStatus(req, res, next) {
    try {
      const aiInferenceService = require('../services/aiInferenceService');
      const pythonStatus = await aiInferenceService.getPythonServiceStatus();
      const health = pythonStatus || monitoringService.getHealthMetrics();
      res.status(200).json({
        status: 'success',
        data: health
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AIController();
