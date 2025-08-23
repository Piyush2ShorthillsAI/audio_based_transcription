/**
 * Integration Example: How to use MessagePreview with your existing contacts
 * 
 * This example shows how to replace your current ContactCard components
 * with the new ContactCardWithMessagePreview to enable dual audio email generation.
 */

import React, { useState, useEffect } from 'react';
import ContactCardWithMessagePreview from './components/ContactCardWithMessagePreview';
import MessagePreview from './components/MessagePreview';
import { useAuth } from './authservice/AuthService';

// Example: Update your AllContacts.jsx component
const AllContactsWithAudio = () => {
  const [contacts, setContacts] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [showMessagePreview, setShowMessagePreview] = useState(false);
  const { user, token, apiService } = useAuth();

  useEffect(() => {
    if (user && token) {
      loadContacts();
      loadFavorites();
    }
  }, [user, token]);

  const loadContacts = async () => {
    try {
      const data = await apiService.fetchPersons(token);
      setContacts(data);
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const loadFavorites = async () => {
    try {
      const data = await apiService.fetchFavorites(token);
      setFavorites(data);
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  };

  const handleToggleFavorite = async (contact) => {
    try {
      await apiService.toggleFavorite(token, contact.id);
      // Update local state
      const isFavorite = favorites.some(fav => fav.id === contact.id);
      if (isFavorite) {
        setFavorites(prev => prev.filter(fav => fav.id !== contact.id));
      } else {
        setFavorites(prev => [...prev, contact]);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const handleViewContact = async (contact) => {
    // Add to recent contacts
    try {
      await apiService.addToRecents(token, contact.id);
    } catch (error) {
      console.error('Error adding to recents:', error);
    }
  };

  return (
    <div className="all-contacts">
      <div className="contacts-header">
        <h2>All Contacts</h2>
        <p>Generate professional emails from voice messages</p>
      </div>

      <div className="contacts-grid">
        {contacts.map((contact) => (
          <ContactCardWithMessagePreview
            key={contact.id}
            contact={contact}
            isFavorite={favorites.some(fav => fav.id === contact.id)}
            onToggleFavorite={handleToggleFavorite}
            onViewContact={handleViewContact}
          />
        ))}
      </div>

      {contacts.length === 0 && (
        <div className="empty-state">
          <p>No contacts found. Add some contacts to get started!</p>
        </div>
      )}
    </div>
  );
};

// Example: Update your ContactsList.jsx component
const ContactsListWithAudio = ({ contacts, favorites, onToggleFavorite, onViewContact }) => {
  return (
    <div className="contacts-list">
      {contacts.map((contact) => (
        <ContactCardWithMessagePreview
          key={contact.id}
          contact={contact}
          isFavorite={favorites.some(fav => fav.id === contact.id)}
          onToggleFavorite={onToggleFavorite}
          onViewContact={onViewContact}
          variant="list" // Optional: use list variant for different styling
        />
      ))}
    </div>
  );
};

// Example: Integration with your App.jsx
const AppWithAudioFeature = () => {
  const [selectedContact, setSelectedContact] = useState(null);
  const [showMessagePreview, setShowMessagePreview] = useState(false);

  // Handler for when user clicks the message button on a contact
  const handleOpenMessagePreview = (contact) => {
    setSelectedContact(contact);
    setShowMessagePreview(true);
  };

  const handleCloseMessagePreview = () => {
    setSelectedContact(null);
    setShowMessagePreview(false);
  };

  return (
    <div className="app">
      {/* Your existing routes and components */}
      
      {/* Example: In your contacts route */}
      <Routes>
        <Route 
          path="/contacts" 
          element={<AllContactsWithAudio />} 
        />
        {/* Your other routes */}
      </Routes>

      {/* Global Message Preview Modal */}
      {selectedContact && (
        <MessagePreview
          contact={selectedContact}
          isOpen={showMessagePreview}
          onClose={handleCloseMessagePreview}
        />
      )}
    </div>
  );
};

// Example: Custom hook for audio functionality
const useAudioFeature = () => {
  const { token } = useAuth();

  const uploadAndProcessAudio = async (actionAudio, contextAudio, contact) => {
    try {
      // Upload action audio
      const actionFormData = new FormData();
      actionFormData.append('audio', actionAudio, 'action-audio.webm');
      actionFormData.append('title', `Action Audio for ${contact.name}`);
      actionFormData.append('contact_id', contact.id);

      const actionResponse = await fetch('http://localhost:8000/audio/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: actionFormData
      });

      const actionResult = await actionResponse.json();

      // Upload context audio
      const contextFormData = new FormData();
      contextFormData.append('audio', contextAudio, 'context-audio.webm');
      contextFormData.append('title', `Context Audio for ${contact.name}`);
      contextFormData.append('contact_id', contact.id);

      const contextResponse = await fetch('http://localhost:8000/audio/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: contextFormData
      });

      const contextResult = await contextResponse.json();

      // Generate email
      const emailResponse = await fetch('http://localhost:8000/audio/generate-dual-email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action_recording_id: actionResult.recording_id,
          context_recording_id: contextResult.recording_id,
          contact_id: contact.id,
          recipient_name: contact.name,
          recipient_email: contact.email
        })
      });

      const emailResult = await emailResponse.json();
      return emailResult.email;

    } catch (error) {
      console.error('Error processing audio:', error);
      throw error;
    }
  };

  return { uploadAndProcessAudio };
};

// Example: Manual MessagePreview trigger (if you don't want to modify existing ContactCards)
const ManualMessagePreviewExample = () => {
  const [selectedContact, setSelectedContact] = useState(null);
  const [showMessagePreview, setShowMessagePreview] = useState(false);
  const [contacts, setContacts] = useState([]);

  const handleGenerateMessage = (contact) => {
    setSelectedContact(contact);
    setShowMessagePreview(true);
  };

  return (
    <div>
      {/* Your existing contact cards */}
      {contacts.map(contact => (
        <div key={contact.id} className="contact-item">
          <span>{contact.name}</span>
          <button onClick={() => handleGenerateMessage(contact)}>
            🎤 Generate Email
          </button>
        </div>
      ))}

      {/* Message Preview Modal */}
      <MessagePreview
        contact={selectedContact}
        isOpen={showMessagePreview}
        onClose={() => setShowMessagePreview(false)}
      />
    </div>
  );
};

export {
  AllContactsWithAudio,
  ContactsListWithAudio,
  AppWithAudioFeature,
  useAudioFeature,
  ManualMessagePreviewExample
};

/**
 * MIGRATION STEPS:
 * 
 * 1. Import the new components:
 *    import ContactCardWithMessagePreview from './components/ContactCardWithMessagePreview';
 *    import MessagePreview from './components/MessagePreview';
 * 
 * 2. Replace existing ContactCard components:
 *    <ContactCard {...props} />
 *    ↓
 *    <ContactCardWithMessagePreview {...props} />
 * 
 * 3. Set up your environment:
 *    - Configure GEMINI_API_KEY in backend
 *    - Run database setup script
 *    - Start backend server with uvicorn
 * 
 * 4. Test the flow:
 *    - Click on a contact
 *    - Click the purple message button
 *    - Record Action and Context audio
 *    - Click "Generate Message"
 *    - Review and approve the generated email
 * 
 * That's it! Your CRM now supports AI-powered email generation from voice! 🎉
 */