import React, { useState, useRef, useEffect } from 'react';
import ContactCardWithMessagePreview from './ContactCardWithMessagePreview';
import './ContactsList.css';

const Favourites = ({ 
  favorites, 
  onToggleFavorite, 
  onClearFavorites,
  onContactClick
}) => {
  const [isRestoringScroll, setIsRestoringScroll] = useState(false);
  const contactsListRef = useRef(null);
  const scrollTimeoutRef = useRef(null);
  const SCROLL_POSITION_KEY = 'favourites_scrollPosition';
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

  // Save scroll position 
  const saveScrollPosition = () => {
    if (contactsListRef.current && !isRestoringScroll) {
      const scrollTop = contactsListRef.current.scrollTop;
      window.sessionStorage.setItem(SCROLL_POSITION_KEY, scrollTop.toString());
      console.log('💾 SAVED scroll position:', scrollTop);
    }
  };

  // Contact click handler
  const handleContactClickWithScroll = (contact) => {
    console.log('🔥 CONTACT CLICKED - SAVING SCROLL NOW!');
    console.log('🔥 Current scroll position:', contactsListRef.current?.scrollTop);
    
    if (contactsListRef.current) {
      const currentScroll = contactsListRef.current.scrollTop;
      console.log('🔥 Explicitly saving:', currentScroll);
      
      // Force save immediately
      window.sessionStorage.setItem(SCROLL_POSITION_KEY, currentScroll.toString());
      
      console.log('🔥 Verification - what was saved:', window.sessionStorage.getItem(SCROLL_POSITION_KEY));
    } else {
      console.log('🔥 ERROR - contactsListRef.current is null!');
    }
    
    if (onContactClick) {
      onContactClick(contact);
    }
  };

  // EXACT COPY FROM ALLCONTACTS: Restore scroll position
  useEffect(() => {
    console.log('🚀 COMPONENT MOUNTED/UPDATED - Loading:', false, 'Favorites:', favorites?.length);
    
    if (!favorites || favorites.length === 0) {
      console.log('🚀 Skipping restore - not ready yet');
      return;
    }
    
    const savedScrollPosition = window.sessionStorage.getItem(SCROLL_POSITION_KEY);
    console.log('🔍 CHECKING STORAGE - Saved position:', savedScrollPosition);
    console.log('🔍 contactsListRef.current exists:', !!contactsListRef.current);
    
    if (savedScrollPosition && contactsListRef.current) {
      const scrollTop = parseInt(savedScrollPosition, 10);
      console.log('🔍 ATTEMPTING RESTORE TO:', scrollTop);
      
      // Set flag to prevent saving during restoration
      setIsRestoringScroll(true);
      
      // Try multiple timing approaches
      const attemptRestore = () => {
        if (contactsListRef.current) {
          console.log('🔍 Setting scrollTop to:', scrollTop);
          contactsListRef.current.scrollTop = scrollTop;
          
          // Check if it worked
          setTimeout(() => {
            if (contactsListRef.current) {
              const actualScroll = contactsListRef.current.scrollTop;
              console.log('🔍 After setting, actual scroll is:', actualScroll);
            }
          }, 50);
          
          // Clear restoration flag
          setTimeout(() => {
            setIsRestoringScroll(false);
          }, 200);
        }
      };
      
      // Try immediate
      attemptRestore();
      
      // Try with requestAnimationFrame
      requestAnimationFrame(() => {
        attemptRestore();
      });
      
      // Try with timeout
      setTimeout(() => {
        attemptRestore();
      }, 100);
      
    } else if (!savedScrollPosition) {
      console.log('🔍 No saved scroll position found');
    } else if (!contactsListRef.current) {
      console.log('🔍 contactsListRef.current is null');
    }
  }, [favorites?.length]);

  // EXACT COPY FROM ALLCONTACTS: Scroll event handler with throttling
  useEffect(() => {
    const contactsList = contactsListRef.current;
    if (!contactsList) return;
    
    const handleScroll = () => {
      const scrollTop = contactsList.scrollTop;
      
      // Throttle saves to avoid excessive storage writes
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      scrollTimeoutRef.current = setTimeout(() => {
        saveScrollPosition();
      }, 200); // Save 200ms after user stops scrolling
    };
    
    contactsList.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      contactsList.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // Save scroll position when component unmounts
  useEffect(() => {
    return () => {
      saveScrollPosition();
    };
  }, []);

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
      <div className="contacts-list" ref={contactsListRef}>
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
              <ContactCardWithMessagePreview
                key={contact.id}
                contact={contact}
                isFavorite={true}
                onToggleFavorite={onToggleFavorite}
                onViewContact={handleContactClickWithScroll} // Save scroll before navigation
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