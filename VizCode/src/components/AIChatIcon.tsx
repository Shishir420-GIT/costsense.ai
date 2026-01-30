import React from 'react';

type Props = { onOpen: () => void };

const AIChatIcon: React.FC<Props> = ({ onOpen }) => {
  return (
    <button
      onClick={onOpen}
      title="AI is here"
      aria-label="Open AI chat"
      style={{
        background: 'transparent',
        border: '0',
        color: '#fff',
        padding: '8px 10px',
        borderRadius: 8,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        fontWeight: 700,
      }}
    >
      {/* simple inline spark/neural icon */}
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <path d="M12 2v4" stroke="#7dd3fc" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 18v4" stroke="#60a5fa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M4.93 4.93l2.83 2.83" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M16.24 16.24l2.83 2.83" stroke="#f472b6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="12" cy="12" r="3" stroke="#c7b8ff" strokeWidth="1.5" fill="#0b1220" />
      </svg>
      <span style={{ color: '#e6eef8', fontSize: 13 }}>AI</span>
    </button>
  );
};

export default AIChatIcon;
