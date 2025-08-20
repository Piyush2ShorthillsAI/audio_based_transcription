import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { AuthProvider, AuthWrapper, Header, useAuth } from './authservice/AuthService';
import ContactDetail from './ContactDetail';
import './App.css';

function AuthenticatedApp() {
  const [persons, setPersons] = useState([]);
  const [error, setError] = useState(null);
  const { user, apiService, token } = useAuth();

  useEffect(() => {
    if (user && token) {
      fetchPersons();
    }
  }, [user, token]);

  const fetchPersons = async () => {
    try {
      const data = await apiService.fetchPersons(token);
      setPersons(data);
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <Router>
      <div className="App">
        <Header title="List of CRM Contacts" />
        
        {error ? (
          <p style={{ color: 'red' }}>Error: {error}</p>
        ) : (
          <div style={{ padding: '0 2rem' }}>
            <Routes>
              <Route path="/" element={
                <div>
                  <h2>Welcome, {user?.username}!</h2>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {persons.map((person) => (
                      <li key={person.id} style={{ 
                        marginBottom: '0.5rem',
                        padding: '0.75rem',
                        backgroundColor: '#f5f5f5',
                        borderRadius: '5px'
                      }}>
                        <Link 
                          to={`/contact/${person.id}`}
                          style={{
                            textDecoration: 'none',
                            color: '#667eea',
                            fontWeight: '500'
                          }}
                        >
                          {person.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              } />
              <Route path="/contact/:id" element={<ContactDetail />} />
            </Routes>
          </div>
        )}
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
