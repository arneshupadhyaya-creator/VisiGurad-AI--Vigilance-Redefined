# AI Module Testing Guide

This guide describes how to run automated unit and integration tests covering the new local AI integration module.

---

## 1. Backend tests
Backend tests utilize Jest and Supertest.

### Running Backend tests
Navigate to the repository root directory or the backend folder and execute:
```bash
cd apps/backend
npm test
```

### Test Scope
* **Mime Filtering**: Verifies invalid formats (like `.exe`, `.sh`) are blocked before processing.
* **Typing Schema Validations**: Verifies Zod validation rules block malformed telemetry objects.
* **Fallback Simulator**: Verifies calculations are computed deterministically when offline.

---

## 2. Frontend tests
Frontend tests utilize Vitest.

### Running Frontend tests
```bash
cd apps/frontend
npm run test
```

### Test Scope
* **useTypingCapture calculations**: Checks hold time and flight time math formulas.
* **bot locks**: Assures that auto-filled inputs successfully trigger VERY_HIGH risk lockout shields.
