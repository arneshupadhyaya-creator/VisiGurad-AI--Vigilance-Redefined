const aiConfig = require('../config/ai.config');

/**
 * AI Structured Logger
 * Purpose: Logs structured events for AI document checks and keystroke dynamics telemetry.
 * Responsibility: Format events into JSON strings while filtering out user-sensitive fields.
 */
const aiLogger = {
  logEvent(level, eventType, message, details = {}) {
    // Determine if we should suppress debug logs
    if (aiConfig.loggingLevel === 'info' && level === 'debug') return;
    if (aiConfig.loggingLevel === 'warn' && (level === 'info' || level === 'debug')) return;
    if (aiConfig.loggingLevel === 'error' && level !== 'error') return;

    // Filter out user-sensitive inputs/keys if any slip in
    const safeDetails = { ...details };
    const sensitiveKeys = ['password', 'secret', 'token', 'keystrokes', 'text', 'raw_keys'];
    sensitiveKeys.forEach(key => {
      if (key in safeDetails) {
        safeDetails[key] = '[REDACTED_SENSITIVE_DATA]';
      }
    });

    const logEntry = {
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      eventType,
      message,
      metadata: safeDetails
    };

    console.log(JSON.stringify(logEntry));
  },

  info(eventType, message, details) {
    this.logEvent('info', eventType, message, details);
  },

  debug(eventType, message, details) {
    this.logEvent('debug', eventType, message, details);
  },

  warn(eventType, message, details) {
    this.logEvent('warn', eventType, message, details);
  },

  error(eventType, message, details) {
    this.logEvent('error', eventType, message, details);
  }
};

module.exports = aiLogger;
