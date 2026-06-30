import React, { createContext, useState, useEffect } from 'react';
import { login as authLogin, register as authRegister, getMe } from '../services/authService';

export const AuthContext = createContext(null);

/**
 * AuthProvider
 * Purpose: Context provider for managing global user session.
 * Responsibility: Track token validation state, synchronize storage keys, and expose user states.
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Validate session on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const data = await getMe();
          if (data.status === 'success') {
            setUser(data.user);
            localStorage.setItem('user', JSON.stringify(data.user));
          } else {
            logout();
          }
        } catch (err) {
          console.error('Session initialization failure:', err);
          logout();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const data = await authLogin(email, password);
      if (data.status === 'success') {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        return true;
      }
      return false;
    } catch (err) {
      const message = err.response?.data?.error || 'Authentication failed. Please check your credentials.';
      setAuthError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const data = await authRegister(email, password);
      if (data.status === 'success') {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        return true;
      }
      return false;
    } catch (err) {
      const message = err.response?.data?.error || 'Registration failed. Please make sure parameters are correct.';
      setAuthError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setAuthError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authError,
        login,
        register,
        logout,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
