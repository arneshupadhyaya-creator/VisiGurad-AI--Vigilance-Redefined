const aiInferenceService = require('./aiInferenceService');
const aiLogger = require('../utils/aiLogger');
const { typingAnalysisRequestSchema } = require('../../../../../shared/contracts/ai.contract');
const { ValidationError } = require('../../utils/customErrors');

/**
 * Typing Behavior Analysis Service
 * Purpose: Evaluates keystroke timing intervals to calculate bot probability.
 * Responsibility: Enforce request contracts, logging, and model invocations.
 */
class TypingAnalysisService {
  async analyzeTyping(metrics) {
    // 1. Validate metrics using shared Zod contract
    const validation = typingAnalysisRequestSchema.safeParse(metrics);
    if (!validation.success) {
      const errorMsg = validation.error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ');
      aiLogger.warn('TYPING_VALIDATION_FAILED', 'Malformed typing telemetry payload', {
        details: errorMsg
      });
      throw new ValidationError(`Malformed typing metrics: ${errorMsg}`);
    }

    aiLogger.info('TYPING_ANALYSIS_REQUEST', 'Received user keystroke dynamics telemetry', {
      wpm: metrics.wpm,
      variance: metrics.variance,
      pasteDetected: metrics.pasteDetected,
      autoFillDetected: metrics.autoFillDetected
    });

    try {
      const response = await aiInferenceService.invokeModel('typing', validation.data);
      return response;
    } catch (err) {
      aiLogger.error('TYPING_ANALYSIS_PIPELINE_ERROR', 'Inference flow failed to analyze typing mechanics', {
        error: err.message
      });
      throw err;
    }
  }
}

module.exports = new TypingAnalysisService();
