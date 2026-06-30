import api from './api';

/**
 * AuthService
 * Purpose: Frontend network interface for credentials management.
 * Responsibility: Execute Axios posts for register/login and extract JWT session envelopes.
 */

export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const register = async (email, password) => {
  const response = await api.post('/auth/register', { email, password });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};
