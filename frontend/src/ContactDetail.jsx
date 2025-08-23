import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from './authservice/AuthService';

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
      <div style={{ padding: '2rem', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'white' }}>
        <p style={{ color: 'red', fontSize: '18px', marginBottom: '20px' }}>Error: {error}</p>
        <Link to="/" style={{ color: '#667eea', textDecoration: 'none', padding: '12px 24px', borderRadius: '8px', border: '1px solid #667eea', fontWeight: '600' }}>
          ← Back to contacts
        </Link>
      </div>
    );
  }

  if (!contact) {
    return (
      <div style={{ padding: '2rem', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'white' }}>
        <p style={{ fontSize: '18px', color: '#6c757d' }}>Loading contact details...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="main-container" style={{ padding: '0', height: '100vh' }}>
        <div className="contact-detail-card">
          <div className="contact-detail-header">
            <Link to="/" className="header-back-button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5"></path>
                <path d="M12 19l-7-7 7-7"></path>
              </svg>
            </Link>
            <div className="header-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div className="contact-detail-info">
              <h1 className="contact-detail-title">Contact Information</h1>
              <p className="contact-detail-subtitle">
                Personal details and information
              </p>
            </div>
          </div>
          
          <div className="contact-detail-body">
            <div className="contact-avatar-large">
              <div className="avatar-circle-large">
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <h2 className="contact-name-large">{contact.name}</h2>
            </div>
            
            <div className="details-cards">
              <div className="detail-card">
                <div className="detail-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
                <div className="detail-card-content">
                  <h4>Full Name</h4>
                  <p>{contact.name}</p>
                </div>
              </div>
              
              <div className="detail-card">
                <div className="detail-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </div>
                <div className="detail-card-content">
                  <h4>Email Address</h4>
                  <p>{contact.email || 'Not provided'}</p>
                </div>
              </div>
              
              {contact.created_at && (
                <div className="detail-card">
                  <div className="detail-card-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line>
                      <line x1="8" y1="2" x2="8" y2="6"></line>
                      <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                  </div>
                  <div className="detail-card-content">
                    <h4>Date Added</h4>
                    <p>{new Date(contact.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .header-back-button {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 44px;
          height: 44px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          color: white;
          text-decoration: none;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          margin-right: 20px;
          flex-shrink: 0;
        }
        
        .header-back-button:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateX(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .header-back-button svg {
          width: 20px;
          height: 20px;
          color: white;
        }
        
        .contact-detail-card {
          background: white;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
        }
        
        .contact-detail-header {
          display: flex;
          align-items: center;
          padding: 32px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          flex-shrink: 0;
        }
        
        .header-icon {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 24px;
          border: 3px solid rgba(255, 255, 255, 0.3);
        }
        
        .header-icon svg {
          width: 40px;
          height: 40px;
          color: white;
        }
        
        .contact-detail-title {
          margin: 0 0 8px 0;
          font-size: 32px;
          font-weight: 700;
        }
        
        .contact-detail-subtitle {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
        }
        
        .contact-detail-body {
          padding: 40px 32px;
          flex: 1;
          overflow-y: auto;
          background: #f8f9fa;
        }
        
        .contact-avatar-large {
          text-align: center;
          margin-bottom: 40px;
        }
        
        .avatar-circle-large {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 48px;
          color: white;
          margin: 0 auto 20px auto;
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
          border: 4px solid white;
        }
        
        .contact-name-large {
          margin: 0;
          font-size: 32px;
          font-weight: 700;
          color: #2c3e50;
          text-align: center;
        }
        
        .details-cards {
          display: grid;
          gap: 24px;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }
        
        .detail-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          border: 1px solid rgba(102, 126, 234, 0.1);
          transition: all 0.2s ease;
        }
        
        .detail-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        }
        
        .detail-card-icon {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 16px;
        }
        
        .detail-card-icon svg {
          width: 24px;
          height: 24px;
          color: white;
        }
        
        .detail-card-content h4 {
          margin: 0 0 8px 0;
          font-size: 16px;
          font-weight: 600;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .detail-card-content p {
          margin: 0;
          font-size: 18px;
          color: #2c3e50;
          font-weight: 600;
          word-break: break-all;
        }
        
        
        @media (max-width: 768px) {
          .header-back-button {
            width: 40px;
            height: 40px;
            margin-right: 12px;
          }
          
          .header-back-button svg {
            width: 18px;
            height: 18px;
          }
          
          .contact-detail-header {
            flex-direction: row;
            text-align: left;
            padding: 20px;
            align-items: center;
          }
          
          .header-icon {
            margin-right: 12px;
            margin-bottom: 0;
            width: 50px;
            height: 50px;
          }
          
          .header-icon svg {
            width: 24px;
            height: 24px;
          }
          
          .contact-detail-title {
            font-size: 20px;
            margin-bottom: 4px;
          }
          
          .contact-detail-subtitle {
            font-size: 14px;
          }
          
          .contact-detail-body {
            padding: 24px 20px;
          }
          
          .contact-avatar-large {
            margin-bottom: 30px;
          }
          
          .avatar-circle-large {
            width: 100px;
            height: 100px;
            font-size: 40px;
          }
          
          .contact-name-large {
            font-size: 24px;
          }
          
          .details-cards {
            grid-template-columns: 1fr;
            gap: 20px;
          }
          
          .detail-card {
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
}

export default ContactDetail;