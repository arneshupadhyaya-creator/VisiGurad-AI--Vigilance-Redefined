const mongoose = require('mongoose');

/**
 * Database Config
 * Purpose: Manages MongoDB connection life cycle.
 * Responsibility: Securely establish connections and handle reconnection failures.
 * Dependencies: mongoose, dotenv (process.env.MONGO_URI)
 */
const connectDB = async () => {
  const mongoUri = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/visiguard';
  
  try {
    console.log(`Connecting to MongoDB...`);
    const conn = await mongoose.connect(mongoUri, {
      serverSelectionTimeoutMS: 5000 // Time out after 5 seconds instead of hanging
    });
    console.log(`MongoDB Connected successfully to host: ${conn.connection.host}`);
    return conn;
  } catch (err) {
    console.error(`MongoDB Connection failure: ${err.message}`);
    console.warn(`System starting with online MongoDB fallback enabled.`);
    return null;
  }
};

module.exports = connectDB;
