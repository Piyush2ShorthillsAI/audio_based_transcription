import React, { useRef, useEffect, useState, useMemo } from 'react';
import ContactCardWithMessagePreview from './ContactCardWithMessagePreview';
import './ContactsList.css';

const RecentContacts = ({ 
  recentContacts, 
  favorites, 
  onToggleFavorite, 
  onClearRecent,
  onContactClick
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name'); // 'name', 'email', 'date'
  const [isRestoringScroll, setIsRestoringScroll] = useState(false);
  const contactsListRef = useRef(null);
  const scrollTimeoutRef = useRef(null);
  const SCROLL_POSITION_KEY = 'recentContacts_scrollPosition';
  const formatTimestamp = (timestamp) => {
    const accessTime = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    
    const timeString = accessTime.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    
    // Check if it's today
    if (accessTime.toDateString() === today.toDateString()) {
      return `Today at ${timeString}`;
    }
    
    // Check if it's yesterday
    if (accessTime.toDateString() === yesterday.toDateString()) {
      return `Yesterday at ${timeString}`;
    }
    
    // For older dates, show full date
    const dateString = accessTime.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: accessTime.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
    });
    
    return `${dateString} at ${timeString}`;
  };

  // Save scroll position 
  const saveScrollPosition = () => {
    if (contactsListRef.current && !isRestoringScroll) {
      const scrollTop = contactsListRef.current.scrollTop;
      window.sessionStorage.setItem(SCROLL_POSITION_KEY, scrollTop.toString());
      console.log('💾 SAVED recent scroll:', scrollTop);
    }
  };

  // Contact click handler
  const handleContactClickWithScroll = (contact) => {
    console.log('🔥 RECENT CONTACT CLICKED - saving scroll...');
    if (contactsListRef.current) {
      const currentScroll = contactsListRef.current.scrollTop;
      window.sessionStorage.setItem(SCROLL_POSITION_KEY, currentScroll.toString());
      console.log('🔥 RECENT: Saved scroll position:', currentScroll);
    }
    if (onContactClick) {
      onContactClick(contact);
    }
  };

  // SCROLL PRESERVATION: Restore scroll position
  useEffect(() => {
    if (!recentContacts || recentContacts.length === 0) return;
    
    const savedScrollPosition = window.sessionStorage.getItem(SCROLL_POSITION_KEY);
    console.log('🔍 RECENT: Checking for saved scroll:', savedScrollPosition);
    
    if (savedScrollPosition && contactsListRef.current) {
      const scrollTop = parseInt(savedScrollPosition, 10);
      setIsRestoringScroll(true);
      
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
                  if (contactsListRef.current) {
          contactsListRef.current.scrollTop = scrollTop;
          console.log('📍 RECENT: Restored scroll to:', scrollTop);
          setTimeout(() => setIsRestoringScroll(false), 100);
        }
        });
      });
    }
  }, [recentContacts?.length]);

  // SCROLL PRESERVATION: Scroll event handler
  useEffect(() => {
    const contactsList = contactsListRef.current;
    if (!contactsList) return;
    
    const handleScroll = () => {
      const scrollTop = contactsList.scrollTop;
      
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      scrollTimeoutRef.current = setTimeout(() => {
        saveScrollPosition();
      }, 200);
    };
    
    contactsList.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      contactsList.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // SCROLL PRESERVATION: Save on unmount
  useEffect(() => {
    return () => {
      saveScrollPosition();
    };
  }, []);

  // Filter, sort and limit contacts based on search term and sort option
  const displayedContacts = useMemo(() => {
    if (!recentContacts) return [];
    
    let filtered = recentContacts;
    
    // Apply search filter if search term exists
    if (searchTerm.trim()) {
      filtered = recentContacts.filter(item =>
        item.contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.contact.email && item.contact.email.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    // Apply sorting
    const sorted = filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.contact.name.localeCompare(b.contact.name);
        case 'email':
          return (a.contact.email || '').localeCompare(b.contact.email || '');
        case 'date':
          return new Date(b.accessedAt) - new Date(a.accessedAt); // Most recent first
        default:
          return 0;
      }
    });
    
    // Always limit to exactly 10 most recent contacts
    return sorted.slice(0, 10);
  }, [recentContacts, searchTerm, sortBy]);

  return (
    <div className="contacts-container">
      {/* Header */}
      <div className="contacts-header">
        <div className="header-info">
          <h2>Recent Contacts</h2>
          <span className="contact-count">
            {displayedContacts.length} contacts
          </span>
        </div>
        {displayedContacts.length > 0 && (
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

      {/* Search and Filter Bar */}
      <div className="search-filter-bar">
        <div className="search-box">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            placeholder="Search recent contacts..."
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

      {/* Info Banner */}
      <div className="info-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 6v6l4 2"></path>
        </svg>
        <span>
          Contacts you've recently viewed will appear here 
          {recentContacts && recentContacts.length > 0 && 
            ` (showing at most 10 recents)`
          }
        </span>
      </div>

      {/* Recent Contacts List */}
      <div className="contacts-list" style={{maxHeight: '650px', overflowY: 'auto', paddingBottom: '32px'}} ref={contactsListRef}>
        {displayedContacts.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? (
              <>
                <div className="empty-icon">🔍</div>
                <h3>No contacts found</h3>
                <p>No recent contacts match "{searchTerm}"</p>
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
                <div className="empty-icon">⏰</div>
                <h3>No recent contacts</h3>
                <p>Contacts you view will appear here for quick access</p>
              </>
            )}
          </div>
        ) : (
          displayedContacts.map(item => (
            <div key={`${item.contact.id}-${item.accessedAt}`} className="recent-contact-wrapper">
              <ContactCardWithMessagePreview
                contact={item.contact}
                isFavorite={favorites.some(fav => fav.id === item.contact.id)}
                onToggleFavorite={onToggleFavorite}
                onViewContact={handleContactClickWithScroll} // Save scroll before navigation
                onMessageClick={onContactClick}
                showHeart={true}
                variant="default"
              />
              <div className="access-time">
                {formatTimestamp(item.accessedAt)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecentContacts;