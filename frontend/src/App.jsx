import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider, AuthWrapper, Header, useAuth } from './authservice/AuthService';
import ContactDetail from './ContactDetail';
import AllContacts from './components/AllContacts';
import RecentContacts from './components/RecentContacts';
import Favourites from './components/Favourites';
import './App.css';

function AuthenticatedApp() {
  const [persons, setPersons] = useState([]);
  const [recentContacts, setRecentContacts] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, apiService, token } = useAuth();

  // Load data from localStorage on component mount
  useEffect(() => {
    const savedRecent = localStorage.getItem('recentContacts');
    const savedFavorites = localStorage.getItem('favoriteContacts');
    
    if (savedRecent) {
      try {
        setRecentContacts(JSON.parse(savedRecent));
      } catch (e) {
        console.error('Error parsing recent contacts:', e);
      }
    }
    
    if (savedFavorites) {
      try {
        setFavorites(JSON.parse(savedFavorites));
      } catch (e) {
        console.error('Error parsing favorite contacts:', e);
      }
    }
  }, []);

  // Fetch contacts when user and token are available
  useEffect(() => {
    if (user && token) {
      fetchPersons();
    }
  }, [user, token]);

  // Save to localStorage whenever recentContacts or favorites change
  useEffect(() => {
    localStorage.setItem('recentContacts', JSON.stringify(recentContacts));
  }, [recentContacts]);

  useEffect(() => {
    localStorage.setItem('favoriteContacts', JSON.stringify(favorites));
  }, [favorites]);

  const fetchPersons = async () => {
    try {
      setLoading(true);
      const data = await apiService.fetchPersons(token);
      setPersons(data);
      setError(null);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleContactClick = (contact) => {
    // Add to recent contacts (max 20 items)
    setRecentContacts(prev => {
      const filtered = prev.filter(item => item.contact.id !== contact.id);
      const newRecent = [{
        contact,
        accessedAt: new Date().toISOString()
      }, ...filtered].slice(0, 20);
      return newRecent;
    });
  };

  const handleToggleFavorite = (contact) => {
    setFavorites(prev => {
      const exists = prev.find(fav => fav.id === contact.id);
      if (exists) {
        return prev.filter(fav => fav.id !== contact.id);
      } else {
        return [...prev, contact];
      }
    });
  };

  const handleClearRecent = () => {
    setRecentContacts([]);
  };

  const handleClearFavorites = () => {
    setFavorites([]);
  };

  const tabs = [
    { id: 'all', label: 'All Contacts', icon: '📱', count: persons.length },
    { id: 'recent', label: 'Recent', icon: '⏰', count: recentContacts.length },
    { id: 'favorites', label: 'Favorites', icon: '❤️', count: favorites.length }
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'all':
        return (
          <AllContacts
            contacts={persons}
            favorites={favorites}
            onToggleFavorite={handleToggleFavorite}
            onContactClick={handleContactClick}
            loading={loading}
          />
        );
      case 'recent':
        return (
          <RecentContacts
            recentContacts={recentContacts}
            favorites={favorites}
            onToggleFavorite={handleToggleFavorite}
            onClearRecent={handleClearRecent}
          />
        );
      case 'favorites':
        return (
          <Favourites
            favorites={favorites}
            onToggleFavorite={handleToggleFavorite}
            onClearFavorites={handleClearFavorites}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Router>
      <div className="App">
        <Header title="CRM Contacts" />
        
        {error && (
          <div className="error-banner">
            <p>Error: {error}</p>
            <button onClick={fetchPersons} className="retry-button">
              Try Again
            </button>
          </div>
        )}
        
        <Routes>
          <Route path="/" element={
            <div className="main-container">
              {/* Welcome Header */}
              <div className="welcome-header">
                <div className="welcome-content">
                  <h1>Welcome back, <span className="username">{user?.username}!</span></h1>
                  <p className="welcome-subtitle">Manage your contacts efficiently</p>
                </div>
                <div className="user-avatar">
                  {user?.username?.charAt(0).toUpperCase()}
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <span className="tab-icon">{tab.icon}</span>
                    <span className="tab-label">{tab.label}</span>
                    {tab.count > 0 && (
                      <span className="tab-count">{tab.count}</span>
                    )}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                {renderActiveTab()}
              </div>
            </div>
          } />
          <Route path="/contact/:id" element={<ContactDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthWrapper>
        <AuthenticatedApp />
      </AuthWrapper>
    </AuthProvider>
  );
}

export default App;
