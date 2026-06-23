const mongoose = require('mongoose');

/**
 * AuditLog Schema for MongoDB
 * Purpose: Model structure for database security event auditing.
 * Responsibility: Track user logins, failures, uploads, and data changes for compliance.
 */
const auditLogSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: false // May be null for anonymous or authentication failure logs
  },
  action: {
    type: String,
    required: true,
    enum: [
      'USER_LOGIN_SUCCESS',
      'USER_LOGIN_FAILED',
      'USER_REGISTERED',
      'USER_LOGOUT',
      'FILE_UPLOADED',
      'SCAN_CREATED',
      'SCAN_DELETED',
      'SECURITY_ALERT'
    ]
  },
  details: {
    type: String,
    required: true
  },
  ipAddress: {
    type: String,
    default: 'Unknown'
  },
  userAgent: {
    type: String,
    default: 'Unknown'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('AuditLog', auditLogSchema);
