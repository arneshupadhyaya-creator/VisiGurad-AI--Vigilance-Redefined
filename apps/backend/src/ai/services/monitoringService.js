const aiConfig = require('../config/ai.config');
const os = require('os');

/**
 * AI Health and Monitoring Service
 * Purpose: Tracks request latencies, load indicators, memory diagnostics, and model availability states.
 * Responsibility: Compile health payloads for status endpoints.
 */
class MonitoringService {
  constructor() {
    this.totalRequests = 0;
    this.totalDuration = 0;
    this.queueSize = 0;
    this.loadedModel = aiConfig.modelName;
    this.version = '1.2.0-cybersecurity-core';
    this.isModelLoaded = true;
  }

  recordRequest(durationMs) {
    this.totalRequests += 1;
    this.totalDuration += durationMs;
  }

  incrementQueue() {
    this.queueSize += 1;
  }

  decrementQueue() {
    if (this.queueSize > 0) {
      this.queueSize -= 1;
    }
  }

  getAverageResponseTime() {
    if (this.totalRequests === 0) return 0;
    return parseFloat((this.totalDuration / this.totalRequests).toFixed(2));
  }

  getHealthMetrics() {
    // Collect system stats
    const totalMemBytes = os.totalmem();
    const freeMemBytes = os.freemem();
    const usedMemBytes = totalMemBytes - freeMemBytes;
    
    // Format memory in MB
    const totalMemMB = Math.round(totalMemBytes / (1024 * 1024));
    const usedMemMB = Math.round(usedMemBytes / (1024 * 1024));

    return {
      aiAvailable: this.isModelLoaded,
      modelLoaded: this.loadedModel,
      memoryUsage: {
        usedMB: usedMemMB,
        totalMB: totalMemMB,
        percentage: parseFloat(((usedMemBytes / totalMemBytes) * 100).toFixed(1))
      },
      averageResponseTime: this.getAverageResponseTime(),
      queueSize: this.queueSize,
      totalProcessed: this.totalRequests,
      version: this.version
    };
  }
}

module.exports = new MonitoringService();
