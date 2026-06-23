const logger = require('../utils/logger');

/**
 * Centralized Error Middleware
 * Purpose: Catches all unhandled exceptions and formats uniform REST API error payloads.
 * Responsibility: Translate custom AppErrors and MongoDB exceptions to correct HTTP statuses.
 */
const errorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  logger.error(`Error encountered: ${err.message}`, err.stack);

  // Mongoose Validation Error
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      status: 'fail',
      error: 'Validation failed',
      details: Object.values(err.errors).map(el => el.message)
    });
  }

  // Mongoose Duplicate Key Error (e.g. email already exists)
  if (err.code === 11000) {
    return res.status(400).json({
      status: 'fail',
      error: 'Duplicate record error',
      details: ['Email account is already registered. Please login instead.']
    });
  }

  // JWT Errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      status: 'fail',
      error: 'Invalid token structure. Authentication failed.'
    });
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      status: 'fail',
      error: 'Session token has expired. Please log in again.'
    });
  }

  // Operational Errors (Errors we explicitly throw)
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      status: err.status,
      error: err.message
    });
  }

  // Programming/Third Party Errors: Don't leak details in production
  const message = process.env.NODE_ENV === 'production' 
    ? 'Internal server execution error.' 
    : err.message;

  return res.status(500).json({
    status: 'error',
    error: message,
    stack: process.env.NODE_ENV === 'production' ? undefined : err.stack
  });
};

module.exports = errorHandler;
