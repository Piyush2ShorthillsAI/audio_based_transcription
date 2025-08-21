import React, { useState, useEffect } from 'react';

const LocalStorageTester = () => {
  const [testResults, setTestResults] = useState('');
  const [isVisible, setIsVisible] = useState(false);

  const runCompletePersistenceTest = () => {
    const results = [];
    
    // Test 1: localStorage functionality
    results.push('🧪 COMPLETE PERSISTENCE TEST');
    results.push('================================');
    
    try {
      const testKey = 'persistenceTest';
      const testData = { test: 'data', timestamp: Date.now() };
      
      localStorage.setItem(testKey, JSON.stringify(testData));
      const retrieved = localStorage.getItem(testKey);
      
      if (retrieved && JSON.parse(retrieved).test === 'data') {
        results.push('✅ localStorage basic functionality: WORKING');
        localStorage.removeItem(testKey);
      } else {
        results.push('❌ localStorage basic functionality: FAILED');
        return results.join('\n');
      }
    } catch (error) {
      results.push(`❌ localStorage error: ${error.message}`);
      return results.join('\n');
    }

    // Test 2: Current data status
    results.push('');
    results.push('📊 Current Data Status:');
    const recents = localStorage.getItem('recentContacts');
    const favorites = localStorage.getItem('favoriteContacts');
    
    results.push(`Recent Contacts: ${recents ? JSON.parse(recents).length + ' items' : 'empty'}`);
    results.push(`Favorites: ${favorites ? JSON.parse(favorites).length + ' items' : 'empty'}`);

    // Test 3: Add test data
    results.push('');
    results.push('➕ Adding test data...');
    
    const testRecents = [{
      contact: { id: 'test-recent-1', name: 'Test Recent User', email: 'recent@test.com' },
      accessedAt: new Date().toISOString()
    }];
    
    const testFavorites = [
      { id: 'test-fav-1', name: 'Test Favorite 1', email: 'fav1@test.com' },
      { id: 'test-fav-2', name: 'Test Favorite 2', email: 'fav2@test.com' }
    ];
    
    try {
      localStorage.setItem('recentContacts', JSON.stringify(testRecents));
      localStorage.setItem('favoriteContacts', JSON.stringify(testFavorites));
      
      results.push('✅ Test data added successfully');
      results.push(`   - ${testRecents.length} recent contact(s)`);
      results.push(`   - ${testFavorites.length} favorite contact(s)`);
    } catch (error) {
      results.push(`❌ Failed to add test data: ${error.message}`);
    }

    // Test 4: Verification
    results.push('');
    results.push('🔍 Verifying persistence...');
    
    const verifyRecents = localStorage.getItem('recentContacts');
    const verifyFavorites = localStorage.getItem('favoriteContacts');
    
    if (verifyRecents && JSON.parse(verifyRecents).length > 0) {
      results.push('✅ Recent contacts persisted correctly');
    } else {
      results.push('❌ Recent contacts NOT persisted');
    }
    
    if (verifyFavorites && JSON.parse(verifyFavorites).length > 0) {
      results.push('✅ Favorites persisted correctly');
    } else {
      results.push('❌ Favorites NOT persisted');
    }

    // Test 5: Instructions
    results.push('');
    results.push('🎯 NEXT STEPS:');
    results.push('1. Refresh this page (F5 or Ctrl+R)');
    results.push('2. Check if test data is still there');
    results.push('3. If data persists, localStorage is working!');
    results.push('4. If data disappears, there\'s still an issue');
    results.push('');
    results.push('📱 You can also check the main app:');
    results.push('   - Look at Recent/Favorites tab counts');
    results.push('   - They should show the test data');

    return results.join('\n');
  };

  const clearTestData = () => {
    localStorage.removeItem('recentContacts');
    localStorage.removeItem('favoriteContacts');
    setTestResults('🗑️ Test data cleared from localStorage.\n\nRefresh the page to see if data truly disappears.');
  };

  const checkCurrentData = () => {
    const recents = localStorage.getItem('recentContacts');
    const favorites = localStorage.getItem('favoriteContacts');
    
    const results = [
      '📊 CURRENT LOCALSTORAGE STATUS',
      '================================',
      '',
      `Recent Contacts: ${recents ? `${JSON.parse(recents).length} items` : 'empty'}`,
      `Favorites: ${favorites ? `${JSON.parse(favorites).length} items` : 'empty'}`,
      '',
      'Raw data:',
      `Recents: ${recents || 'null'}`,
      `Favorites: ${favorites || 'null'}`
    ];
    
    setTestResults(results.join('\n'));
  };

  if (!isVisible) {
    return (
      <div style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        zIndex: 1000
      }}>
        <button 
          onClick={() => setIsVisible(true)}
          style={{
            background: '#28a745',
            color: 'white',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          🧪 Test Persistence
        </button>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '10px',
      right: '10px',
      background: 'white',
      border: '2px solid #28a745',
      borderRadius: '8px',
      padding: '15px',
      zIndex: 1000,
      maxWidth: '400px',
      maxHeight: '500px',
      overflowY: 'auto',
      fontSize: '11px',
      fontFamily: 'monospace',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: '#28a745' }}>🧪 localStorage Tester</h3>
        <button 
          onClick={() => setIsVisible(false)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}
        >
          ✕
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginBottom: '10px' }}>
        <button 
          onClick={() => setTestResults(runCompletePersistenceTest())}
          style={{ 
            padding: '6px 10px', 
            fontSize: '11px', 
            background: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '3px', 
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          🧪 Run Complete Test
        </button>
        
        <button 
          onClick={checkCurrentData}
          style={{ 
            padding: '6px 10px', 
            fontSize: '11px', 
            background: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '3px', 
            cursor: 'pointer' 
          }}
        >
          📊 Check Current Data
        </button>
        
        <button 
          onClick={clearTestData}
          style={{ 
            padding: '6px 10px', 
            fontSize: '11px', 
            background: '#dc3545', 
            color: 'white', 
            border: 'none', 
            borderRadius: '3px', 
            cursor: 'pointer' 
          }}
        >
          🗑️ Clear Test Data
        </button>
      </div>

      <div style={{ 
        background: '#f8f9fa', 
        border: '1px solid #dee2e6', 
        borderRadius: '4px', 
        padding: '8px', 
        whiteSpace: 'pre-wrap',
        fontSize: '10px',
        lineHeight: '1.3'
      }}>
        {testResults || 'Click "Run Complete Test" to start testing localStorage persistence.'}
      </div>
    </div>
  );
};

export default LocalStorageTester;