const jwt = require('jsonwebtoken');
const userRepository = require('../repositories/userRepository');
const { AuthenticationError } = require('../utils/customErrors');
const logger = require('../utils/logger');

/**
 * Authorization Middleware
 * Purpose: Evaluates HTTP headers for valid Bearer JWT.
 * Responsibility: Parse token, verify signature, fetch active user from repository, and append user object to request.
 */
const protect = async (req, res, next) => {
  let token;

  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      // Get token from header
      token = req.headers.authorization.split(' ')[1];

      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'DUMMY_REPLACE_WITH_REAL_SECRET');

      // Get user from database
      req.user = await userRepository.findById(decoded.id);
      
      if (!req.user) {
        throw new AuthenticationError('User associated with this token no longer exists.');
      }

      return next();
    } catch (err) {
      logger.warn(`JWT verification failure: ${err.message}`);
      return next(new AuthenticationError('Not authorized, token verification failed.'));
    }
  }

  if (!token) {
    return next(new AuthenticationError('Not authorized, security token is missing.'));
  }
};

module.exports = { protect };
