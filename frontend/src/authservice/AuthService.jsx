import React, { createContext, useContext, useState, useEffect } from 'react';
import './AuthService.css';

// =============================================================================
// API SERVICE
// =============================================================================
const API_BASE = 'http://127.0.0.1:8000';

export const ApiService = {
  async login(loginData) {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      if (response.ok) {
        const tokenData = await response.json();
        return { success: true, data: tokenData };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error occurred' };
    }
  },

  async signup(formData) {
    try {
      const response = await fetch(`${API_BASE}/auth/signup`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const tokenData = await response.json();
        return { success: true, data: tokenData };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error occurred' };
    }
  },

  async getCurrentUser(token) {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        return null;
      }
    } catch (error) {
      return null;
    }
  },

  async fetchPersons(token) {
    try {
      const response = await fetch(`${API_BASE}/persons`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error('Failed to fetch persons');
      }
    } catch (error) {
      throw error;
    }
  },

  async fetchPerson(token, id) {
    try {
      const response = await fetch(`${API_BASE}/persons/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error('Failed to fetch person');
      }
    } catch (error) {
      throw error;
    }
  },

  // Generic HTTP methods for API calls
  async get(endpoint, token) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`GET ${endpoint} failed`);
      }
    } catch (error) {
      throw error;
    }
  },

  async post(endpoint, data, token) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`POST ${endpoint} failed`);
      }
    } catch (error) {
      throw error;
    }
  },

  async delete(endpoint, token) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`DELETE ${endpoint} failed`);
      }
    } catch (error) {
      throw error;
    }
  }
};

// =============================================================================
// AUTH CONTEXT
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
// AUTH PROVIDER
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

// =============================================================================
// LOADING SCREEN COMPONENT
// =============================================================================
export const LoadingScreen = () => (
  <div className="loading-container">
    <div>Loading...</div>
  </div>
);

// =============================================================================
// LOGIN FORM COMPONENT
// =============================================================================
export const LoginForm = ({ onToggleMode }) => {
  const [formData, setFormData] = useState({
    login: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p className="auth-subtitle">Sign in to your account</p>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login">Email or Username</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                id="login"
                name="login"
                value={formData.login}
                onChange={handleChange}
                required
                placeholder="Enter your email or username"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <span className="input-icon">🔒</span>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
            </div>
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading && <span className="loading-spinner"></span>}
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <p className="toggle-mode">
          New to our platform?
          <button type="button" onClick={onToggleMode}>
            Create Account
          </button>
        </p>
      </div>
    </div>
  );
};

// =============================================================================
// SIGNUP FORM COMPONENT
// =============================================================================
export const SignupForm = ({ onToggleMode }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePhotoChange = (e) => {
    if (e.target.files[0]) {
      setPhoto(e.target.files[0]);
    }
  };

  const validatePassword = (password) => {
    const requirements = [];
    
    if (password.length < 8) {
      requirements.push('at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
      requirements.push('at least one uppercase letter (A-Z)');
    }
    if (!/[a-z]/.test(password)) {
      requirements.push('at least one lowercase letter (a-z)');
    }
    if (!/\d/.test(password)) {
      requirements.push('at least one numeric digit (0-9)');
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      requirements.push('at least one special character (!@#$%^&*)');
    }
    
    return requirements;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate password requirements
    const passwordRequirements = validatePassword(formData.password);
    if (passwordRequirements.length > 0) {
      setError('Password does not meet security requirements. Please ensure it contains at least 8 characters including uppercase, lowercase, numeric, and special characters.');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const submitData = new FormData();
    submitData.append('username', formData.username);
    submitData.append('email', formData.email);
    submitData.append('password', formData.password);
    
    if (photo) {
      submitData.append('photo', photo);
    }

    const result = await signup(submitData);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Join Us Today</h2>
          <p className="auth-subtitle">Create your new account</p>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Choose a username"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <span className="input-icon">📧</span>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <span className="input-icon">🔒</span>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Create a secure password"
              />
            </div>
            <div className="password-requirements">
              <p className="requirements-text">
                Password must contain at least 8 characters including uppercase, lowercase, numeric, and special characters.
              </p>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <div className="input-wrapper">
              <span className="input-icon">🔐</span>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="photo">Profile Photo (Optional)</label>
            <input
              type="file"
              id="photo"
              name="photo"
              onChange={handlePhotoChange}
              accept="image/*"
              placeholder="📷 Upload your photo"
            />
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading && <span className="loading-spinner"></span>}
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="toggle-mode">
          Already have an account?
          <button type="button" onClick={onToggleMode}>
            Sign In
          </button>
        </p>
      </div>
    </div>
  );
};

// =============================================================================
// HEADER COMPONENT
// =============================================================================
export const Header = ({ title }) => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="header">
      <h1>{title}</h1>
      
      {user && (
        <div className="profile-section">
          <div className="profile-info">
            <div className="profile-username">{user.username}</div>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
          
          {user.photo_url ? (
            <img
              src={`${API_BASE}${user.photo_url}`}
              alt={user.username}
              className="profile-photo"
            />
          ) : (
            <div className="profile-photo">
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// =============================================================================
// AUTH WRAPPER COMPONENT
// =============================================================================
export const AuthWrapper = ({ children }) => {
  const { user, loading } = useAuth();
  const [authMode, setAuthMode] = useState('login');

  if (loading) {
    return <LoadingScreen />;
  }

  if (!user) {
    return authMode === 'login' ? (
      <LoginForm onToggleMode={() => setAuthMode('signup')} />
    ) : (
      <SignupForm onToggleMode={() => setAuthMode('login')} />
    );
  }

  return children;
};

// =============================================================================
// DEFAULT EXPORT
// =============================================================================
export default {
  AuthProvider,
  AuthWrapper,
  Header,
  LoadingScreen,
  useAuth,
  ApiService
};