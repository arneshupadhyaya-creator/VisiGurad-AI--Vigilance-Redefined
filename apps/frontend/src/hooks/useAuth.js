import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

/**
 * useAuth hook
 * Purpose: Custom hook to retrieve user auth state.
 * Responsibility: Throw explicit error if consumed outside AuthProvider scopes.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be consumed within an AuthProvider wrapper.');
  }
  return context;
};
