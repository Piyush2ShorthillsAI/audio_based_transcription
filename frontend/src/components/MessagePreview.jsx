import React, { useState, useEffect } from 'react';
import AudioRecorderCompact from './AudioRecorderCompact';
import { useAuth } from '../authservice/AuthService';
import './MessagePreview.css';

const MessagePreview = ({ contact, isOpen, onClose }) => {
  const [actionAudioList, setActionAudioList] = useState([]);
  const [contextAudioList, setContextAudioList] = useState([]);
  const [selectedActionAudio, setSelectedActionAudio] = useState(null);
  const [selectedContextAudio, setSelectedContextAudio] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedEmail, setGeneratedEmail] = useState(null);
  const [emailStatus, setEmailStatus] = useState('draft'); // draft, approved, rejected
  const [isLoadingAudios, setIsLoadingAudios] = useState(false);
  const { user, token } = useAuth();

  // Reset state when modal opens/closes and fetch audio lists
  useEffect(() => {
    if (isOpen) {
      setSelectedActionAudio(null);
      setSelectedContextAudio(null);
      setGeneratedEmail(null);
      setEmailStatus('draft');
      setIsProcessing(false);
      fetchAudioLists();
    } else {
      // Clear lists when closing to avoid stale data
      setActionAudioList([]);
      setContextAudioList([]);
    }
  }, [isOpen, contact?.id]);

  // Debug generatedEmail content
  useEffect(() => {
    if (generatedEmail) {
      console.log('🔍 Generated email raw response:', generatedEmail);
      console.log('📧 Response type:', typeof generatedEmail);
      console.log('📧 Response length:', generatedEmail?.length);
    }
  }, [generatedEmail]);

  // Fetch audio lists for both action and context
  const fetchAudioLists = async () => {
    if (!contact?.id) return;
    
    setIsLoadingAudios(true);
    try {
      const [actionResponse, contextResponse] = await Promise.all([
        fetch(`http://localhost:8000/contacts/${contact.id}/audio?audio_type=action`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`http://localhost:8000/contacts/${contact.id}/audio?audio_type=context`, {
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

  const generateMessage = async () => {
    if (!selectedActionAudio || !selectedContextAudio) {
      alert('Please select both Action and Context audio before generating message.');
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
          contact_id: contact.id,
          recipient_name: contact.name,
          recipient_email: contact.email
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
    
    try {
      // Save to recents
      const response = await fetch(`http://localhost:8000/recents/${contact.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (response.ok) {
        console.log('Contact added to recents');
      }

      // Copy email to clipboard
      if (generatedEmail) {
        await navigator.clipboard.writeText(generatedEmail);
        alert('Email content copied to clipboard!');
      }

    } catch (error) {
      console.error('Error approving email:', error);
    }
  };

  const handleReject = () => {
    setEmailStatus('rejected');
    setGeneratedEmail(null);
  };

  if (!isOpen) return null;

  return (
    <div className="message-preview-overlay" onClick={onClose}>
      <div className="message-preview-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="message-preview-header">
          <div className="preview-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
          </div>
          <div>
            <h2>Message Preview</h2>
            <p>Executive message review & approval</p>
          </div>
          <div className="status-badge">
            <span className={`status ${emailStatus}`}>{emailStatus}</span>
          </div>
          <button className="close-button" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Email Preview Section */}
        {generatedEmail && (
          <div className="email-preview-section">
            <div className="email-content">
              <div className="email-raw-response">
                <pre>{generatedEmail}</pre>
              </div>
            </div>

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
              <span>Action</span>
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
                      onClick={() => setSelectedActionAudio(audio)}
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
              <span>Context</span>
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
                      onClick={() => setSelectedContextAudio(audio)}
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
                  ))}
                </>
              ) : (
                <div className="no-audios">No context audios recorded yet</div>
              )}
            </div>
          </div>
        </div>

        {/* Instructions */}
        {!generatedEmail && (
          <div className="instructions">
            <h4>Recording Instructions:</h4>
            <div className="instruction-list">
              <div className="instruction-item">
                <strong>Action:</strong> Record specific tasks, requests, or actions needed
              </div>
              <div className="instruction-item">
                <strong>Context:</strong> Record background information, details, or additional context
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessagePreview;