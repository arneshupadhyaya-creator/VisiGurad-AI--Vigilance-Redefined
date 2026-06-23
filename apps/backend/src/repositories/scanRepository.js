const Scan = require('../models/scanModel');

/**
 * ScanRepository
 * Purpose: Decouples direct MongoDB operations for Scans from business services.
 * Responsibility: Execute Mongoose queries to save scans, load history, or delete records.
 */
class ScanRepository {
  async create(scanData) {
    const scan = new Scan(scanData);
    return await scan.save();
  }

  async findByUserId(userId) {
    // If a userId is provided, filter by it. Otherwise return all (or empty if offline).
    if (userId) {
      return await Scan.find({ userId }).sort({ createdAt: -1 });
    }
    return await Scan.find().sort({ createdAt: -1 });
  }

  async findById(id) {
    return await Scan.findById(id);
  }

  async deleteById(id) {
    return await Scan.findByIdAndDelete(id);
  }
}

module.exports = new ScanRepository();
