const { z } = require('zod');

/**
 * Scan Contract
 * Purpose: Defines validation constraints and response schemas for image analysis scans.
 * Responsibility: Ensure uploaded metadata and scan deletions match security definitions.
 */

// Scan deletion validator
const scanDeleteSchema = z.object({
  id: z.string().regex(/^[0-9a-fA-F]{24}$/, 'Invalid MongoDB ObjectId')
});

// Scan response contract shape
const scanResponseSchema = z.object({
  message: z.string(),
  scan: z.object({
    id: z.string(),
    originalName: z.string(),
    originalPath: z.string(),
    elaPath: z.string(),
    fileSize: z.number(),
    dimensions: z.string(),
    threatScore: z.number(),
    status: z.enum(['Clean', 'Suspicious', 'Tampered']),
    createdAt: z.string()
  })
});

module.exports = {
  scanDeleteSchema,
  scanResponseSchema
};
