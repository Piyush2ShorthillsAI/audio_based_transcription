import React, { useState, useEffect } from 'react';

const DebugPanel = ({ recentContacts, favorites, onForceLoad, onForceSave }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [localStorageStatus, setLocalStorageStatus] = useState('Unknown');

  useEffect(() => {
    // Test localStorage on component mount
    testLocalStorage();
  }, []);

  const testLocalStorage = () => {
    try {
      const testKey = 'debugTest';
      const testValue = { test: 'data', timestamp: Date.now() };
      
      localStorage.setItem(testKey, JSON.stringify(testValue));
      const retrieved = localStorage.getItem(testKey);
      
      if (retrieved && JSON.parse(retrieved).test === 'data') {
        setLocalStorageStatus('✅ Working');
        localStorage.removeItem(testKey);
      } else {
        setLocalStorageStatus('❌ Failed');
      }
    } catch (error) {
      setLocalStorageStatus('❌ Error: ' + error.message);
    }
  };

  const getStorageInfo = () => {
    const recents = localStorage.getItem('recentContacts');
    const favorites = localStorage.getItem('favoriteContacts');
    
    return {
      recents: recents ? JSON.parse(recents) : null,
      favorites: favorites ? JSON.parse(favorites) : null,
      recentsLength: recents ? JSON.parse(recents).length : 0,
      favoritesLength: favorites ? JSON.parse(favorites).length : 0
    };
  };

  const addTestData = () => {
    const testRecent = [{
      contact: { id: 'test-1', name: 'Test Contact 1', email: 'test1@example.com' },
      accessedAt: new Date().toISOString()
    }];
    
    const testFavorite = [{ id: 'test-2', name: 'Test Favorite 1', email: 'fav1@example.com' }];
    
    localStorage.setItem('recentContacts', JSON.stringify(testRecent));
    localStorage.setItem('favoriteContacts', JSON.stringify(testFavorite));
    
    alert('Test data added to localStorage. Refresh the page to see if it persists!');
  };

  const clearStorage = () => {
    localStorage.removeItem('recentContacts');
    localStorage.removeItem('favoriteContacts');
    alert('localStorage cleared!');
  };

  if (!isVisible) {
    return (
      <div style={{
        position: 'fixed',
        top: '10px',
        right: '10px',
        zIndex: 1000
      }}>
        <button 
          onClick={() => setIsVisible(true)}
          style={{
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            cursor: 'pointer'
          }}
        >
          🐛 Debug
        </button>
      </div>
    );
  }

  const storageInfo = getStorageInfo();

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'white',
      border: '2px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      zIndex: 1000,
      maxWidth: '300px',
      fontSize: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: 0, fontSize: '14px' }}>🐛 Debug Panel</h3>
        <button 
          onClick={() => setIsVisible(false)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}
        >
          ✕
        </button>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>localStorage Status:</strong> {localStorageStatus}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>Current State:</strong><br/>
        Recents: {recentContacts.length}<br/>
        Favorites: {favorites.length}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>localStorage Data:</strong><br/>
        Recents: {storageInfo.recentsLength}<br/>
        Favorites: {storageInfo.favoritesLength}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        <button 
          onClick={testLocalStorage}
          style={{ padding: '4px 8px', fontSize: '11px', background: '#28a745', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
        >
          Test localStorage
        </button>
        
        <button 
          onClick={addTestData}
          style={{ padding: '4px 8px', fontSize: '11px', background: '#17a2b8', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
        >
          Add Test Data
        </button>
        
        <button 
          onClick={() => {
            const info = getStorageInfo();
            console.log('📊 Storage Debug:', info);
            alert(`Recents: ${info.recentsLength}, Favorites: ${info.favoritesLength}`);
          }}
          style={{ padding: '4px 8px', fontSize: '11px', background: '#007bff', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
        >
          Log Storage
        </button>
        
        <button 
          onClick={clearStorage}
          style={{ padding: '4px 8px', fontSize: '11px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
        >
          Clear Storage
        </button>
      </div>
    </div>
  );
};

export default DebugPanel;