const request = require('supertest');
const aiInferenceService = require('../../apps/backend/src/ai/services/aiInferenceService');
const { typingAnalysisRequestSchema } = require('../../shared/contracts/ai.contract');

/**
 * Backend AI Security Tests
 * Purpose: Validate AI routes, contract matching, validation filters, and offline simulators.
 */
describe('AI Cybersecurity Integration Endpoints', () => {
  let mockAppUrl;

  beforeAll(() => {
    mockAppUrl = 'http://localhost:5000/api/ai';
  });

  it('should validate typing metrics using Zod schema constraints', () => {
    const invalidMetrics = {
      wpm: -10, // Invalid: must be non-negative
      variance: 20,
      pasteDetected: 'maybe' // Invalid: must be boolean
    };

    const result = typingAnalysisRequestSchema.safeParse(invalidMetrics);
    expect(result.success).toBe(false);
    console.log('[Test Pass] Successfully blocked invalid typing metrics structure.');
  });

  it('should pass validation for correctly formatted typing behavior metrics', () => {
    const validMetrics = {
      holdTime: 120,
      flightTime: 50,
      digraphLatency: 170,
      trigraphLatency: 290,
      typingSpeed: 300,
      wpm: 60,
      burstSpeed: 350,
      variance: 15,
      consistency: 80,
      backspaceFrequency: 2,
      idleTime: 0,
      errorRate: 0.05,
      pasteDetected: false,
      autoFillDetected: false
    };

    const result = typingAnalysisRequestSchema.safeParse(validMetrics);
    expect(result.success).toBe(true);
    console.log('[Test Pass] Successfully validated correct keystroke dynamics telemetry.');
  });

  it('should fall back to simulated inference when local AI endpoint is unreachable', async () => {
    // Invoke model with offline parameters to trigger fallback simulator
    const payload = { originalName: 'tampered-invoice.pdf', sizeBytes: 5000 };
    const result = await aiInferenceService.invokeModel('document', payload);

    expect(result.authenticity).toBe(false); // Since name contains 'tampered'
    expect(result.tampering_detected).toBe(true);
    expect(result.risk_score).toBeGreaterThan(0.7);
    console.log('[Test Pass] Fallback simulator computed correct, deterministic tamper threat levels.');
  });
});
