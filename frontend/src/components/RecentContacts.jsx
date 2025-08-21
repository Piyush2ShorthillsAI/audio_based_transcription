import React from 'react';
import ContactCard from './ContactCard';
import './ContactsList.css';

const RecentContacts = ({ 
  recentContacts, 
  favorites, 
  onToggleFavorite, 
  onClearRecent 
}) => {
  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const accessTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - accessTime) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  return (
    <div className="contacts-container">
      {/* Header */}
      <div className="contacts-header">
        <div className="header-info">
          <h2>Recent Contacts</h2>
          <span className="contact-count">{recentContacts.length} contacts</span>
        </div>
        {recentContacts.length > 0 && (
          <button className="clear-button" onClick={onClearRecent}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18"></path>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
              <path d="M8 6V4c0-1 1-2 2-2h4c0 1 1 2 2 2v2"></path>
            </svg>
            Clear All
          </button>
        )}
      </div>

      {/* Info Banner */}
      <div className="info-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 6v6l4 2"></path>
        </svg>
        <span>Contacts you've recently viewed will appear here</span>
      </div>

      {/* Recent Contacts List */}
      <div className="contacts-list">
        {recentContacts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">⏰</div>
            <h3>No recent contacts</h3>
            <p>Contacts you view will appear here for quick access</p>
          </div>
        ) : (
          recentContacts.map(item => (
            <div key={`${item.contact.id}-${item.accessedAt}`} className="recent-contact-wrapper">
              <ContactCard
                contact={item.contact}
                isFavorite={favorites.some(fav => fav.id === item.contact.id)}
                onToggleFavorite={onToggleFavorite}
                onViewContact={null} // No need to add to recent again
                showHeart={true}
                variant="recent"
              />
              <div className="access-time">
                {formatTimeAgo(item.accessedAt)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecentContacts;