import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './ContactCard.css'; // Reuse existing styles

const ContactCardWithMessagePreview = React.memo(({ 
  contact, 
  isFavorite = false, 
  onToggleFavorite, 
  onViewContact,
  onMessageClick,
  showHeart = true,
  variant = 'default' 
}) => {
  const navigate = useNavigate();

  const handleCardClick = (e) => {
    // Only prevent default if clicking directly on card, not on buttons  
    if (e.target === e.currentTarget) {
      e.preventDefault();
    }
  };

  const handleHeartClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(contact);
    }
  };

  const handleViewClick = (e) => {
    e.stopPropagation();
    console.log('👁️ View button clicked for:', contact.name);
    if (onViewContact) {
      onViewContact(contact);
    }
  };

  const handleMessageClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Add contact to recents when generating message
    if (onMessageClick) {
      onMessageClick(contact);
    }
    
    navigate(`/message/${contact.id}`);
  };

  return (
    <>
      <div className={`contact-card ${variant}`} onClick={handleCardClick}>
        <div className="contact-avatar">
          <div className="avatar-circle">
            {contact.name.charAt(0).toUpperCase()}
          </div>
  
        </div>
        
        <div className="contact-info">
          <h3 className="contact-name">{contact.name}</h3>
          <p className="contact-email">
            {contact.email || 'No email provided'}
          </p>
          {contact.created_at && (
            <p className="contact-date">
              Added {new Date(contact.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
        
        <div className="contact-actions">
          <button 
            className="action-button message-button"
            onClick={handleMessageClick}
            title="Generate message from voice"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              <path d="M12 7v6"></path>
              <path d="M9 10h6"></path>
            </svg>
          </button>

          {showHeart && (
            <button 
              className={`heart-button ${isFavorite ? 'favorite' : ''}`}
              onClick={handleHeartClick}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <svg 
                viewBox="0 0 24 24" 
                fill={isFavorite ? 'currentColor' : 'none'} 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
            </button>
          )}
          
          <Link 
            to={`/contact/${contact.id}`} 
            className="view-button"
            onClick={handleViewClick}
            title="View contact details"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </Link>
        </div>
      </div>
    </>
  );
});

ContactCardWithMessagePreview.displayName = 'ContactCardWithMessagePreview';

export default ContactCardWithMessagePreview;