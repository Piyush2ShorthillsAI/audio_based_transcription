import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider, AuthWrapper, Header, useAuth } from './authservice/AuthService';
import ContactDetail from './ContactDetail';
import AllContacts from './components/AllContacts';
import RecentContacts from './components/RecentContacts';
import Favourites from './components/Favourites';

import './App.css';

function AuthenticatedApp() {
  const [persons, setPersons] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, apiService, token } = useAuth();
  
  // SIMPLIFIED: Compute favorites and recents from persons list
  const favorites = useMemo(() => 
    persons.filter(person => person.is_favorite), 
    [persons]
  );
  
  const recentContacts = useMemo(() => {
    const recents = persons
      .filter(person => person.last_accessed_at)
      .map(person => ({
        contact: person,
        accessedAt: person.last_accessed_at
      }))
      .sort((a, b) => new Date(b.accessedAt) - new Date(a.accessedAt))
      .slice(0, 20);
    
    return recents;
  }, [persons]);

  // SIMPLIFIED: Just fetch persons on mount (contains all data we need)
  useEffect(() => {
    console.log('🚀 App mounting - Simplified approach: fetching contacts directly...');
    if (user && token) {
      fetchPersons();
    }
  }, [user, token]);

  // SIMPLIFIED: No localStorage management needed anymore - everything is in the database

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

  // SIMPLIFIED: No more complex sync logic needed - everything comes from /persons endpoint

  const handleContactClick = async (contact) => {
    console.log('🔄 Updating contact access time:', contact.name);
    
    // SIMPLIFIED APPROACH: Just call the recents API and refresh persons list
    if (user && token) {
      try {
        const result = await apiService.post(`/recents/${contact.id}`, {}, token);
        console.log('🌐 Contact access time updated:', result);
        
        // Refresh the main persons list which now includes last_accessed_at field
        await fetchPersons();
      } catch (error) {
        console.log('🌐 Backend update failed:', error.message);
      }
    }
  };

  const handleToggleFavorite = async (contact) => {
    console.log(`❤️ Toggling favorite:`, contact.name);
    
    // SIMPLIFIED APPROACH: Just call the toggle API and refresh persons list
    if (user && token) {
      try {
        const result = await apiService.post(`/favorites/${contact.id}`, {}, token);
        console.log('🌐 Favorite toggled successfully:', result);
        
        // Refresh the main persons list which now includes is_favorite field
        await fetchPersons();
      } catch (error) {
        console.log('🌐 Backend toggle failed:', error.message);
      }
    }
  };

  const handleClearRecent = async () => {
    console.log('🗑️ Clearing recent contacts');
    
    // SIMPLIFIED: Call API to clear recents and refresh persons list
    if (user && token) {
      try {
        await apiService.delete('/recents', token);
        console.log('🌐 Cleared recent contacts on backend');
        
        // Refresh the main persons list which now has updated last_accessed_at fields
        await fetchPersons();
      } catch (error) {
        console.log('🌐 Backend clear failed:', error.message);
      }
    }
  };

  const handleClearFavorites = async () => {
    console.log('🗑️ Clearing favorites');
    
    // SIMPLIFIED: Call API to clear favorites and refresh persons list
    if (user && token) {
      try {
        await apiService.delete('/favorites', token);
        console.log('🌐 Cleared favorites on backend');
        
        // Refresh the main persons list which now has updated is_favorite fields
        await fetchPersons();
      } catch (error) {
        console.log('🌐 Backend clear failed:', error.message);
      }
    }
  };

  const tabs = [
    { id: 'all', label: 'All Contacts', icon: '📱', count: persons.length },
    { id: 'recent', label: 'Recent', icon: '⏰', count: Math.min(recentContacts.length, 10) },
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
            onContactClick={handleContactClick}
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
