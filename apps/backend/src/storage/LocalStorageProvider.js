const StorageProvider = require('./StorageProvider');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

/**
 * LocalStorageProvider
 * Purpose: Local filesystem storage driver.
 * Responsibility: Manage file creation and removal in the local uploads directory.
 */
class LocalStorageProvider extends StorageProvider {
  constructor(uploadsDir) {
    super();
    this.uploadsDir = uploadsDir || path.join(__dirname, '..', '..', 'uploads');
    // Ensure folder exists
    if (!fs.existsSync(this.uploadsDir)) {
      fs.mkdirSync(this.uploadsDir, { recursive: true });
    }
  }

  async saveFile(file) {
    // Multer handles direct file saving to disk by default, so we just get filename
    const filename = file.filename;
    logger.info(`LocalStorageProvider saved file: ${filename}`);
    return `/uploads/${filename}`;
  }

  async deleteFile(fileUrl) {
    try {
      // Convert web URL '/uploads/file.png' to local path
      const baseFilename = path.basename(fileUrl);
      const localPath = path.join(this.uploadsDir, baseFilename);
      
      if (fs.existsSync(localPath)) {
        fs.unlinkSync(localPath);
        logger.info(`LocalStorageProvider deleted file: ${localPath}`);
        return true;
      }
      logger.warn(`File not found for deletion on local filesystem: ${localPath}`);
      return false;
    } catch (err) {
      logger.error(`LocalStorageProvider delete error: ${err.message}`);
      return false;
    }
  }
}

module.exports = LocalStorageProvider;
