require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const connectDB = require('./src/config/db');
const authRoutes = require('./src/routes/authRoutes');
const scanRoutes = require('./src/routes/scanRoutes');
const aiRoutes = require('./src/ai/routes/aiRoutes');
const errorHandler = require('./src/middlewares/errorMiddleware');
const metricsService = require('./src/monitoring/metricsService');
const logger = require('./src/utils/logger');

const app = express();

// Middlewares
app.use(cors());
app.use(express.json());

// Latency & Metrics tracking middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    metricsService.recordLatency(req.originalUrl || req.url, duration);
  });
  next();
});

// Configure Static File Serving for uploads
const uploadsDir = path.resolve(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}
app.use('/uploads', express.static(uploadsDir));

// Connect to MongoDB
connectDB();

// API Routes mounting
app.use('/api/auth', authRoutes);
app.use('/api', scanRoutes);
app.use('/api/ai', aiRoutes);

// Catch-all route not found (404)
app.use((req, res, next) => {
  res.status(404).json({
    status: 'fail',
    error: `Can't find ${req.originalUrl} on this server.`
  });
});

// Centralized Global Error Handler Middleware
app.use(errorHandler);

// Set Port from environment
const port = process.env.PORT || 5000;

// Start Server
app.listen(port, () => {
  logger.info(`VisiGuard AI production-grade backend listening on: http://localhost:${port}`);
});