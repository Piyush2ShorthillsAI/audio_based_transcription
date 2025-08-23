import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../authservice/AuthService';
import './AudioRecorder.css';

const AudioRecorderCompact = React.memo(({ 
  contactId,
  audioType,
  onAudioSaved,
  onRecordingStart,
  onRecordingStop,
  maxDuration = 300, // 5 minutes default
  format = 'audio/mp3',
  variant = 'compact'
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { token } = useAuth();

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // Save audio to backend
  const saveAudio = async () => {
    if (!recordedBlob || !contactId || !audioType) {
      setError('Missing required data to save audio');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', recordedBlob, `${audioType}-audio.webm`);
      formData.append('title', `${audioType.charAt(0).toUpperCase() + audioType.slice(1)} Audio`);
      formData.append('contact_id', contactId);
      formData.append('audio_type', audioType);

      const response = await fetch('http://localhost:8000/audio/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to save audio');
      }

      const result = await response.json();
      console.log('Audio saved successfully:', result.message);
      
      // Clear the recorded blob after successful save
      setRecordedBlob(null);
      setRecordingTime(0);
      
      // Notify parent component
      if (onAudioSaved) {
        onAudioSaved(result);
      }

    } catch (error) {
      console.error('Error saving audio:', error);
      setError('Failed to save audio. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Audio level visualization
  const updateAudioLevel = useCallback(() => {
    if (analyserRef.current && isRecording && !isPaused) {
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      analyserRef.current.getByteFrequencyData(dataArray);
      
      const average = dataArray.reduce((a, b) => a + b) / bufferLength;
      setAudioLevel(Math.min(100, (average / 255) * 100));
      
      animationRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [isRecording, isPaused]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;

      // Set up audio level monitoring
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      // Set up MediaRecorder - try MP3 first, then fallback to WebM
      let mimeType;
      if (MediaRecorder.isTypeSupported('audio/mp3')) {
        mimeType = 'audio/mp3';
      } else if (MediaRecorder.isTypeSupported('audio/mpeg')) {
        mimeType = 'audio/mpeg';
      } else if (MediaRecorder.isTypeSupported(format)) {
        mimeType = format;
      } else {
        mimeType = 'audio/webm'; // Last resort
      }
      
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        setRecordedBlob(blob);
      };

      // Start recording
      mediaRecorderRef.current.start(100);
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          if (newTime >= maxDuration) {
            stopRecording();
            return maxDuration;
          }
          return newTime;
        });
      }, 1000);

      // Start audio level monitoring
      updateAudioLevel();

      if (onRecordingStart) {
        onRecordingStart();
      }

    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError(getMicrophoneErrorMessage(err));
      cleanup();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      setAudioLevel(0);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      
      cleanup();

      if (onRecordingStop) {
        onRecordingStop(recordingTime);
      }
    }
  };

  const deleteRecording = () => {
    setRecordedBlob(null);
    setRecordingTime(0);
    setError(null);
  };

  const getMicrophoneErrorMessage = (error) => {
    switch (error.name) {
      case 'NotAllowedError':
        return 'Microphone access denied. Please allow microphone permissions.';
      case 'NotFoundError':
        return 'No microphone found. Please connect a microphone.';
      case 'NotSupportedError':
        return 'Audio recording is not supported in this browser.';
      default:
        return `Microphone error: ${error.message}`;
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`audio-recorder ${variant}`}>
      {error && (
        <div className="audio-recorder-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <span>{error}</span>
        </div>
      )}

      <div className="recording-controls">
        {!isRecording && !recordedBlob && (
          <button 
            className="record-button start compact" 
            onClick={startRecording}
            disabled={!!error}
            title="Start recording"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="8"></circle>
            </svg>
          </button>
        )}

        {isRecording && (
          <button 
            className="record-button stop compact" 
            onClick={stopRecording}
            title="Stop recording"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <rect x="8" y="8" width="8" height="8" rx="1"></rect>
            </svg>
          </button>
        )}
      </div>

      {(isRecording || recordedBlob) && (
        <div className="recording-info">
          <div className="time-display compact">
            <span className="current-time">{formatTime(recordingTime)}</span>
          </div>

          {isRecording && (
            <div className="audio-visualizer compact">
              <div className="wave-container compact">
                {[...Array(8)].map((_, i) => (
                  <div 
                    key={i}
                    className="wave-bar"
                    style={{
                      height: `${Math.random() * audioLevel + 20}%`,
                      animationDelay: `${i * 0.15}s`,
                    }}
                  ></div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {recordedBlob && (
        <div className="playback-controls compact">
          <audio controls>
            <source src={URL.createObjectURL(recordedBlob)} />
            Your browser does not support the audio element.
          </audio>
          
          <div className="action-buttons">
            <button 
              className="action-button save compact"
              onClick={saveAudio}
              disabled={isSaving || !contactId}
              title={!contactId ? "Contact ID required" : "Save recording"}
            >
              {isSaving ? (
                <div className="spinner-small"></div>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>
                </svg>
              )}
            </button>
            
            <button 
              className="action-button delete compact"
              onClick={deleteRecording}
              disabled={isSaving}
              title="Delete recording"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3,6 5,6 21,6"></polyline>
                <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6"></path>
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
});

AudioRecorderCompact.displayName = 'AudioRecorderCompact';

export default AudioRecorderCompact;