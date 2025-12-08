const config = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    model: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
    maxTokens: parseInt(process.env.OPENAI_MAX_TOKENS) || 4096,
    temperature: parseFloat(process.env.OPENAI_TEMPERATURE) || 0.1,
    timeout: parseInt(process.env.OPENAI_TIMEOUT) || 30000,
    rateLimit: {
      requests: parseInt(process.env.OPENAI_RATE_LIMIT) || 60,
      window: 60 * 1000 // 1 minute
    }
  },
  
  gemini: {
    apiKey: process.env.GEMINI_API_KEY,
    model: process.env.GEMINI_MODEL || 'gemini-1.5-pro-latest',
    maxTokens: parseInt(process.env.GEMINI_MAX_TOKENS) || 8192,
    temperature: parseFloat(process.env.GEMINI_TEMPERATURE) || 0.1,
    timeout: parseInt(process.env.GEMINI_TIMEOUT) || 30000,
    rateLimit: {
      requests: parseInt(process.env.GEMINI_RATE_LIMIT) || 60,
      window: 60 * 1000 // 1 minute
    }
  },
  
  general: {
    maxConversationHistory: parseInt(process.env.MAX_CONVERSATION_HISTORY) || 6,
    enableFallback: process.env.ENABLE_AI_FALLBACK !== 'false',
    logLevel: process.env.LOG_LEVEL || 'info',
    enableCaching: process.env.ENABLE_CACHING !== 'false',
    cacheTimeout: parseInt(process.env.CACHE_TIMEOUT) || 300 // 5 minutes
  }
};

function validateEnvironment() {
  const missing = [];
  const warnings = [];

  // Check for at least one AI provider
  if (!config.openai.apiKey && !config.gemini.apiKey) {
    missing.push('At least one AI provider API key (OPENAI_API_KEY or GEMINI_API_KEY)');
  }

  // Check for OpenAI config if key is present
  if (config.openai.apiKey) {
    if (!config.openai.apiKey.startsWith('sk-')) {
      warnings.push('OPENAI_API_KEY format appears invalid (should start with sk-)');
    }
  }

  // Check for Gemini config if key is present
  if (config.gemini.apiKey) {
    if (!config.gemini.apiKey.startsWith('AIza')) {
      warnings.push('GEMINI_API_KEY format appears invalid (should start with AIza)');
    }
  }

  // Validate numeric configs
  if (isNaN(config.openai.maxTokens) || config.openai.maxTokens < 1) {
    warnings.push('Invalid OPENAI_MAX_TOKENS, using default');
    config.openai.maxTokens = 4096;
  }

  if (isNaN(config.gemini.maxTokens) || config.gemini.maxTokens < 1) {
    warnings.push('Invalid GEMINI_MAX_TOKENS, using default');
    config.gemini.maxTokens = 8192;
  }

  if (isNaN(config.openai.temperature) || config.openai.temperature < 0 || config.openai.temperature > 2) {
    warnings.push('Invalid OPENAI_TEMPERATURE, using default');
    config.openai.temperature = 0.1;
  }

  if (isNaN(config.gemini.temperature) || config.gemini.temperature < 0 || config.gemini.temperature > 2) {
    warnings.push('Invalid GEMINI_TEMPERATURE, using default');
    config.gemini.temperature = 0.1;
  }

  return { missing, warnings };
}

function getProviderConfig(provider) {
  const providerConfig = config[provider];
  if (!providerConfig) {
    throw new Error(`Unknown provider: ${provider}`);
  }
  
  return {
    ...providerConfig,
    ...config.general
  };
}

function isProduction() {
  return process.env.NODE_ENV === 'production';
}

function shouldLog(level) {
  const levels = { error: 0, warn: 1, info: 2, debug: 3 };
  const currentLevel = levels[config.general.logLevel] || 2;
  const targetLevel = levels[level] || 2;
  return targetLevel <= currentLevel;
}

module.exports = {
  config,
  validateEnvironment,
  getProviderConfig,
  isProduction,
  shouldLog
};