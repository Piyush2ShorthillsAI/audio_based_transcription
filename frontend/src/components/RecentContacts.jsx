import React, { useRef, useEffect, useState } from 'react';
import ContactCardWithMessagePreview from './ContactCardWithMessagePreview';
import './ContactsList.css';

const RecentContacts = ({ 
  recentContacts, 
  favorites, 
  onToggleFavorite, 
  onClearRecent,
  onContactClick
}) => {
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

  // Ensure we always limit to exactly 10 most recent contacts
  const displayedContacts = recentContacts ? recentContacts.slice(0, 10) : [];

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
            <div className="empty-icon">⏰</div>
            <h3>No recent contacts</h3>
            <p>Contacts you view will appear here for quick access</p>
          </div>
        ) : (
          displayedContacts.map(item => (
            <div key={`${item.contact.id}-${item.accessedAt}`} className="recent-contact-wrapper">
              <ContactCardWithMessagePreview
                contact={item.contact}
                isFavorite={favorites.some(fav => fav.id === item.contact.id)}
                onToggleFavorite={onToggleFavorite}
                onViewContact={handleContactClickWithScroll} // Save scroll before navigation
                showHeart={true}
                variant="recent"
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