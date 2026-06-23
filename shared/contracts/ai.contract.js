const { z } = require('zod');

/**
 * AI Integration Contract
 * Purpose: Defines expected request/response objects and event structures for the AI pipeline.
 * Responsibility: Formalize communication parameters for the future pluggable local AI model.
 */

// Contract structure expected for calling the AI model service
const aiAnalysisRequestSchema = z.object({
  imagePath: z.string().min(1, 'Target image path is required for execution'),
  outputPath: z.string().min(1, 'Output visual path is required'),
  options: z.object({
    quality: z.number().int().min(1).max(100).default(90),
    channels: z.enum(['RGB', 'RGBA', 'L']).default('RGB')
  }).optional()
});

// Response payload returned by the AI service layer
const aiAnalysisResponseSchema = z.object({
  success: z.boolean(),
  threatScore: z.number().min(0).max(100),
  status: z.enum(['Clean', 'Suspicious', 'Tampered']),
  anomaliesCount: z.number().int().nonnegative().optional(),
  modelName: z.string().optional(),
  simulated: z.boolean().optional(),
  completedAt: z.string()
});

// Event payload structures for WebSockets (progress streaming)
const aiProgressEventSchema = z.object({
  scanId: z.string(),
  stage: z.enum([
    'METADATA_EXTRACTION',
    'COMPRESSION_DELTA_GENERATION',
    'DIVERGENT_REGION_CLUSTERING',
    'THREAT_INDEX_CALCULATION',
    'HEATMAP_OVERLAY_RENDER'
  ]),
  progressPercent: z.number().min(0).max(100),
  timestamp: z.string()
});

module.exports = {
  aiAnalysisRequestSchema,
  aiAnalysisResponseSchema,
  aiProgressEventSchema
};
