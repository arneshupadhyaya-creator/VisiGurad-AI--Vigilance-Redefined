const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const userRepository = require('../repositories/userRepository');
const { ValidationError, AuthenticationError } = require('../utils/customErrors');
const auditService = require('../audit/auditService');

/**
 * AuthService
 * Purpose: Implements authentication business logic.
 * Responsibility: Hash user passwords, verify login credentials, sign JWTs, and audit auth events.
 */
class AuthService {
  /**
   * Signs a standard JWT.
   */
  generateToken(userId) {
    return jwt.sign(
      { id: userId },
      process.env.JWT_SECRET || 'DUMMY_REPLACE_WITH_REAL_SECRET',
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );
  }

  /**
   * Registers a new user.
   */
  async register(email, password, req = null) {
    // Check if user already exists
    const existingUser = await userRepository.findByEmail(email);
    if (existingUser) {
      await auditService.log('USER_LOGIN_FAILED', `Attempted registration for existing email: ${email}`, null, req);
      throw new ValidationError('Email address is already in use.');
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Save user
    const user = await userRepository.create({
      email,
      password: hashedPassword
    });

    await auditService.log('USER_REGISTERED', `Successfully registered account: ${email}`, user._id, req);

    const token = this.generateToken(user._id);
    return { token, user: { id: user._id, email: user.email, role: user.role, createdAt: user.createdAt } };
  }

  /**
   * Log in user
   */
  async login(email, password, req = null) {
    const user = await userRepository.findByEmail(email);
    if (!user) {
      await auditService.log('USER_LOGIN_FAILED', `Login attempt failed: Email not found (${email})`, null, req);
      throw new AuthenticationError('Invalid email or password.');
    }

    // Verify password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      await auditService.log('USER_LOGIN_FAILED', `Login attempt failed: Password mismatch for ${email}`, user._id, req);
      throw new AuthenticationError('Invalid email or password.');
    }

    await auditService.log('USER_LOGIN_SUCCESS', `User logged in: ${email}`, user._id, req);

    const token = this.generateToken(user._id);
    return { token, user: { id: user._id, email: user.email, role: user.role, createdAt: user.createdAt } };
  }
}

module.exports = new AuthService();
