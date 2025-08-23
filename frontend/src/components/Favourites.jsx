import React, { useState, useRef, useEffect, useMemo } from 'react';
import ContactCardWithMessagePreview from './ContactCardWithMessagePreview';
import './ContactsList.css';

const Favourites = ({ 
  favorites, 
  onToggleFavorite, 
  onClearFavorites,
  onContactClick
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name'); // 'name', 'email', 'date'
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

  // Filter and sort favorites based on search term and sort option
  const filteredFavorites = useMemo(() => {
    let filtered = favorites;
    
    // Apply search filter if search term exists
    if (searchTerm.trim()) {
      filtered = favorites.filter(contact =>
        contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (contact.email && contact.email.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    // Apply sorting
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'email':
          return (a.email || '').localeCompare(b.email || '');
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at); // Most recent first
        default:
          return 0;
      }
    });
  }, [favorites, searchTerm, sortBy]);

  const getFavoriteStats = () => {
    if (filteredFavorites.length === 0) return null;
    
    const withEmail = filteredFavorites.filter(contact => contact.email).length;
    const withoutEmail = filteredFavorites.length - withEmail;
    
    return { withEmail, withoutEmail, total: filteredFavorites.length };
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
          <span className="contact-count">{filteredFavorites.length} favorites</span>
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

      {/* Search and Filter Bar */}
      <div className="search-filter-bar">
        <div className="search-box">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            placeholder="Search favorite contacts..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              // Clear saved scroll position when searching (user expects results from top)
              window.sessionStorage.removeItem(SCROLL_POSITION_KEY);
            }}
            className="search-input"
          />
          {searchTerm && (
            <button 
              className="clear-search"
              onClick={() => {
                setSearchTerm('');
                window.sessionStorage.removeItem(SCROLL_POSITION_KEY);
              }}
            >
              ✕
            </button>
          )}
        </div>

        <div className="sort-dropdown">
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              window.sessionStorage.removeItem(SCROLL_POSITION_KEY);
            }}
            className="sort-select"
          >
            <option value="name">Sort by Name</option>
            <option value="email">Sort by Email</option>
            <option value="date">Sort by Date</option>
          </select>
        </div>
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
        {filteredFavorites.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? (
              <>
                <div className="empty-icon">🔍</div>
                <h3>No favorites found</h3>
                <p>No favorite contacts match "{searchTerm}"</p>
                <button 
                  className="clear-search-btn"
                  onClick={() => {
                    setSearchTerm('');
                    window.sessionStorage.removeItem(SCROLL_POSITION_KEY);
                  }}
                >
                  Clear Search
                </button>
              </>
            ) : (
              <>
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
              </>
            )}
          </div>
        ) : (
          <>
            {filteredFavorites.map(contact => (
              <ContactCardWithMessagePreview
                key={contact.id}
                contact={contact}
                isFavorite={true}
                onToggleFavorite={onToggleFavorite}
                onViewContact={handleContactClickWithScroll} // Save scroll before navigation
                onMessageClick={onContactClick}
                showHeart={true}
                variant="default"
              />
            ))}
            
            {/* Quick Stats Footer */}
            <div className="favorites-footer">
              <p>
                {searchTerm ? (
                  `Showing ${filteredFavorites.length} of ${favorites.length} favorite contacts`
                ) : (
                  favorites.length === 1 
                    ? 'You have 1 favorite contact' 
                    : `You have ${favorites.length} favorite contacts`
                )}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Favourites;