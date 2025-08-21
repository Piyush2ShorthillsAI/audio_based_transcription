import React, { useState, useMemo } from 'react';
import ContactCard from './ContactCard';
import './ContactsList.css';

const AllContacts = ({ 
  contacts, 
  favorites, 
  onToggleFavorite, 
  onContactClick,
  loading 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name'); // 'name', 'email', 'date'

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
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button 
              className="clear-search"
              onClick={() => setSearchTerm('')}
            >
              ✕
            </button>
          )}
        </div>

        <div className="sort-dropdown">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="name">Sort by Name</option>
            <option value="email">Sort by Email</option>
            <option value="date">Sort by Date</option>
          </select>
        </div>
      </div>

      {/* Contacts List */}
      <div className="contacts-list">
        {filteredAndSortedContacts.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? (
              <>
                <div className="empty-icon">🔍</div>
                <h3>No contacts found</h3>
                <p>Try adjusting your search terms</p>
                <button 
                  className="clear-search-btn"
                  onClick={() => setSearchTerm('')}
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
            <ContactCard
              key={contact.id}
              contact={contact}
              isFavorite={favorites.some(fav => fav.id === contact.id)}
              onToggleFavorite={onToggleFavorite}
              onViewContact={onContactClick}
              showHeart={true}
              variant="default"
            />
          ))
        )}
      </div>
    </div>
  );
};

export default AllContacts;