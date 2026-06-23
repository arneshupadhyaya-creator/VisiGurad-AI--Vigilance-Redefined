const rateLimit = require('express-rate-limit');
const { RateLimitError } = require('../utils/customErrors');

/**
 * Rate Limiter Middlwares
 * Purpose: Protect API surface from denial-of-service (DoS) and authentication brute-force attacks.
 * Responsibility: Track IP addresses and block requests exceeding threshold rates.
 */

// Auth Limiter: Tight restriction for logins/registrations
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per window
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  handler: (req, res, next) => {
    next(new RateLimitError('Too many login/registration attempts. Please try again after 15 minutes.'));
  }
});

// Scan Limiter: Restricts file uploads and computations
const scanLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20, // Limit each IP to 20 scans per window
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res, next) => {
    next(new RateLimitError('Forensic scan limit reached. Max 20 uploads per 15 minutes allowed.'));
  }
});

module.exports = {
  authLimiter,
  scanLimiter
};
