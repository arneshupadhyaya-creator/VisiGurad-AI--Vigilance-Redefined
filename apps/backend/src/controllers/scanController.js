const scanService = require('../services/scanService');
const { scanDeleteSchema } = require('../../../../shared/contracts/scan.contract');
const { ValidationError } = require('../utils/customErrors');

/**
 * ScanController
 * Purpose: Exposes HTTP routes for image analysis.
 * Responsibility: Parse Multer uploads, evaluate scan queries, invoke forensic pipeline services, and handle deletions.
 */
class ScanController {
  /**
   * Upload and Analyze Document
   */
  async createScan(req, res, next) {
    try {
      const file = req.file;
      const userId = req.user ? req.user._id : null;

      // Call Service to process upload and run ELA
      const result = await scanService.processScan(file, userId, req);

      res.status(201).json({
        status: 'success',
        message: 'Analysis completed successfully.',
        scan: result.scan,
        simulated: result.simulated,
        warning: result.warning
      });
    } catch (err) {
      next(err);
    }
  }

  /**
   * Fetch Scan History
   */
  async getScanHistory(req, res, next) {
    try {
      const userId = req.user ? req.user._id : null;
      const scans = await scanService.getUserScans(userId);
      res.status(200).json(scans);
    } catch (err) {
      next(err);
    }
  }

  /**
   * Delete Scan Record
   */
  async deleteScan(req, res, next) {
    try {
      // 1. Zod validation
      const validation = scanDeleteSchema.safeParse({ id: req.params.id });
      if (!validation.success) {
        throw new ValidationError('Invalid scan ID format.');
      }

      const scanId = req.params.id;
      const userId = req.user ? req.user._id : null;

      // 2. Call Service
      const result = await scanService.deleteScan(scanId, userId, req);

      // 3. Response
      res.status(200).json({
        status: 'success',
        ...result
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new ScanController();
