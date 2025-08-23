import React, { createContext, useContext, useState, useEffect } from 'react';
import { ApiService } from './api/ApiService';
import './styles/auth.css';

// =============================================================================
// AUTH CONTEXT & HOOKS
// =============================================================================
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// =============================================================================
// AUTH PROVIDER COMPONENT
// =============================================================================
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const userData = await ApiService.getCurrentUser(token);
      if (userData) {
        setUser(userData);
      } else {
        // Token is invalid, remove it
        logout();
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (loginData) => {
    const result = await ApiService.login(loginData);
    
    if (result.success) {
      const tokenData = result.data;
      setToken(tokenData.access_token);
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      return { success: true };
    }
    
    return result;
  };

  const signup = async (formData) => {
    const result = await ApiService.signup(formData);
    
    if (result.success) {
      const tokenData = result.data;
      setToken(tokenData.access_token);
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      return { success: true };
    }
    
    return result;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    apiService: ApiService,
    token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};