import api from '../../services/api';

/**
 * Frontend AI Client Layer
 * Purpose: Connects frontend UI triggers to backend AI endpoints.
 * Responsibility: Execute API requests for document verification, health status, and typing telemetry.
 */

export const verifyDocument = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/ai/verify-document', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    }
  });

  return response.data;
};

export const analyzeTyping = async (metrics) => {
  const response = await api.post('/ai/analyze-typing', metrics);
  return response.data;
};

export const getAIStatus = async () => {
  const response = await api.get('/ai/status');
  return response.data;
};
