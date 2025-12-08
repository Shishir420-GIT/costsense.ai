import React, { useState, useEffect } from 'react';
import './AIProviderToggle.css';
import type { Provider, AIStatus } from '../types/ai';

interface Props {
  currentProvider: Provider;
  onProviderChange: (provider: Provider) => void;
  disabled?: boolean;
}

const AIProviderToggle: React.FC<Props> = ({ 
  currentProvider, 
  onProviderChange, 
  disabled = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const providers = [
    { 
      key: 'openai' as Provider, 
      name: 'OpenAI', 
      icon: '🤖',
      description: 'GPT-4 Turbo'
    },
    { 
      key: 'gemini' as Provider, 
      name: 'Gemini', 
      icon: '✨',
      description: 'Google AI'
    }
  ];

  const currentProviderInfo = providers.find(p => p.key === currentProvider);

  useEffect(() => {
    fetchAIStatus();
  }, []);

  const fetchAIStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chat/status');
      if (response.ok) {
        const status = await response.json();
        setAIStatus(status);
      }
    } catch (error) {
      console.warn('Could not fetch AI status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSelect = (provider: Provider) => {
    if (!disabled && aiStatus?.available.includes(provider)) {
      onProviderChange(provider);
      setIsOpen(false);
    }
  };

  const isProviderAvailable = (provider: Provider) => {
    return aiStatus?.available.includes(provider) ?? true;
  };

  const getProviderStatus = (provider: Provider) => {
    return aiStatus?.providers[provider];
  };

  return (
    <div className="ai-provider-toggle">
      {/* Mobile: Dropdown */}
      <div className="ai-toggle-mobile">
        <button
          className={`ai-toggle-button ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          aria-label="Select AI Provider"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
        >
          <div className="ai-toggle-current">
            <span className="ai-toggle-icon" role="img" aria-hidden="true">
              {currentProviderInfo?.icon}
            </span>
            <div className="ai-toggle-text">
              <div className="ai-toggle-name">{currentProviderInfo?.name}</div>
              <div className="ai-toggle-desc">{currentProviderInfo?.description}</div>
            </div>
          </div>
          <svg 
            className="ai-toggle-chevron" 
            width="12" 
            height="12" 
            viewBox="0 0 12 12"
            aria-hidden="true"
          >
            <path 
              d="M2.5 4.5L6 8L9.5 4.5" 
              stroke="currentColor" 
              strokeWidth="1.5" 
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        {isOpen && (
          <div className="ai-toggle-dropdown" role="listbox">
            {providers.map((provider) => {
              const status = getProviderStatus(provider.key);
              const available = isProviderAvailable(provider.key);
              
              return (
                <button
                  key={provider.key}
                  className={`ai-toggle-option ${
                    currentProvider === provider.key ? 'selected' : ''
                  } ${!available ? 'unavailable' : ''}`}
                  onClick={() => handleProviderSelect(provider.key)}
                  disabled={!available}
                  role="option"
                  aria-selected={currentProvider === provider.key}
                >
                  <span className="ai-toggle-icon" role="img" aria-hidden="true">
                    {provider.icon}
                  </span>
                  <div className="ai-toggle-text">
                    <div className="ai-toggle-name">{provider.name}</div>
                    <div className="ai-toggle-desc">
                      {status?.configured === false 
                        ? 'Not configured' 
                        : provider.description
                      }
                    </div>
                  </div>
                  {!available && (
                    <div className="ai-toggle-status-badge unavailable" title="Not available">
                      ⚠️
                    </div>
                  )}
                  {currentProvider === provider.key && (
                    <div className="ai-toggle-status-badge selected" title="Selected">
                      ✓
                    </div>
                  )}
                </button>
              );
            })}
            
            {loading && (
              <div className="ai-toggle-loading">
                <div className="ai-toggle-spinner"></div>
                Checking status...
              </div>
            )}
          </div>
        )}
      </div>

      {/* Desktop: Toggle buttons */}
      <div className="ai-toggle-desktop">
        <div className="ai-toggle-group" role="radiogroup" aria-label="AI Provider Selection">
          {providers.map((provider) => {
            const available = isProviderAvailable(provider.key);
            // const status = getProviderStatus(provider.key); // Remove if not used
            
            return (
              <button
                key={provider.key}
                className={`ai-toggle-tab ${
                  currentProvider === provider.key ? 'active' : ''
                } ${!available ? 'unavailable' : ''} ${disabled ? 'disabled' : ''}`}
                onClick={() => handleProviderSelect(provider.key)}
                disabled={disabled || !available}
                role="radio"
                aria-checked={currentProvider === provider.key}
                title={
                  !available 
                    ? `${provider.name} is not available` 
                    : `Switch to ${provider.name}`
                }
              >
                <span className="ai-toggle-icon" role="img" aria-hidden="true">
                  {provider.icon}
                </span>
                <span className="ai-toggle-label">{provider.name}</span>
                {!available && (
                  <span className="ai-toggle-warning" aria-label="Unavailable">⚠️</span>
                )}
              </button>
            );
          })}
        </div>
        
        {loading && (
          <div className="ai-toggle-status">
            <div className="ai-toggle-spinner-small"></div>
          </div>
        )}
      </div>

      {/* Click outside to close dropdown */}
      {isOpen && (
        <div 
          className="ai-toggle-overlay" 
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default AIProviderToggle;