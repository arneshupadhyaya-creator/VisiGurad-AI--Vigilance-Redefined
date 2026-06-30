const AuditLog = require('../models/auditModel');
const logger = require('../utils/logger');
const mongoose = require('mongoose');

/**
 * AuditService
 * Purpose: Centrally registers security audit logs.
 * Responsibility: Save audit payloads to MongoDB or fallback to system logger if database is offline.
 */
class AuditService {
  async log(action, details, userId = null, req = null) {
    let ipAddress = 'Unknown';
    let userAgent = 'Unknown';
    
    if (req) {
      ipAddress = req.ip || req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'Unknown';
      userAgent = req.headers['user-agent'] || 'Unknown';
    }

    const logPayload = {
      userId,
      action,
      details,
      ipAddress,
      userAgent,
      createdAt: new Date()
    };

    logger.info(`AUDIT EVENT [${action}]: ${details} (User: ${userId || 'Anonymous'}, IP: ${ipAddress})`);

    try {
      if (mongoose.connection.readyState === 1) {
        const auditRecord = new AuditLog(logPayload);
        await auditRecord.save();
      } else {
        logger.warn('AuditLog was not persisted to database: Database is offline.');
      }
    } catch (err) {
      logger.error('Failed to save audit log record to MongoDB', err.stack);
    }
  }
}

module.exports = new AuditService();
