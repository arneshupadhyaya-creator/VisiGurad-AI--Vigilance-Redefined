const logger = require('../utils/logger');
const auditService = require('../audit/auditService');

/**
 * User Activity Monitoring Service
 * Purpose: Track application access patterns and collect statistical footprints.
 * Responsibility: Register requests, log user activity events, and provide a monitoring interface.
 */
class MonitorService {
  constructor() {
    this.monitoringEnabled = true;
  }

  /**
   * Tracks user interaction events.
   */
  async trackActivity(userId, actionType, description, req = null) {
    if (!this.monitoringEnabled) {
      logger.info(`Monitoring disabled. Skipping activity tracking for User: ${userId}`);
      return;
    }

    logger.debug(`Tracking Activity: User: ${userId}, Action: ${actionType}, Desc: ${description}`);
    
    // Log as a security audit log
    await auditService.log(actionType, description, userId, req);
  }

  /**
   * Disable activity monitoring
   */
  disableMonitoring() {
    this.monitoringEnabled = false;
    logger.info('User activity monitoring has been disabled.');
  }

  /**
   * Enable activity monitoring
   */
  enableMonitoring() {
    this.monitoringEnabled = true;
    logger.info('User activity monitoring has been enabled.');
  }
}

module.exports = new MonitorService();
