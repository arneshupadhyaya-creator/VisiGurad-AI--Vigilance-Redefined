/**
 * Centralized Custom Error Classes
 * Purpose: Provides structured error shapes with specific HTTP status codes.
 * Responsibility: Allow services to throw descriptive, category-specific exceptions.
 */

class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true; // Indicates user-facing operational errors vs coding bugs
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message || 'Validation failed', 400);
  }
}

class AuthenticationError extends AppError {
  constructor(message) {
    super(message || 'Unauthorized access request', 401);
  }
}

class ForbiddenError extends AppError {
  constructor(message) {
    super(message || 'Access forbidden', 403);
  }
}

class NotFoundError extends AppError {
  constructor(message) {
    super(message || 'Requested resource not found', 404);
  }
}

class RateLimitError extends AppError {
  constructor(message) {
    super(message || 'Too many requests, please slow down', 429);
  }
}

module.exports = {
  AppError,
  ValidationError,
  AuthenticationError,
  ForbiddenError,
  NotFoundError,
  RateLimitError
};
