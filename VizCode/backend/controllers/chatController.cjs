const aiService = require('../services/aiService.cjs');
const { shouldLog } = require('../config/aiConfig.cjs');

// In-memory conversation storage (use Redis/database for production scale)
const conversations = new Map();

function getConversationId(req) {
  // Use session ID or generate based on IP + User-Agent for simple session tracking
  const sessionData = req.headers['user-agent'] + req.connection.remoteAddress;
  return Buffer.from(sessionData).toString('base64').substring(0, 16);
}

exports.handleChat = async (req, res) => {
  const startTime = Date.now();
  
  try {
    const { message, provider = 'openai', regenerate = false } = req.body;
    
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({ 
        error: 'Message is required',
        code: 'INVALID_INPUT'
      });
    }

    if (message.length > 4000) {
      return res.status(400).json({ 
        error: 'Message too long (max 4000 characters)',
        code: 'MESSAGE_TOO_LONG'
      });
    }

    // Get or create conversation history
    const conversationId = getConversationId(req);
    let history = conversations.get(conversationId) || [];
    
    if (shouldLog('info')) {
      console.log(`[ChatController] Processing message for session ${conversationId} with ${provider} provider`);
    }

    // Add user message to history (unless regenerating)
    if (!regenerate) {
      history.push({ from: 'user', text: message.trim(), timestamp: new Date().toISOString() });
    }

    // Generate AI response
    const result = await aiService.generateDiagram(message.trim(), provider, history);
    
    if (!result.success) {
      if (shouldLog('warn')) {
        console.warn(`[ChatController] AI generation failed:`, result.error);
      }
      
      return res.status(500).json({ 
        error: result.error,
        code: 'AI_GENERATION_FAILED',
        provider: result.provider,
        fallbackMessage: 'AI is currently unavailable. Please try again in a moment.'
      });
    }

    // Prepare response
    const aiResponse = {
      reply: result.explanation || 'I\'ve processed your message!',
      provider: result.provider,
      generationTime: result.duration
    };

    // Include DSL only if it was generated
    if (result.dsl) {
      aiResponse.dsl = result.dsl;
    }

    // Add AI response to conversation history
    const historyEntry = { 
      from: 'ai', 
      text: aiResponse.reply, 
      timestamp: result.timestamp 
    };
    
    // Include DSL in history only if it was generated
    if (result.dsl) {
      historyEntry.dsl = result.dsl;
    }
    
    history.push(historyEntry);

    // Limit conversation history (keep last 20 messages)
    if (history.length > 20) {
      history = history.slice(-20);
    }
    
    conversations.set(conversationId, history);

    // Clean up old conversations (simple memory management)
    if (conversations.size > 1000) {
      const oldestKeys = Array.from(conversations.keys()).slice(0, 100);
      oldestKeys.forEach(key => conversations.delete(key));
    }

    const totalTime = Date.now() - startTime;
    if (shouldLog('info')) {
      console.log(`[ChatController] Response completed in ${totalTime}ms`);
    }

    res.json(aiResponse);

  } catch (error) {
    const totalTime = Date.now() - startTime;
    
    if (shouldLog('error')) {
      console.error(`[ChatController] Unexpected error after ${totalTime}ms:`, error);
    }

    res.status(500).json({ 
      error: 'Internal server error',
      code: 'INTERNAL_ERROR',
      fallbackMessage: 'Something went wrong. Please try again.'
    });
  }
};

exports.getConversationHistory = (req, res) => {
  try {
    const conversationId = getConversationId(req);
    const history = conversations.get(conversationId) || [];
    
    res.json({ 
      conversationId,
      history: history.map(msg => ({
        from: msg.from,
        text: msg.text,
        timestamp: msg.timestamp
      }))
    });
  } catch (error) {
    console.error('[ChatController] Error getting conversation history:', error);
    res.status(500).json({ error: 'Failed to retrieve conversation history' });
  }
};

exports.clearConversation = (req, res) => {
  try {
    const conversationId = getConversationId(req);
    conversations.delete(conversationId);
    
    res.json({ 
      success: true,
      message: 'Conversation cleared'
    });
  } catch (error) {
    console.error('[ChatController] Error clearing conversation:', error);
    res.status(500).json({ error: 'Failed to clear conversation' });
  }
};

exports.getAIStatus = async (req, res) => {
  try {
    const status = await aiService.validateConfiguration();
    const availableProviders = aiService.getAvailableProviders();
    
    res.json({
      providers: status,
      available: availableProviders,
      conversationCount: conversations.size
    });
  } catch (error) {
    console.error('[ChatController] Error getting AI status:', error);
    res.status(500).json({ error: 'Failed to get AI status' });
  }
};
