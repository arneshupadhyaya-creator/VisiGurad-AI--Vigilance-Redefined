const authService = require('../services/authService');
const { registerSchema, loginSchema } = require('../../../../shared/contracts/auth.contract');
const { ValidationError } = require('../utils/customErrors');

/**
 * AuthController
 * Purpose: Exposes HTTP routes for login and register endpoints.
 * Responsibility: Parse credentials, execute Zod validations, call auth services, and return JSON tokens.
 */
class AuthController {
  /**
   * Register User
   */
  async register(req, res, next) {
    try {
      // 1. Zod contract validation
      const validation = registerSchema.safeParse(req.body);
      if (!validation.success) {
        // Collect errors
        const messages = validation.error.issues.map(issue => issue.message);
        throw new ValidationError(`Validation failed: ${messages.join(', ')}`);
      }

      const { email, password } = validation.data;

      // 2. Call Service
      const result = await authService.register(email, password, req);

      // 3. Return Response
      res.status(201).json({
        status: 'success',
        message: 'Account registered successfully.',
        ...result
      });
    } catch (err) {
      next(err);
    }
  }

  /**
   * Login User
   */
  async login(req, res, next) {
    try {
      // 1. Zod contract validation
      const validation = loginSchema.safeParse(req.body);
      if (!validation.success) {
        const messages = validation.error.issues.map(issue => issue.message);
        throw new ValidationError(`Validation failed: ${messages.join(', ')}`);
      }

      const { email, password } = validation.data;

      // 2. Call Service
      const result = await authService.login(email, password, req);

      // 3. Return Response
      res.status(200).json({
        status: 'success',
        message: 'Logged in successfully.',
        ...result
      });
    } catch (err) {
      next(err);
    }
  }

  /**
   * Get Active Profile
   */
  async getProfile(req, res, next) {
    try {
      res.status(200).json({
        status: 'success',
        user: {
          id: req.user._id,
          email: req.user.email,
          role: req.user.role,
          createdAt: req.user.createdAt
        }
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AuthController();
