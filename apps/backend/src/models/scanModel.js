const mongoose = require('mongoose');

/**
 * Scan Schema for MongoDB
 * Purpose: Model structure for image forensics audits.
 * Responsibility: Track compression delta files, original assets, dimensions, and computed threat levels.
 */
const scanSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: false // Optional to allow anonymous uploads or offline backup modes
  },
  originalName: {
    type: String,
    required: true,
    trim: true
  },
  originalPath: {
    type: String,
    required: true
  },
  elaPath: {
    type: String,
    required: true
  },
  fileSize: {
    type: Number, // in bytes
    required: true
  },
  dimensions: {
    type: String, // e.g., "1920x1080"
    default: "Unknown"
  },
  threatScore: {
    type: Number, // Value from 0.0 to 100.0
    required: true,
    min: 0,
    max: 100
  },
  status: {
    type: String, // "Clean", "Suspicious", "Tampered"
    required: true,
    enum: ['Clean', 'Suspicious', 'Tampered']
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Scan', scanSchema);
