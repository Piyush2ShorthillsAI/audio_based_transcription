import React, { useState, useMemo, useEffect, useRef } from 'react';
import ContactCardWithMessagePreview from './ContactCardWithMessagePreview';
import './ContactsList.css';

const AllContacts = React.memo(({ 
  contacts, 
  favorites, 
  onToggleFavorite, 
  onContactClick,
  loading 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name'); // 'name', 'email', 'date'
  const [isRestoringScroll, setIsRestoringScroll] = useState(false);
  const contactsListRef = useRef(null);
  const scrollTimeoutRef = useRef(null);
  const SCROLL_POSITION_KEY = 'allContacts_scrollPosition';

  // Optimize favorites lookup with a Set for O(1) performance
  const favoritesSet = useMemo(() => {
    return new Set(favorites.map(fav => fav.id));
  }, [favorites]);

  const filteredAndSortedContacts = useMemo(() => {
    let filtered = contacts.filter(contact =>
      contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (contact.email && contact.email.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'email':
          return (a.email || '').localeCompare(b.email || '');
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at);
        default:
          return 0;
      }
    });
  }, [contacts, searchTerm, sortBy]);

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

  // DEBUGGING: Restore scroll position
  useEffect(() => {
    console.log('🚀 COMPONENT MOUNTED/UPDATED - Loading:', loading, 'Contacts:', contacts.length);
    
    if (loading || contacts.length === 0) {
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
  }, [loading, contacts.length]);

  // SIMPLIFIED: Scroll event handler with throttling
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

  if (loading) {
    return (
      <div className="contacts-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading contacts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="contacts-container">
      {/* Header */}
      <div className="contacts-header">
        <div className="header-info">
          <h2>All Contacts</h2>
          <span className="contact-count">{filteredAndSortedContacts.length} contacts</span>
        </div>
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
            placeholder="Search contacts..."
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

      {/* Contacts List */}
      <div className="contacts-list" ref={contactsListRef}>
        {filteredAndSortedContacts.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? (
              <>
                <div className="empty-icon">🔍</div>
                <h3>No contacts found</h3>
                <p>Try adjusting your search terms</p>
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
                <div className="empty-icon">📱</div>
                <h3>No contacts yet</h3>
                <p>Your contacts will appear here once added</p>
              </>
            )}
          </div>
        ) : (
          filteredAndSortedContacts.map(contact => (
            <ContactCardWithMessagePreview
              key={contact.id}
              contact={contact}
              isFavorite={favoritesSet.has(contact.id)}
              onToggleFavorite={onToggleFavorite}
              onViewContact={handleContactClickWithScroll}
              showHeart={true}
              variant="default"
            />
          ))
        )}
      </div>
    </div>
  );
});

AllContacts.displayName = 'AllContacts';

export default AllContacts;