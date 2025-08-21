import React, { useState } from 'react';
import ContactCard from './ContactCard';
import './ContactsList.css';

const Favourites = ({ 
  favorites, 
  onToggleFavorite, 
  onClearFavorites,
  onContactClick 
}) => {
  const [showConfirmClear, setShowConfirmClear] = useState(false);

  const handleClearFavorites = () => {
    if (!showConfirmClear) {
      setShowConfirmClear(true);
      setTimeout(() => setShowConfirmClear(false), 3000); // Auto hide after 3s
    } else {
      onClearFavorites();
      setShowConfirmClear(false);
    }
  };

  const getFavoriteStats = () => {
    if (favorites.length === 0) return null;
    
    const withEmail = favorites.filter(contact => contact.email).length;
    const withoutEmail = favorites.length - withEmail;
    
    return { withEmail, withoutEmail, total: favorites.length };
  };

  const stats = getFavoriteStats();

  return (
    <div className="contacts-container">
      {/* Header */}
      <div className="contacts-header">
        <div className="header-info">
          <h2>Favourite Contacts</h2>
          <span className="contact-count">{favorites.length} favorites</span>
        </div>
        {favorites.length > 0 && (
          <button 
            className={`clear-button ${showConfirmClear ? 'confirm' : ''}`}
            onClick={handleClearFavorites}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
            {showConfirmClear ? 'Click to Confirm' : 'Clear All'}
          </button>
        )}
      </div>

      {/* Stats Banner */}
      {stats && (
        <div className="stats-banner">
          <div className="stat-item">
            <span className="stat-number">{stats.total}</span>
            <span className="stat-label">Total Favorites</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">{stats.withEmail}</span>
            <span className="stat-label">With Email</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">{stats.withoutEmail}</span>
            <span className="stat-label">Without Email</span>
          </div>
        </div>
      )}

      {/* Info Banner */}
      <div className="info-banner favorite-info">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
        <span>Your most important contacts are saved here</span>
      </div>

      {/* Favorites List */}
      <div className="contacts-list">
        {favorites.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💝</div>
            <h3>No favorite contacts</h3>
            <p>Click the heart icon on any contact to add them to your favorites</p>
            <div className="empty-hint">
              <div className="heart-demo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
              </div>
              <span>Click this icon to add to favorites</span>
            </div>
          </div>
        ) : (
          <>
            {favorites.map(contact => (
              <ContactCard
                key={contact.id}
                contact={contact}
                isFavorite={true}
                onToggleFavorite={onToggleFavorite}
                onViewContact={onContactClick} // Now viewing favorites also adds to recents
                showHeart={true}
                variant="favorite"
              />
            ))}
            
            {/* Quick Stats Footer */}
            <div className="favorites-footer">
              <p>
                {favorites.length === 1 
                  ? 'You have 1 favorite contact' 
                  : `You have ${favorites.length} favorite contacts`
                }
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Favourites;