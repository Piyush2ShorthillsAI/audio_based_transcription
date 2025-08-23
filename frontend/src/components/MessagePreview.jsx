import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AudioRecorderCompact from './AudioRecorderCompact';
import { useAuth } from '../authservice/AuthService';
import './MessagePreview.css';

const MessagePreview = ({ contact: propContact, isOpen, onClose, isFullPage = false }) => {
  const { contactId } = useParams();
  const navigate = useNavigate();
  const [contact, setContact] = useState(propContact);
  const [isLoadingContact, setIsLoadingContact] = useState(false);
  const [actionAudioList, setActionAudioList] = useState([]);
  const [contextAudioList, setContextAudioList] = useState([]);
  const [selectedActionAudio, setSelectedActionAudio] = useState(null);
  const [selectedContextAudio, setSelectedContextAudio] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedEmail, setGeneratedEmail] = useState(null);
  const [emailStatus, setEmailStatus] = useState('draft'); // draft, approved, rejected
  const [isLoadingAudios, setIsLoadingAudios] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedEmail, setEditedEmail] = useState('');
  const [storedMessages, setStoredMessages] = useState([]);
  const [isLoadingStored, setIsLoadingStored] = useState(false);
  const { user, token } = useAuth();

  // Fetch contact when in full page mode
  useEffect(() => {
    if (isFullPage && contactId && !propContact) {
      fetchContactDetails();
    }
  }, [isFullPage, contactId, propContact]);

  // Reset state when modal opens/closes and fetch audio lists
  useEffect(() => {
    const shouldLoad = isFullPage || isOpen;
    if (shouldLoad && (contact?.id || contactId)) {
      setSelectedActionAudio(null);
      setSelectedContextAudio(null);
      setGeneratedEmail(null);
      setEmailStatus('draft');
      setIsProcessing(false);
      setIsEditing(false);
      setEditedEmail('');
      fetchAudioLists();
      fetchStoredMessages();
    } else if (!shouldLoad) {
      // Clear lists when closing to avoid stale data
      setActionAudioList([]);
      setContextAudioList([]);
    }
  }, [isOpen, isFullPage, contact?.id, contactId]);

  // Debug generatedEmail content and initialize edited version
  useEffect(() => {
    if (generatedEmail) {
      console.log('🔍 Generated email raw response:', generatedEmail);
      console.log('📧 Response type:', typeof generatedEmail);
      console.log('📧 Response length:', generatedEmail?.length);
      setEditedEmail(generatedEmail); // Initialize edited version
    }
  }, [generatedEmail]);

  // Fetch contact details when in full page mode
  const fetchContactDetails = async () => {
    if (!contactId) return;
    
    try {
      setIsLoadingContact(true);
      const response = await fetch(`http://localhost:8000/persons/${contactId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch contact details');
      }

      const contactData = await response.json();
      setContact(contactData);
    } catch (error) {
      console.error('Error fetching contact:', error);
      alert('Failed to load contact details.');
    } finally {
      setIsLoadingContact(false);
    }
  };

  // Fetch stored/approved messages for this contact
  const fetchStoredMessages = async () => {
    const currentContactId = contact?.id || contactId;
    if (!currentContactId) return;
    
    console.log('🔍 Fetching stored messages for contact:', currentContactId);
    console.log('🔑 Using token:', token ? 'Present' : 'Missing');
    
    try {
      setIsLoadingStored(true);
      const url = `http://localhost:8000/emails/approved?contact_id=${currentContactId}`;
      console.log('📡 Making request to:', url);
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('📊 Response status:', response.status);
      console.log('📊 Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Stored messages data:', data);
        setStoredMessages(data.emails || []);
      } else {
        const errorText = await response.text();
        console.error('❌ API Error:', response.status, errorText);
      }
    } catch (error) {
      console.error('💥 Error fetching stored messages:', error);
    } finally {
      setIsLoadingStored(false);
    }
  };

  // Fetch audio lists for both action and context
  const fetchAudioLists = async () => {
    const currentContactId = contact?.id || contactId;
    if (!currentContactId) return;
    
    setIsLoadingAudios(true);
    try {
      const [actionResponse, contextResponse] = await Promise.all([
        fetch(`http://localhost:8000/contacts/${currentContactId}/audio?audio_type=action`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`http://localhost:8000/contacts/${currentContactId}/audio?audio_type=context`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (actionResponse.ok) {
        const actionData = await actionResponse.json();
        setActionAudioList(actionData.recordings || []);
      }

      if (contextResponse.ok) {
        const contextData = await contextResponse.json();
        setContextAudioList(contextData.recordings || []);
      }
    } catch (error) {
      console.error('Error fetching audio lists:', error);
    } finally {
      setIsLoadingAudios(false);
    }
  };

  // Handle audio save completion - refresh the appropriate list
  const handleAudioSaved = (audioType) => {
    console.log(`${audioType} audio saved successfully`);
    fetchAudioLists(); // Refresh both lists
  };

  // Handle action audio selection with toggle
  const handleActionAudioSelect = (audio) => {
    if (selectedActionAudio?.id === audio.id) {
      // If clicking on already selected audio, deselect it
      setSelectedActionAudio(null);
    } else {
      // Select the new audio
      setSelectedActionAudio(audio);
    }
  };

  // Handle context audio selection with toggle
  const handleContextAudioSelect = (audio) => {
    if (selectedContextAudio?.id === audio.id) {
      // If clicking on already selected audio, deselect it
      setSelectedContextAudio(null);
    } else {
      // Select the new audio
      setSelectedContextAudio(audio);
    }
  };

  const generateMessage = async () => {
    if (!selectedActionAudio || !selectedContextAudio) {
      alert('Please select both Action and Context audio before generating message.');
      return;
    }

    const currentContactId = contact?.id || contactId;
    if (!currentContactId) {
      alert('Contact information not available.');
      return;
    }

    setIsProcessing(true);
    setEmailStatus('draft');

    try {
      // Generate email from selected audios directly (no upload needed)
      const generateResponse = await fetch('http://localhost:8000/audio/generate-dual-email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action_recording_id: selectedActionAudio.id,
          context_recording_id: selectedContextAudio.id,
          contact_id: currentContactId,
          recipient_name: contact?.name || 'Contact',
          recipient_email: contact?.email || ''
        })
      });

      if (!generateResponse.ok) {
        throw new Error('Failed to generate email');
      }

      const emailResult = await generateResponse.json();
      console.log('📧 Generated email result:', emailResult);
      setGeneratedEmail(emailResult.email);

    } catch (error) {
      console.error('Error generating message:', error);
      alert('Failed to generate message. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApprove = async () => {
    setEmailStatus('approved');
    
    const currentContactId = contact?.id || contactId;
    if (!currentContactId) {
      alert('Contact information not available.');
      return;
    }
    
    try {
      const emailToCopy = editedEmail || generatedEmail;
      
      // Save approved email to database
      await fetch('http://localhost:8000/emails/approve', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_id: currentContactId,
          recording_id: selectedActionAudio?.id || selectedContextAudio?.id,
          email_content: emailToCopy
        })
      });

      // Save to recents
      const response = await fetch(`http://localhost:8000/recents/${currentContactId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (response.ok) {
        console.log('Contact added to recents');
      }

      // Copy email to clipboard
      if (emailToCopy) {
        await navigator.clipboard.writeText(emailToCopy);
        alert('Email approved and saved!');
      }

      // Refresh stored messages list
      fetchStoredMessages();

      // Clear the generated email section after successful approval
      setGeneratedEmail(null);
      setEmailStatus('draft');
      setEditedEmail('');
      setIsEditing(false);
      
      // Clear selected audios so user can start fresh
      setSelectedActionAudio(null);
      setSelectedContextAudio(null);

    } catch (error) {
      console.error('Error approving email:', error);
      alert('Error saving email. Please try again.');
    }
  };

  const handleReject = () => {
    setEmailStatus('rejected');
    setGeneratedEmail(null);
    setEditedEmail('');
    setIsEditing(false);
    
    // Clear selected audios so user can start fresh
    setSelectedActionAudio(null);
    setSelectedContextAudio(null);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    setGeneratedEmail(editedEmail);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedEmail(generatedEmail); // Reset to original
    setIsEditing(false);
  };

  // Show component if it's full page mode OR if modal is open
  if (!isFullPage && !isOpen) return null;

  // Show loading state when fetching contact in full page mode
  if (isFullPage && isLoadingContact) {
    return (
      <div className="message-preview-page loading">
        <div className="loading-spinner"></div>
        <p>Loading contact details...</p>
      </div>
    );
  }

  // Show error if contact not found in full page mode
  if (isFullPage && !contact && !isLoadingContact) {
    return (
      <div className="message-preview-page error">
        <div className="error-message">
          <h2>Contact not found</h2>
          <p>The contact you're looking for could not be found.</p>
          <button onClick={() => navigate('/')} className="close-button-error">Go Back</button>
        </div>
      </div>
    );
  }

  const handleClose = () => {
    if (isFullPage) {
      navigate('/');
    } else {
      onClose();
    }
  };

  const content = (
    <>
        {/* Header */}
        <div className="message-preview-header">
          <div className="preview-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
          </div>
          <div>
            <h2>Voice Message Generator</h2>
            <p>AI-powered email composition from voice recordings</p>
          </div>
          <div className="status-badge">
            <span className={`status ${emailStatus}`}>{emailStatus}</span>
          </div>
          <button className="close-button" onClick={handleClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Email Preview Section */}
        {generatedEmail && (
          <div className="email-preview-section">
            <div className="email-header-section">
              <div className="email-section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                  <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
                <h3>Generated Email Message</h3>
                <p>AI-composed email based on your voice recordings</p>
              </div>
            </div>
            <div className="email-content">
              {isEditing ? (
                <div className="email-edit-mode">
                  <textarea
                    value={editedEmail}
                    onChange={(e) => setEditedEmail(e.target.value)}
                    className="email-edit-textarea"
                    rows={20}
                    placeholder="Edit your email content here..."
                  />
                  <div className="edit-actions">
                    <button 
                      className="save-edit-button" 
                      onClick={handleSaveEdit}
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 6L9 17l-5-5"></path>
                      </svg>
                      Save Changes
                    </button>
                    <button 
                      className="cancel-edit-button" 
                      onClick={handleCancelEdit}
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="email-raw-response">
                  <pre>{editedEmail || generatedEmail}</pre>
                </div>
              )}
            </div>

            {!isEditing && (
              <div className="email-actions">
                <button 
                  className="reject-button" 
                  onClick={handleReject}
                  disabled={isProcessing}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Reject
                </button>
                <button 
                  className="edit-button" 
                  onClick={handleEdit}
                  disabled={isProcessing}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="m18 2 4 4-14 14H4v-4L18 2z"></path>
                  </svg>
                  Edit
                </button>
                <button 
                  className="approve-button" 
                  onClick={handleApprove}
                  disabled={isProcessing}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 6L9 17l-5-5"></path>
                  </svg>
                  Approve
                </button>
              </div>
            )}
          </div>
        )}

        {/* Contact Info */}
        <div className="contact-info-section">
          <div className="contact-avatar">
            <div className="avatar-circle">
              {contact.name.charAt(0).toUpperCase()}
            </div>
          </div>
          <div className="contact-details">
            <h3>{contact.name}</h3>
            <p>{contact.email}</p>
          </div>
          <button 
            className="generate-button"
            onClick={generateMessage}
            disabled={!selectedActionAudio || !selectedContextAudio || isProcessing}
          >
            {isProcessing ? (
              <>
                <div className="spinner"></div>
                Generating...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
                  <path d="m18 13-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
                  <path d="m2 2 7.586 7.586"></path>
                  <circle cx="11" cy="11" r="2"></circle>
                </svg>
                Generate Message
              </>
            )}
          </button>
        </div>

        {/* Audio Recording Section */}
        <div className="audio-recording-section">
          {/* Action Audio */}
          <div className="audio-column">
            <div className="audio-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
              <div className="header-text">
                <h4>Action Recording</h4>
                <p>Record specific tasks or requests</p>
              </div>
            </div>
            
            <div className="audio-recorder-container">
              <AudioRecorderCompact
                contactId={contact.id}
                audioType="action"
                onAudioSaved={() => handleAudioSaved('action')}
                maxDuration={300} // 5 minutes
                format="audio/webm;codecs=opus"
                variant="compact"
              />
            </div>
            
            {/* Action Audio List */}
            <div className="audio-list">
              {isLoadingAudios ? (
                <div className="loading">Loading audios...</div>
              ) : actionAudioList.length > 0 ? (
                <>
                  <h5>Select Action Audio:</h5>
                  {actionAudioList.map((audio) => (
                    <div 
                      key={audio.id} 
                      className={`audio-item ${selectedActionAudio?.id === audio.id ? 'selected' : ''}`}
                    >
                      <div 
                        className="audio-item-main"
                        onClick={() => handleActionAudioSelect(audio)}
                      >
                        <div className="audio-info">
                          <div className="audio-title">{audio.title}</div>
                          <div className="audio-meta">
                            {new Date(audio.created_at).toLocaleString()} • 
                            {audio.duration ? ` ${Math.round(audio.duration)}s` : ''} • 
                            {audio.file_size ? ` ${(audio.file_size / 1024).toFixed(0)}KB` : ''}
                          </div>
                        </div>
                        {selectedActionAudio?.id === audio.id && (
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 6L9 17l-5-5"></path>
                          </svg>
                        )}
                      </div>
                      
                      {/* Audio Playback Controls */}
                      <div className="audio-playback" onClick={(e) => e.stopPropagation()}>
                        <audio 
                          controls 
                          preload="none"
                          className="audio-player"
                        >
                          <source src={`http://localhost:8000/${audio.file_path}`} type="audio/webm" />
                          <source src={`http://localhost:8000/${audio.file_path}`} type="audio/mp3" />
                          Your browser does not support the audio element.
                        </audio>
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <div className="no-audios">No action audios recorded yet</div>
              )}
            </div>
          </div>

          {/* Context Audio */}
          <div className="audio-column">
            <div className="audio-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
                <path d="M21 12h-6m-6 0H3"></path>
              </svg>
              <div className="header-text">
                <h4>Context Recording</h4>
                <p>Record background information & details</p>
              </div>
            </div>
            
            <div className="audio-recorder-container">
              <AudioRecorderCompact
                contactId={contact.id}
                audioType="context"
                onAudioSaved={() => handleAudioSaved('context')}
                maxDuration={300} // 5 minutes
                format="audio/webm;codecs=opus"
                variant="compact"
              />
            </div>
            
            {/* Context Audio List */}
            <div className="audio-list">
              {isLoadingAudios ? (
                <div className="loading">Loading audios...</div>
              ) : contextAudioList.length > 0 ? (
                <>
                  <h5>Select Context Audio:</h5>
                  {contextAudioList.map((audio) => (
                    <div 
                      key={audio.id} 
                      className={`audio-item ${selectedContextAudio?.id === audio.id ? 'selected' : ''}`}
                    >
                      <div 
                        className="audio-item-main"
                        onClick={() => handleContextAudioSelect(audio)}
                      >
                        <div className="audio-info">
                          <div className="audio-title">{audio.title}</div>
                          <div className="audio-meta">
                            {new Date(audio.created_at).toLocaleString()} • 
                            {audio.duration ? ` ${Math.round(audio.duration)}s` : ''} • 
                            {audio.file_size ? ` ${(audio.file_size / 1024).toFixed(0)}KB` : ''}
                          </div>
                        </div>
                        {selectedContextAudio?.id === audio.id && (
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 6L9 17l-5-5"></path>
                          </svg>
                        )}
                      </div>
                      
                      {/* Audio Playback Controls */}
                      <div className="audio-playback" onClick={(e) => e.stopPropagation()}>
                        <audio 
                          controls 
                          preload="none"
                          className="audio-player"
                        >
                          <source src={`http://localhost:8000/${audio.file_path}`} type="audio/webm" />
                          <source src={`http://localhost:8000/${audio.file_path}`} type="audio/mp3" />
                          Your browser does not support the audio element.
                        </audio>
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <div className="no-audios">No context audios recorded yet</div>
              )}
            </div>
          </div>
        </div>

        {/* Stored Messages Section */}
        <div className="stored-messages-section">
          <div className="stored-messages-header">
            <div className="stored-section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
              <h3>Stored Messages</h3>
              <p>Previously generated and approved emails for this contact</p>
            </div>
          </div>
          
          <div className="stored-messages-content">
            {isLoadingStored ? (
              <div className="loading-stored">
                <div className="spinner"></div>
                <span>Loading stored messages...</span>
              </div>
            ) : storedMessages.length > 0 ? (
              <div className="messages-list">
                {storedMessages.map((message, index) => (
                  <div key={message.id || index} className="stored-message-item">
                    <div className="message-meta">
                      <div className="message-date">
                        {new Date(message.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                      <div className="message-status approved">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20,6 9,17 4,12"></polyline>
                        </svg>
                        Approved
                      </div>
                    </div>
                    <div className="message-content">
                      <pre>{message.email_content}</pre>
                    </div>
                    <div className="message-actions">
                      <button 
                        className="copy-message-button"
                        onClick={() => navigator.clipboard.writeText(message.email_content)}
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
                          <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
                        </svg>
                        Copy
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-stored-messages">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                <h4>No Stored Messages</h4>
                <p>Generate and approve messages to see them stored here</p>
              </div>
            )}
          </div>
        </div>
    </>
  );

  // Return wrapped content based on mode
  if (isFullPage) {
    return (
      <div className="message-preview-page">
        {content}
      </div>
    );
  } else {
    return (
      <div className="message-preview-overlay" onClick={handleClose}>
        <div className="message-preview-modal" onClick={(e) => e.stopPropagation()}>
          {content}
        </div>
      </div>
    );
  }
};

export default MessagePreview;