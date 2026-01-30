import React, { useEffect, useRef, useState } from 'react';
import '../styles/ai-chat.css';
import type { Provider, Message } from '../types/ai';

interface Props {
  open: boolean;
  onClose: () => void;
  provider: Provider;
  onDSLGenerated?: (dsl: string, explanation: string) => void;
}

const AIChatWindow: React.FC<Props> = ({ open, onClose, provider, onDSLGenerated }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // persistent position (kept in memory while app runs)
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const [size, setSize] = useState<{ w: number; h: number } | null>(null);
  const draggingRef = useRef(false);
  const dragOffsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const resizingRef = useRef(false);
  const resizeStartRef = useRef<{ x: number; y: number; w: number; h: number } | null>(null);
  const [minimized, setMinimized] = useState(false);
  const minimizedDraggingRef = useRef(false);
  const minimizedDragOffsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const minimizedMovedRef = useRef(false);

  // Handle initial setup and position/size initialization
  useEffect(() => {
    if (open) {
      // initialize position to center if not set
      if (!pos && typeof window !== 'undefined') {
        const defaultW = Math.min(720, Math.floor(window.innerWidth * 0.6));
        const defaultH = Math.min(640, Math.floor(window.innerHeight * 0.6));
        setPos({ x: Math.max(8, Math.floor((window.innerWidth - defaultW) / 2)), y: Math.max(8, Math.floor((window.innerHeight - defaultH) / 2)) });
      }
      if (!size && typeof window !== 'undefined') {
        setSize({ w: Math.min(720, Math.floor(window.innerWidth * 0.6)), h: Math.min(640, Math.floor(window.innerHeight * 0.6)) });
      }
    }
  }, [open, pos, size]);

  // Handle greeting messages and provider changes
  useEffect(() => {
    if (open) {
      const newGreeting = `Hi! I'm VizCode's AI assistant powered by ${provider === 'openai' ? 'OpenAI GPT-4' : 'Google Gemini'}. Describe your cloud architecture and I'll generate the diagram for you!`;
      
      setMessages(m => {
        if (m.length === 0) {
          // First time opening - create initial greeting
          return [{ from: 'ai', text: newGreeting }];
        } else {
          // Update first AI message when provider changes
          const firstAiIndex = m.findIndex(msg => msg.from === 'ai');
          if (firstAiIndex >= 0) {
            const updatedMessages = [...m];
            updatedMessages[firstAiIndex] = { ...m[firstAiIndex], text: newGreeting };
            return updatedMessages;
          }
          // If no AI message found, add greeting at the beginning
          return [{ from: 'ai', text: newGreeting }, ...m];
        }
      });
    }
  }, [open, provider]);

  useEffect(() => {
    const el = containerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, open]);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (resizingRef.current) {
        // resize
        if (!resizeStartRef.current) return;
        const dx = e.clientX - resizeStartRef.current.x;
        const dy = e.clientY - resizeStartRef.current.y;
        const newW = Math.max(300, resizeStartRef.current.w + dx);
        const newH = Math.max(220, resizeStartRef.current.h + dy);
        setSize({ w: Math.min(window.innerWidth - 32, newW), h: Math.min(window.innerHeight - 32, newH) });
        return;
      }
      // window dragging
      if (draggingRef.current) {
        e.preventDefault();
        const x = e.clientX - dragOffsetRef.current.x;
        const y = e.clientY - dragOffsetRef.current.y;
        // clamp to viewport
        const maxX = Math.max(0, window.innerWidth - 200);
        const maxY = Math.max(0, window.innerHeight - 100);
        setPos({ x: Math.max(8, Math.min(maxX, x)), y: Math.max(8, Math.min(maxY, y)) });
        return;
      }
      // minimized dragging
      if (minimizedDraggingRef.current) {
        e.preventDefault();
        const x = e.clientX - minimizedDragOffsetRef.current.x;
        const y = e.clientY - minimizedDragOffsetRef.current.y;
        const maxX = Math.max(0, window.innerWidth - 56);
        const maxY = Math.max(0, window.innerHeight - 56);
        setPos({ x: Math.max(8, Math.min(maxX, x)), y: Math.max(8, Math.min(maxY, y)) });
        minimizedMovedRef.current = true;
        return;
      }
    };
  const onUp = () => { draggingRef.current = false; resizingRef.current = false; resizeStartRef.current = null; minimizedDraggingRef.current = false; };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    return () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
  }, []);

  // touch support
  useEffect(() => {
    const onMove = (e: TouchEvent) => {
      // window drag
      if (draggingRef.current) {
        const t = e.touches[0];
        if (!t) return;
        const x = t.clientX - dragOffsetRef.current.x;
        const y = t.clientY - dragOffsetRef.current.y;
        setPos({ x: Math.max(8, x), y: Math.max(8, y) });
        return;
      }
      // minimized drag
      if (minimizedDraggingRef.current) {
        const t = e.touches[0];
        if (!t) return;
        const x = t.clientX - minimizedDragOffsetRef.current.x;
        const y = t.clientY - minimizedDragOffsetRef.current.y;
        setPos({ x: Math.max(8, x), y: Math.max(8, y) });
        minimizedMovedRef.current = true;
        return;
      }
    };
  const onEnd = () => { draggingRef.current = false; resizingRef.current = false; resizeStartRef.current = null; minimizedDraggingRef.current = false; };
    document.addEventListener('touchmove', onMove);
    document.addEventListener('touchend', onEnd);
    return () => {
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend', onEnd);
    };
  }, []);

  // If not open, nothing to render. When open and minimized=true we render the floating icon.
  if (!open) return null;

  const onHeaderMouseDown = (e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).closest('.ai-chat-window') as HTMLElement | null;
    if (!rect) return;
    const box = rect.getBoundingClientRect();
    draggingRef.current = true;
    dragOffsetRef.current = { x: e.clientX - (pos?.x ?? box.left), y: e.clientY - (pos?.y ?? box.top) };
  };

  const onHeaderTouchStart = (e: React.TouchEvent) => {
    const t = e.touches[0];
    const rect = (e.currentTarget as HTMLElement).closest('.ai-chat-window') as HTMLElement | null;
    if (!rect || !t) return;
    const box = rect.getBoundingClientRect();
    draggingRef.current = true;
    dragOffsetRef.current = { x: t.clientX - (pos?.x ?? box.left), y: t.clientY - (pos?.y ?? box.top) };
  };

  // Minimize action is handled inline where the button is used.


  const send = async () => {
    const txt = input.trim();
    if (!txt || isLoading) return;
    
    // Clear any previous errors
    setError(null);
    
    // Add user message
    const userMessage: Message = { from: 'user', text: txt, timestamp: new Date().toISOString() };
    setMessages(m => [...m, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001';
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          message: txt, 
          provider,
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Network error' }));
        throw new Error(errorData.error || errorData.fallbackMessage || `Server error (${response.status})`);
      }

      const data = await response.json();
      
      if (!data.reply) {
        throw new Error('Invalid response from server');
      }

      // Add AI response
      const aiMessage: Message = {
        from: 'ai',
        text: data.reply,
        dsl: data.dsl,
        timestamp: new Date().toISOString()
      };
      
      setMessages(m => [...m, aiMessage]);
      
      // If DSL was generated, notify parent component
      if (data.dsl && onDSLGenerated) {
        onDSLGenerated(data.dsl, data.reply);
      }

    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      
      // Add error message to chat
      const errorMsg: Message = {
        from: 'ai',
        text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        error: true,
        timestamp: new Date().toISOString()
      };
      setMessages(m => [...m, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const stylePos: React.CSSProperties = pos ? { position: 'absolute', left: pos.x, top: pos.y } : { position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)' };

  return (
    <div
      className="ai-chat-modal"
      style={{
        pointerEvents: minimized ? 'none' : 'auto',
        background: minimized ? 'transparent' : 'rgba(2,6,23,0.6)'
      }}
    >
      {minimized ? (
        // When minimized, we allow pointer events to pass through the modal overlay so the user can continue working on the diagram.
  <div
          className="ai-chat-minimized"
          style={{ left: pos ? pos.x : 20, top: pos ? pos.y : 20 }}
          role="button"
          aria-label="Open chat"
          onMouseDown={(e) => {
            minimizedDraggingRef.current = true;
            minimizedDragOffsetRef.current = { x: e.clientX - (pos?.x ?? 20), y: e.clientY - (pos?.y ?? 20) };
            minimizedMovedRef.current = false;
          }}
          onTouchStart={(e) => {
            const t = e.touches[0];
            if (!t) return;
            minimizedDraggingRef.current = true;
            minimizedDragOffsetRef.current = { x: t.clientX - (pos?.x ?? 20), y: t.clientY - (pos?.y ?? 20) };
            minimizedMovedRef.current = false;
          }}
          onClick={() => { if (!minimizedMovedRef.current) setMinimized(false); }}
        >
          <div className="ai-chat-minimized-icon" style={{ pointerEvents: 'auto' }}>
            <img src="/vizcode.svg" alt="AI" width={36} height={36} style={{ display: 'block' }} />
            <div className="ai-chat-min-badge">•</div>
          </div>
        </div>
      ) : (
        <div className="ai-chat-window" style={{ ...stylePos, width: size ? size.w : undefined, height: size ? size.h : undefined }} role="dialog" aria-label="AI chat window">
          <div className="ai-chat-header" onMouseDown={onHeaderMouseDown} onTouchStart={onHeaderTouchStart} style={{ cursor: 'move', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div className="ai-chat-title">VizBot</div>
              <div className="ai-chat-sub">From Thought to Code—Instantly</div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <button className="ai-chat-close" onClick={() => setMinimized(true)} title="Minimize">_</button>
              <button className="ai-chat-close" onClick={onClose} aria-label="Close chat">✕</button>
            </div>
          </div>
          <div className="ai-chat-body">
            <div className="ai-chat-messages" ref={containerRef}>
              {messages.map((m, i) => (
                <div key={i} className={`ai-chat-message ${
                  m.from === 'user' ? 'ai-chat-user' : 'ai-chat-ai'
                } ${m.error ? 'ai-chat-error' : ''}`}>
                  <div className="ai-chat-message-content">
                    {m.text}
                  </div>
                  {m.dsl && (
                    <div className="ai-chat-dsl-preview">
                      <div className="ai-chat-dsl-header">
                        <span>Generated DSL:</span>
                        <button 
                          className="ai-chat-copy-btn"
                          onClick={() => navigator.clipboard?.writeText(m.dsl!)}
                          title="Copy DSL to clipboard"
                        >
                          📋
                        </button>
                      </div>
                      <pre className="ai-chat-dsl-code">{m.dsl}</pre>
                    </div>
                  )}
                  {m.timestamp && (
                    <div className="ai-chat-timestamp">
                      {new Date(m.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="ai-chat-message ai-chat-ai ai-chat-loading">
                  <div className="ai-chat-typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="ai-chat-loading-text">
                    {provider === 'openai' ? 'GPT-4' : 'Gemini'} is thinking...
                  </span>
                </div>
              )}
              {error && (
                <div className="ai-chat-error-banner">
                  <span className="ai-chat-error-icon">⚠️</span>
                  <span>{error}</span>
                  <button 
                    className="ai-chat-error-retry"
                    onClick={() => setError(null)}
                  >
                    Dismiss
                  </button>
                </div>
              )}
            </div>
            <div className="ai-chat-input-row">
              <textarea 
                value={input} 
                onChange={e => setInput(e.target.value)} 
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }} 
                placeholder={isLoading ? 'Please wait...' : 'Describe your cloud architecture...'}
                disabled={isLoading}
                rows={2}
                maxLength={4000}
              />
              <div className="ai-chat-send-area">
                <div className="ai-chat-char-count">
                  {input.length}/4000
                </div>
                <button 
                  className="ai-chat-send" 
                  onClick={send}
                  disabled={isLoading || !input.trim()}
                  title={isLoading ? 'Please wait...' : 'Send message (Enter)'}
                >
                  {isLoading ? (
                    <div className="ai-chat-send-spinner"></div>
                  ) : (
                    'Send'
                  )}
                </button>
              </div>
            </div>
          </div>
          <div className="ai-chat-resize-handle" onMouseDown={(e) => {
            resizingRef.current = true;
            resizeStartRef.current = { x: e.clientX, y: e.clientY, w: (size?.w ?? 600), h: (size?.h ?? 400) };
          }} />
        </div>
      )}
    </div>
  );
};

export default AIChatWindow;
