import { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send } from 'lucide-react'
import { chatAPI } from '../services/api'

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [sessionId, setSessionId] = useState<string>()
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!message.trim() || loading) return

    const userMessage = message.trim()
    setMessage('')
    setLoading(true)

    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await chatAPI.send(userMessage, sessionId)

      if (!sessionId) {
        setSessionId(response.data.session_id)
      }

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.message,
          intent: response.data.intent,
          tool_used: response.data.tool_used,
        },
      ])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-ey-yellow hover:bg-ey-yellow-dark text-black rounded-full p-4 shadow-lg transition-all z-50"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-ey-grey-dark border border-ey-grey-light rounded-lg shadow-2xl flex flex-col z-50">
          {/* Header */}
          <div className="bg-ey-grey-medium border-b border-ey-grey-light p-4 flex items-center justify-between rounded-t-lg">
            <div className="flex items-center space-x-2">
              <MessageCircle className="h-5 w-5 text-ey-yellow" />
              <span className="font-semibold text-white">CostSense AI Assistant</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-8">
                <p className="mb-2">👋 Hello! I'm your cost intelligence assistant.</p>
                <p className="text-sm">Ask me about your cloud costs, optimizations, or create tickets.</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-ey-yellow text-black'
                      : 'bg-ey-grey-medium text-white border border-ey-grey-light'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.tool_used && (
                    <span className="text-xs opacity-70 mt-1 block">
                      Used: {msg.tool_used}
                    </span>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-ey-grey-medium text-white rounded-lg p-3 border border-ey-grey-light">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-ey-yellow rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-ey-yellow rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-ey-yellow rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-ey-grey-light p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about costs, optimizations..."
                className="flex-1 bg-ey-grey-medium border border-ey-grey-light rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-ey-yellow"
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !message.trim()}
                className="bg-ey-yellow hover:bg-ey-yellow-dark text-black rounded-lg px-4 py-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
