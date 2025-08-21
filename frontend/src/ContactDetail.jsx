import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth, Header } from './authservice/AuthService';

function ContactDetail() {
  const { id } = useParams();
  const [contact, setContact] = useState(null);
  const [error, setError] = useState(null);
  const { user, apiService, token } = useAuth();

  useEffect(() => {
    if (user && token) {
      fetchContact();
    }
  }, [id, user, token]);

  const fetchContact = async () => {
    try {
      const data = await apiService.fetchPerson(token, id);
      setContact(data);
    } catch (error) {
      setError(error.message);
    }
  };

  if (error) {
    return (
      <div>
        <Header title="Contact Details" />
        <div style={{ padding: '0 2rem' }}>
          <p style={{ color: 'red' }}>Error: {error}</p>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none' }}>
            ← Back to contacts
          </Link>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div>
        <Header title="Contact Details" />
        <div style={{ padding: '0 2rem' }}>
          <p>Loading contact details...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Header title="Contact Details" />
      <div style={{ padding: '0 2rem' }}>
        <div style={{ 
          backgroundColor: '#f9f9f9', 
          padding: '2rem', 
          borderRadius: '8px',
          maxWidth: '600px'
        }}>
          <h2 style={{ color: '#333', marginBottom: '1rem' }}>
            {contact.name}
          </h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>ID:</strong> {contact.id}
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>Name:</strong> {contact.name}
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>Email:</strong> {contact.email || 'No email provided'}
          </div>
          
          {contact.created_at && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Added:</strong> {new Date(contact.created_at).toLocaleDateString()}
            </div>
          )}
        </div>
        
        <div style={{ marginTop: '2rem' }}>
          <Link 
            to="/" 
            style={{ 
              color: '#667eea', 
              textDecoration: 'none',
              fontWeight: '500'
            }}
          >
            ← Back to contacts
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ContactDetail;