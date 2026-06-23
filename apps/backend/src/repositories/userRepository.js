const User = require('../models/userModel');

/**
 * UserRepository
 * Purpose: Decouples direct MongoDB operations for User model from business services.
 * Responsibility: Execute Mongo transactions for finding, updating, and saving user accounts.
 */
class UserRepository {
  async findByEmail(email) {
    return await User.findOne({ email });
  }

  async findById(id) {
    return await User.findById(id).select('-password');
  }

  async create(userData) {
    const user = new User(userData);
    return await user.save();
  }
}

module.exports = new UserRepository();
