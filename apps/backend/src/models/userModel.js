const mongoose = require('mongoose');

/**
 * User Schema for MongoDB
 * Purpose: Model structure for user records.
 * Responsibility: Securely index user email accounts and save bcrypt password hashes.
 */
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please fill a valid email address']
  },
  password: {
    type: String,
    required: [true, 'Password hash is required'],
    minlength: 8
  },
  role: {
    type: String,
    enum: ['User', 'Admin', 'Security_Auditor'],
    default: 'Security_Auditor' // Matches default forensic workspace profile
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', userSchema);
