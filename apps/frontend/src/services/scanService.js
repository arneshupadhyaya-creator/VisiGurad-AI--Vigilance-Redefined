import api from './api';

/**
 * ScanService
 * Purpose: Frontend network interface for document forensic operations.
 * Responsibility: Execute multipart uploads for scans, retrieve lists, and delete records.
 */

export const uploadAndAnalyze = async (file) => {
  const formData = new FormData();
  formData.append('image', file);
  
  const response = await api.post('/scan', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};

export const fetchScanHistory = async () => {
  const response = await api.get('/scans');
  return response.data;
};

export const deleteScanRecord = async (id) => {
  const response = await api.delete(`/scans/${id}`);
  return response.data;
};
