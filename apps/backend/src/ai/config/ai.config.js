/**
 * AI Integration Configuration Layer
 * Purpose: Centrally manages AI settings loaded from environment variables.
 * Responsibility: Expose clean configurations for timeouts, endpoints, thresholds, and limits.
 */
const aiConfig = {
  // Model settings
  modelEndpoint: process.env.AI_MODEL_ENDPOINT || 'http://localhost:8000/predict',
  modelName: process.env.AI_MODEL_NAME || 'visiguard-cyber-resnet50',
  timeout: parseInt(process.env.AI_TIMEOUT || '10000', 10), // in ms
  retryAttempts: parseInt(process.env.AI_RETRY_ATTEMPTS || '3', 10),
  cacheEnabled: process.env.AI_CACHE_ENABLED === 'true',

  // Limits & Thresholds
  maxUploadSize: parseInt(process.env.AI_MAX_UPLOAD_SIZE || '10485760', 10), // Default: 10MB in bytes
  confidenceThreshold: parseFloat(process.env.AI_CONFIDENCE_THRESHOLD || '80.0'), // Min confidence %
  typingBotThreshold: parseFloat(process.env.AI_TYPING_BOT_THRESHOLD || '0.70'), // Risk index threshold

  // Threat & Bot Severity Thresholds
  typingSeverity: {
    medium: parseFloat(process.env.AI_TYPING_SEVERITY_MEDIUM || '0.30'),
    high: parseFloat(process.env.AI_TYPING_SEVERITY_HIGH || '0.60'),
    veryHigh: parseFloat(process.env.AI_TYPING_SEVERITY_VERY_HIGH || '0.85'),
  },

  // Logging & Environment
  loggingLevel: process.env.AI_LOGGING_LEVEL || 'info', // debug | info | warn | error
  isDev: process.env.NODE_ENV !== 'production'
};

module.exports = aiConfig;
