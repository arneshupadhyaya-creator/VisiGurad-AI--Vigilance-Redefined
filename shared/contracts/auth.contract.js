const { z } = require('zod');

/**
 * Authentication Contract
 * Purpose: Defines validation schemas, request/response models, and contract rules for Auth API.
 * Responsibility: Enforce request validation and document JSON responses.
 * Inputs/Outputs: Standard JSON bodies.
 */

// Registration Schema
const registerSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .max(100, 'Email must be under 100 characters')
    .trim()
    .toLowerCase(),
  password: z.string()
    .min(8, 'Password must be at least 8 characters long')
    .max(50, 'Password must be under 50 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
});

// Login Schema
const loginSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email format')
    .trim()
    .toLowerCase(),
  password: z.string()
    .min(1, 'Password is required')
});

// API Response Shapes (For technical reference/documentation)
const authResponseSchema = z.object({
  token: z.string(),
  user: z.object({
    id: z.string(),
    email: z.string(),
    role: z.string(),
    createdAt: z.string()
  })
});

module.exports = {
  registerSchema,
  loginSchema,
  authResponseSchema
};
