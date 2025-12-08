const OpenAIProvider = require('./openaiProvider.cjs');
const GeminiProvider = require('./geminiProvider.cjs');

class AIService {
  constructor() {
    this.providers = {
      openai: new OpenAIProvider(),
      gemini: new GeminiProvider()
    };
    this.defaultProvider = 'openai';
  }

  async generateDiagram(prompt, provider = this.defaultProvider, conversationHistory = []) {
    try {
      const aiProvider = this.providers[provider];
      if (!aiProvider) {
        throw new Error(`Unsupported AI provider: ${provider}`);
      }

      const startTime = Date.now();
      console.log(`[AIService] Starting generation with ${provider} provider`);

      const result = await aiProvider.generateDSL(prompt, conversationHistory);
      
      const duration = Date.now() - startTime;
      console.log(`[AIService] Generation completed in ${duration}ms`);

      return {
        success: true,
        dsl: result.dsl,
        explanation: result.explanation,
        provider,
        duration,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error(`[AIService] Error with ${provider} provider:`, error.message);
      
      // Fallback to alternative provider if available
      if (provider !== this.defaultProvider) {
        console.log(`[AIService] Attempting fallback to ${this.defaultProvider}`);
        try {
          return await this.generateDiagram(prompt, this.defaultProvider, conversationHistory);
        } catch (fallbackError) {
          console.error(`[AIService] Fallback failed:`, fallbackError.message);
        }
      }

      return {
        success: false,
        error: this.sanitizeError(error),
        provider,
        timestamp: new Date().toISOString()
      };
    }
  }

  sanitizeError(error) {
    // Don't expose API keys or internal details
    const message = error.message || 'AI service temporarily unavailable';
    
    if (message.includes('API key')) {
      return 'Authentication error - please check API configuration';
    }
    
    if (message.includes('quota') || message.includes('rate limit')) {
      return 'Service temporarily busy - please try again in a moment';
    }
    
    if (message.includes('network') || message.includes('timeout')) {
      return 'Connection issue - please check your internet and try again';
    }

    return message;
  }

  isProviderAvailable(provider) {
    return this.providers[provider] && this.providers[provider].isConfigured();
  }

  getAvailableProviders() {
    return Object.keys(this.providers).filter(provider => 
      this.isProviderAvailable(provider)
    );
  }

  async validateConfiguration() {
    const results = {};
    
    for (const [name, provider] of Object.entries(this.providers)) {
      try {
        const isValid = await provider.validateConfiguration();
        results[name] = {
          available: isValid,
          configured: provider.isConfigured()
        };
      } catch (error) {
        results[name] = {
          available: false,
          configured: false,
          error: error.message
        };
      }
    }
    
    return results;
  }
}

module.exports = new AIService();