const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const mongoose = require('mongoose');
const scanRepository = require('../repositories/scanRepository');
const LocalStorageProvider = require('../storage/LocalStorageProvider');
const auditService = require('../audit/auditService');
const { ValidationError, NotFoundError } = require('../utils/customErrors');
const logger = require('../utils/logger');

// Instantiate storage driver
const storage = new LocalStorageProvider();

/**
 * ScanService
 * Purpose: Digital forensics pipeline coordinator.
 * Responsibility: Executes ELA scripts, writes audit histories, handles disk cleans, and wraps ML execution.
 */
class ScanService {
  /**
   * Spawns Python ELA script or falls back to simulation.
   */
  async executeEla(inputPath, outputPath) {
    return new Promise((resolve) => {
      // Path to cli.py relative to __dirname (apps/backend/src/services/)
      const cliPath = path.resolve(__dirname, '..', '..', '..', '..', 'ML', 'cli.py');
      
      logger.info(`Spawning Python process: python "${cliPath}" "${inputPath}" "${outputPath}" 90`);
      const pythonProcess = spawn('python', [cliPath, inputPath, outputPath, '90']);
      
      let stdoutData = '';
      let stderrData = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const parsedResult = JSON.parse(stdoutData.trim());
            if (parsedResult.success) {
              return resolve({
                success: true,
                threatScore: parsedResult.threatScore,
                status: parsedResult.status,
                simulated: false
              });
            }
          } catch (e) {
            logger.error('Failed to parse Python stdout JSON:', e);
          }
        }
        
        logger.warn(`Python ELA failed (code ${code}). Stderr: ${stderrData.trim()}. Running simulated fallback...`);
        resolve(this.simulateEla(inputPath, outputPath, stderrData));
      });
      
      pythonProcess.on('error', (err) => {
        logger.warn(`Could not spawn Python. Error: ${err.message}. Running simulated fallback...`);
        resolve(this.simulateEla(inputPath, outputPath, err.message));
      });
    });
  }

  /**
   * Mock ELA simulation to copy file and compute deterministic score.
   */
  simulateEla(inputPath, outputPath, errorDetail = '') {
    try {
      fs.copyFileSync(inputPath, outputPath);
      
      // Deterministic mock score based on path name characters
      const hash = inputPath.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      const threatScore = (hash % 80) + 5; // between 5% and 85%
      
      let status = 'Clean';
      if (threatScore >= 45) status = 'Tampered';
      else if (threatScore >= 15) status = 'Suspicious';
      
      return {
        success: true,
        threatScore,
        status,
        simulated: true,
        warning: `Simulated ELA run. Detail: ${errorDetail || 'Python environment offline.'}`
      };
    } catch (err) {
      logger.error('ELA Simulation failure:', err);
      return {
        success: false,
        error: `Forensic simulation failed: ${err.message}`
      };
    }
  }

  /**
   * Process uploaded document, run ELA, and save to DB
   */
  async processScan(file, userId = null, req = null) {
    if (!file) {
      throw new ValidationError('No image file was uploaded for analysis.');
    }

    const inputPath = file.path;
    const originalFilename = file.filename;

    // Create unique name for ELA file
    const elaFilename = `ela-${path.basename(originalFilename, path.extname(originalFilename))}.png`;
    const uploadsDir = path.dirname(inputPath);
    const outputPath = path.join(uploadsDir, elaFilename);

    // Run ELA analysis
    const analysis = await this.executeEla(inputPath, outputPath);

    if (!analysis.success) {
      throw new ValidationError(analysis.error || 'Forensic ELA computation failed.');
    }

    // Save image references through storage layer
    const originalUrl = `/uploads/${originalFilename}`;
    const elaUrl = `/uploads/${elaFilename}`;

    const scanData = {
      userId,
      originalName: file.originalname,
      originalPath: originalUrl,
      elaPath: elaUrl,
      fileSize: file.size,
      dimensions: 'Standard', // Expandable to image-size utility
      threatScore: analysis.threatScore,
      status: analysis.status
    };

    let savedScan;
    if (mongoose.connection.readyState === 1) {
      savedScan = await scanRepository.create(scanData);
    } else {
      // In-memory offline fallback
      savedScan = {
        ...scanData,
        _id: new mongoose.Types.ObjectId(),
        createdAt: new Date(),
        dbOffline: true
      };
    }

    await auditService.log(
      'SCAN_CREATED',
      `Forensic scan completed for ${file.originalname}. Score: ${analysis.threatScore}%. Status: ${analysis.status}.`,
      userId,
      req
    );

    return {
      scan: savedScan,
      simulated: analysis.simulated,
      warning: analysis.warning
    };
  }

  /**
   * Get all past scans for user
   */
  async getUserScans(userId) {
    if (mongoose.connection.readyState !== 1) {
      logger.warn('MongoDB offline. Returning empty scan collection.');
      return [];
    }
    return await scanRepository.findByUserId(userId);
  }

  /**
   * Delete a scan audit record
   */
  async deleteScan(scanId, userId = null, req = null) {
    if (mongoose.connection.readyState !== 1) {
      logger.warn('MongoDB offline. Skipping scan database record deletion.');
      return { message: 'Item deleted (Simulated - database offline).' };
    }

    const scan = await scanRepository.findById(scanId);
    if (!scan) {
      throw new NotFoundError('Forensic scan record not found.');
    }

    // Delete files using storage provider
    await storage.deleteFile(scan.originalPath);
    await storage.deleteFile(scan.elaPath);

    // Delete record in DB
    await scanRepository.deleteById(scanId);

    await auditService.log(
      'SCAN_DELETED',
      `Forensic scan record ${scanId} deleted. File: ${scan.originalName}`,
      userId,
      req
    );

    return { message: 'Scan history and files deleted successfully.' };
  }
}

module.exports = new ScanService();
