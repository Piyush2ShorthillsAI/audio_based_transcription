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
      <div className="main-container" style={{ padding: '0 20px' }}>
        <div className="contact-detail-card">
          <div className="contact-detail-header">
            <div className="contact-detail-avatar">
              {contact.name.charAt(0).toUpperCase()}
            </div>
            <div className="contact-detail-info">
              <h1 className="contact-detail-name">{contact.name}</h1>
              <p className="contact-detail-email">
                {contact.email || 'No email provided'}
              </p>
            </div>
          </div>
          
          <div className="contact-detail-body">
            <div className="detail-section">
              <h3>Contact Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Full Name</label>
                  <span>{contact.name}</span>
                </div>
                <div className="detail-item">
                  <label>Email Address</label>
                  <span>{contact.email || 'Not provided'}</span>
                </div>
                <div className="detail-item">
                  <label>Contact ID</label>
                  <span className="contact-id">{contact.id}</span>
                </div>
                {contact.created_at && (
                  <div className="detail-item">
                    <label>Date Added</label>
                    <span>{new Date(contact.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="contact-detail-footer">
            <Link to="/" className="back-button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5"></path>
                <path d="M12 19l-7-7 7-7"></path>
              </svg>
              Back to Contacts
            </Link>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .contact-detail-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          max-width: 800px;
          margin: 0 auto;
        }
        
        .contact-detail-header {
          display: flex;
          align-items: center;
          padding: 32px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }
        
        .contact-detail-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 32px;
          margin-right: 24px;
          border: 3px solid rgba(255, 255, 255, 0.3);
        }
        
        .contact-detail-name {
          margin: 0 0 8px 0;
          font-size: 28px;
          font-weight: 700;
        }
        
        .contact-detail-email {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
        }
        
        .contact-detail-body {
          padding: 32px;
        }
        
        .detail-section h3 {
          margin: 0 0 24px 0;
          font-size: 20px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        .detail-grid {
          display: grid;
          gap: 20px;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
        
        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .detail-item label {
          font-size: 12px;
          font-weight: 600;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .detail-item span {
          font-size: 16px;
          color: #2c3e50;
          font-weight: 500;
        }
        
        .contact-id {
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 12px !important;
          background: #f8f9fa;
          padding: 8px 12px;
          border-radius: 6px;
          border: 1px solid #e9ecef;
          word-break: break-all;
        }
        
        .contact-detail-footer {
          padding: 24px 32px;
          background: #f8f9fa;
          border-top: 1px solid #e9ecef;
        }
        
        .back-button {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: #667eea;
          text-decoration: none;
          font-weight: 600;
          padding: 12px 20px;
          border-radius: 10px;
          transition: all 0.2s ease;
          background: white;
          border: 1px solid #e1e5e9;
        }
        
        .back-button:hover {
          background: #667eea;
          color: white;
          transform: translateX(-4px);
        }
        
        .back-button svg {
          width: 18px;
          height: 18px;
        }
        
        @media (max-width: 768px) {
          .contact-detail-header {
            flex-direction: column;
            text-align: center;
            padding: 24px;
          }
          
          .contact-detail-avatar {
            margin-right: 0;
            margin-bottom: 16px;
          }
          
          .contact-detail-body {
            padding: 24px;
          }
          
          .detail-grid {
            grid-template-columns: 1fr;
          }
          
          .contact-detail-footer {
            padding: 20px 24px;
          }
        }
      `}</style>
    </div>
  );
}

export default ContactDetail;