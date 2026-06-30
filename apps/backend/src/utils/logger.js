/**
 * Application Logger Interface
 * Purpose: Centrally formats server output messages and handles levels.
 * Responsibility: Format console prints and hook into third party log aggregators.
 */
const logger = {
  info: (message, ...args) => {
    console.log(`[INFO] ${new Date().toISOString()} - ${message}`, ...args);
  },
  warn: (message, ...args) => {
    console.warn(`[WARN] ${new Date().toISOString()} - ${message}`, ...args);
  },
  error: (message, errorStack) => {
    console.error(`[ERROR] ${new Date().toISOString()} - ${message}`);
    if (errorStack) console.error(errorStack);
  },
  debug: (message, ...args) => {
    if (process.env.NODE_ENV !== 'production') {
      console.log(`[DEBUG] ${new Date().toISOString()} - ${message}`, ...args);
    }
  }
};

module.exports = logger;
