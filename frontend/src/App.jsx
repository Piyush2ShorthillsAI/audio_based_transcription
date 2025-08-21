import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider, AuthWrapper, Header, useAuth } from './authservice/AuthService';
import ContactDetail from './ContactDetail';
import AllContacts from './components/AllContacts';
import RecentContacts from './components/RecentContacts';
import Favourites from './components/Favourites';
import DebugPanel from './DebugPanel';
import LocalStorageTester from './LocalStorageTester';
import './App.css';

function AuthenticatedApp() {
  const [persons, setPersons] = useState([]);
  const [recentContacts, setRecentContacts] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [localStorageLoaded, setLocalStorageLoaded] = useState(false);
  const { user, apiService, token } = useAuth();

  // Load from localStorage immediately on mount (only once)
  useEffect(() => {
    console.log('🚀 App mounting - Loading from localStorage...');
    
    const savedRecent = localStorage.getItem('recentContacts');
    const savedFavorites = localStorage.getItem('favoriteContacts');
    
    console.log('📊 localStorage check:', { 
      hasRecents: !!savedRecent, 
      hasFavorites: !!savedFavorites,
      recentsSize: savedRecent?.length || 0,
      favoritesSize: savedFavorites?.length || 0
    });
    
    // Load recent contacts
    if (savedRecent && savedRecent !== 'null' && savedRecent !== '[]') {
      try {
        const parsedRecents = JSON.parse(savedRecent);
        if (Array.isArray(parsedRecents) && parsedRecents.length > 0) {
          setRecentContacts(parsedRecents);
          console.log('✅ Loaded recent contacts from localStorage:', parsedRecents.length);
        }
      } catch (e) {
        console.error('❌ Error parsing recent contacts:', e);
        localStorage.removeItem('recentContacts'); // Clear corrupted data
      }
    }
    
    // Load favorites
    if (savedFavorites && savedFavorites !== 'null' && savedFavorites !== '[]') {
      try {
        const parsedFavorites = JSON.parse(savedFavorites);
        if (Array.isArray(parsedFavorites) && parsedFavorites.length > 0) {
          setFavorites(parsedFavorites);
          console.log('✅ Loaded favorites from localStorage:', parsedFavorites.length);
        }
      } catch (e) {
        console.error('❌ Error parsing favorites:', e);
        localStorage.removeItem('favoriteContacts'); // Clear corrupted data
      }
    }
    
    console.log('📱 Initial load complete');
    setLocalStorageLoaded(true);
  }, []); // Empty dependency array - run only once on mount

  // Debug functions available in browser console
  useEffect(() => {
    // Debug function to check localStorage
    window.debugStorage = () => {
      const recents = localStorage.getItem('recentContacts');
      const favorites = localStorage.getItem('favoriteContacts');
      console.log('📊 localStorage Debug:');
      console.log('Recent Contacts:', recents ? JSON.parse(recents).length + ' items' : 'empty');
      console.log('Favorites:', favorites ? JSON.parse(favorites).length + ' items' : 'empty');
      console.log('Current State - Recents:', recentContacts.length, 'Favorites:', favorites.length);
      return {
        localStorage: { recents, favorites },
        state: { recentContacts, favorites }
      };
    };

    // Force save current state to localStorage
    window.forceSave = () => {
      localStorage.setItem('recentContacts', JSON.stringify(recentContacts));
      localStorage.setItem('favoriteContacts', JSON.stringify(favorites));
      console.log('💾 Force saved to localStorage');
      console.log('Recents:', recentContacts.length, 'Favorites:', favorites.length);
    };

    // Force load from localStorage
    window.forceLoad = () => {
      const savedRecent = localStorage.getItem('recentContacts');
      const savedFavorites = localStorage.getItem('favoriteContacts');
      
      if (savedRecent) {
        const parsed = JSON.parse(savedRecent);
        setRecentContacts(parsed);
        console.log('📱 Force loaded recents:', parsed.length);
      }
      
      if (savedFavorites) {
        const parsed = JSON.parse(savedFavorites);
        setFavorites(parsed);
        console.log('📱 Force loaded favorites:', parsed.length);
      }
    };

    // Test localStorage persistence
    window.testPersistence = () => {
      const testData = { test: 'data', timestamp: Date.now() };
      localStorage.setItem('persistenceTest', JSON.stringify(testData));
      
      const retrieved = localStorage.getItem('persistenceTest');
      const success = retrieved && JSON.parse(retrieved).test === 'data';
      
      localStorage.removeItem('persistenceTest');
      
      console.log('🧪 localStorage Test:', success ? '✅ WORKING' : '❌ FAILED');
      return success;
    };
  }, [recentContacts, favorites]);

  // Sync with backend when user and token become available (but only after localStorage is loaded)
  useEffect(() => {
    if (user && token && localStorageLoaded) {
      console.log('User logged in and localStorage loaded - attempting backend sync...');
      // Additional delay to ensure UI is stable
      const syncTimer = setTimeout(() => {
        syncWithBackend();
      }, 1500); // 1.5 second delay
      
      return () => clearTimeout(syncTimer);
    }
  }, [user, token, localStorageLoaded]);

  // Save to localStorage whenever state changes (after initial load)
  useEffect(() => {
    if (localStorageLoaded && recentContacts.length >= 0) {
      localStorage.setItem('recentContacts', JSON.stringify(recentContacts));
      console.log('💾 Auto-saved recents to localStorage:', recentContacts.length);
    }
  }, [recentContacts, localStorageLoaded]);

  useEffect(() => {
    if (localStorageLoaded && favorites.length >= 0) {
      localStorage.setItem('favoriteContacts', JSON.stringify(favorites));
      console.log('💾 Auto-saved favorites to localStorage:', favorites.length);
    }
  }, [favorites, localStorageLoaded]);

  // Fetch contacts when user and token are available
  useEffect(() => {
    if (user && token) {
      fetchPersons();
    }
  }, [user, token]);

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

  // Helper function to merge recent contacts from backend and local storage
  const mergeRecentContacts = (backendData, localData) => {
    // Convert backend data to expected format if needed
    const backendRecents = Array.isArray(backendData) ? backendData : [];
    const localRecents = Array.isArray(localData) ? localData : [];
    
    // Create a map to avoid duplicates (prefer most recent access time)
    const contactMap = new Map();
    
    // Add local contacts first
    localRecents.forEach(item => {
      if (item.contact && item.contact.id) {
        contactMap.set(item.contact.id, item);
      }
    });
    
    // Add backend contacts (will overwrite if more recent)
    backendRecents.forEach(item => {
      if (item.contact && item.contact.id) {
        const existing = contactMap.get(item.contact.id);
        if (!existing || new Date(item.accessedAt) > new Date(existing.accessedAt)) {
          contactMap.set(item.contact.id, item);
        }
      }
    });
    
    // Convert back to array and sort by access time
    return Array.from(contactMap.values())
      .sort((a, b) => new Date(b.accessedAt) - new Date(a.accessedAt))
      .slice(0, 20); // Limit to 20 most recent
  };

  // Helper function to merge favorites from backend and local storage
  const mergeFavorites = (backendData, localData) => {
    const backendFavorites = Array.isArray(backendData) ? backendData : [];
    const localFavorites = Array.isArray(localData) ? localData : [];
    
    // Create a map to avoid duplicates
    const contactMap = new Map();
    
    // Add all contacts (both backend and local)
    [...backendFavorites, ...localFavorites].forEach(contact => {
      if (contact && contact.id) {
        contactMap.set(contact.id, contact);
      }
    });
    
    // Convert back to array
    return Array.from(contactMap.values());
  };

  const syncWithBackend = async () => {
    try {
      // Try to sync with backend, but don't fail if it doesn't work
      await Promise.all([
        fetchRecentContacts(),
        fetchFavorites()
      ]);
    } catch (error) {
      console.log('Backend sync unavailable, using localStorage');
    }
  };

  const fetchRecentContacts = async () => {
    try {
      console.log('🌐 Fetching recent contacts from backend...');
      const data = await apiService.get('/recents', token);
      console.log('📊 Backend recents response:', data?.length || 0, 'items');
      console.log('📊 Current local recents:', recentContacts.length, 'items');
      
      // CONSERVATIVE APPROACH: Only merge if backend has MORE data or local is completely empty
      if (Array.isArray(data)) {
        if (recentContacts.length === 0) {
          // No local data, use backend data
          if (data.length > 0) {
            setRecentContacts(data);
            console.log('✅ Using backend recents (no local data):', data.length);
          } else {
            console.log('⚠️ Both local and backend empty for recents');
          }
        } else if (data.length > recentContacts.length) {
          // Backend has more data, merge intelligently
          const merged = mergeRecentContacts(data, recentContacts);
          setRecentContacts(merged);
          console.log('✅ Merged recents (backend had more data):', merged.length);
        } else {
          // Keep local data (it's equal or better)
          console.log('✅ Keeping local recents (equal or better than backend)');
        }
      } else {
        console.log('⚠️ Invalid backend data format, keeping local recents');
      }
    } catch (error) {
      console.log('🔴 Backend error, keeping localStorage recents:', error.message);
    }
  };

  const fetchFavorites = async () => {
    try {
      console.log('🌐 Fetching favorites from backend...');
      const data = await apiService.get('/favorites', token);
      console.log('📊 Backend favorites response:', data?.length || 0, 'items');
      console.log('📊 Current local favorites:', favorites.length, 'items');
      
      // CONSERVATIVE APPROACH: Only merge if backend has MORE data or local is completely empty
      if (Array.isArray(data)) {
        if (favorites.length === 0) {
          // No local data, use backend data
          if (data.length > 0) {
            setFavorites(data);
            console.log('✅ Using backend favorites (no local data):', data.length);
          } else {
            console.log('⚠️ Both local and backend empty for favorites');
          }
        } else if (data.length > favorites.length) {
          // Backend has more data, merge intelligently
          const merged = mergeFavorites(data, favorites);
          setFavorites(merged);
          console.log('✅ Merged favorites (backend had more data):', merged.length);
        } else {
          // Keep local data (it's equal or better)
          console.log('✅ Keeping local favorites (equal or better than backend)');
        }
      } else {
        console.log('⚠️ Invalid backend data format, keeping local favorites');
      }
    } catch (error) {
      console.log('🔴 Backend error, keeping localStorage favorites:', error.message);
    }
  };

  const handleContactClick = async (contact) => {
    console.log('🔄 Adding contact to recents:', contact.name);
    
    // Immediately update UI (optimistic update) - localStorage auto-saves via useEffect
    setRecentContacts(prev => {
      const filtered = prev.filter(item => item.contact?.id !== contact.id);
      const newRecent = [{
        contact,
        accessedAt: new Date().toISOString()
      }, ...filtered].slice(0, 20);
      
      return newRecent;
    });

    // CRITICAL: Always try to sync with backend for cross-device functionality
    if (user && token) {
      try {
        const result = await apiService.post(`/recents/${contact.id}`, {}, token);
        console.log('🌐 Synced with backend successfully:', result);
      } catch (error) {
        console.log('🌐 Backend sync failed (data still saved locally):', error.message);
      }
    }
  };

  const handleToggleFavorite = async (contact) => {
    const isFavorite = favorites.some(fav => fav.id === contact.id);
    console.log(`❤️ ${isFavorite ? 'Removing' : 'Adding'} favorite:`, contact.name);
    
    // Immediately update UI (optimistic update) - localStorage auto-saves via useEffect
    setFavorites(prev => {
      const newFavorites = isFavorite 
        ? prev.filter(fav => fav.id !== contact.id)
        : [...prev, contact];
      
      return newFavorites;
    });

    // CRITICAL: Always try to sync with backend for cross-device functionality
    if (user && token) {
      try {
        let result;
        if (isFavorite) {
          result = await apiService.delete(`/favorites/${contact.id}`, token);
        } else {
          result = await apiService.post(`/favorites/${contact.id}`, {}, token);
        }
        console.log('🌐 Favorite synced with backend successfully:', result);
      } catch (error) {
        console.log('🌐 Backend sync failed (data still saved locally):', error.message);
      }
    }
  };

  const handleClearRecent = async () => {
    console.log('🗑️ Clearing recent contacts');
    
    // Immediately update UI - localStorage auto-saves via useEffect
    setRecentContacts([]);

    // Try to sync with backend in background
    if (user && token) {
      try {
        await apiService.delete('/recents', token);
        console.log('🌐 Cleared recent contacts on backend');
      } catch (error) {
        console.log('🌐 Backend clear failed (localStorage auto-cleared)');
      }
    }
  };

  const handleClearFavorites = async () => {
    console.log('🗑️ Clearing favorites');
    
    // Immediately update UI - localStorage auto-saves via useEffect
    setFavorites([]);

    // Try to sync with backend in background
    if (user && token) {
      try {
        await apiService.delete('/favorites', token);
        console.log('🌐 Cleared favorites on backend');
      } catch (error) {
        console.log('🌐 Backend clear failed (localStorage auto-cleared)');
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
          />
        );
      default:
        return null;
    }
  };

  return (
    <Router>
      <div className="App">
        <DebugPanel 
          recentContacts={recentContacts}
          favorites={favorites}
        />
        <LocalStorageTester />
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
