const { getProviderConfig, shouldLog } = require('../config/aiConfig.cjs');

// Simple in-memory rate limiter (use Redis for production scale)
class RateLimiter {
  constructor() {
    this.requests = new Map();
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000); // Cleanup every minute
  }

  isAllowed(clientId, provider) {
    const config = getProviderConfig(provider);
    const now = Date.now();
    const windowStart = now - config.rateLimit.window;
    
    // Get or create client request history
    if (!this.requests.has(clientId)) {
      this.requests.set(clientId, new Map());
    }
    
    const clientRequests = this.requests.get(clientId);
    
    // Get or create provider request history for this client
    if (!clientRequests.has(provider)) {
      clientRequests.set(provider, []);
    }
    
    const providerRequests = clientRequests.get(provider);
    
    // Remove requests outside the window
    const validRequests = providerRequests.filter(timestamp => timestamp > windowStart);
    clientRequests.set(provider, validRequests);
    
    // Check if limit exceeded
    if (validRequests.length >= config.rateLimit.requests) {
      if (shouldLog('warn')) {
        console.warn(`[RateLimiter] Rate limit exceeded for client ${clientId} on ${provider}: ${validRequests.length}/${config.rateLimit.requests}`);
      }
      return false;
    }
    
    // Add current request
    validRequests.push(now);
    return true;
  }
  
  getRemainingRequests(clientId, provider) {
    const config = getProviderConfig(provider);
    const clientRequests = this.requests.get(clientId)?.get(provider) || [];
    const now = Date.now();
    const windowStart = now - config.rateLimit.window;
    const validRequests = clientRequests.filter(timestamp => timestamp > windowStart);
    
    return Math.max(0, config.rateLimit.requests - validRequests.length);
  }
  
  getResetTime(clientId, provider) {
    const clientRequests = this.requests.get(clientId)?.get(provider) || [];
    if (clientRequests.length === 0) return 0;
    
    const config = getProviderConfig(provider);
    const oldestRequest = Math.min(...clientRequests);
    return oldestRequest + config.rateLimit.window;
  }
  
  cleanup() {
    const now = Date.now();
    const maxAge = 5 * 60 * 1000; // 5 minutes
    
    for (const [clientId, clientRequests] of this.requests.entries()) {
      let hasActiveRequests = false;
      
      for (const [provider, requests] of clientRequests.entries()) {
        const activeRequests = requests.filter(timestamp => timestamp > now - maxAge);
        
        if (activeRequests.length > 0) {
          clientRequests.set(provider, activeRequests);
          hasActiveRequests = true;
        } else {
          clientRequests.delete(provider);
        }
      }
      
      if (!hasActiveRequests) {
        this.requests.delete(clientId);
      }
    }
    
    if (shouldLog('debug')) {
      console.log(`[RateLimiter] Cleanup completed. Active clients: ${this.requests.size}`);
    }
  }
  
  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.requests.clear();
  }
}

const rateLimiter = new RateLimiter();

function rateLimitMiddleware(req, res, next) {
  try {
    // Generate client ID from request
    const clientId = getClientId(req);
    const provider = req.body?.provider || 'openai';
    
    // Check rate limit
    if (!rateLimiter.isAllowed(clientId, provider)) {
      const remaining = rateLimiter.getRemainingRequests(clientId, provider);
      const resetTime = rateLimiter.getResetTime(clientId, provider);
      
      return res.status(429).json({
        error: 'Too many requests',
        code: 'RATE_LIMIT_EXCEEDED',
        remaining,
        resetTime: new Date(resetTime).toISOString(),
        retryAfter: Math.ceil((resetTime - Date.now()) / 1000)
      });
    }
    
    // Add rate limit info to response headers
    const remaining = rateLimiter.getRemainingRequests(clientId, provider);
    res.set({
      'X-RateLimit-Limit': getProviderConfig(provider).rateLimit.requests,
      'X-RateLimit-Remaining': remaining,
      'X-RateLimit-Reset': new Date(rateLimiter.getResetTime(clientId, provider)).toISOString()
    });
    
    next();
    
  } catch (error) {
    if (shouldLog('error')) {
      console.error('[RateLimiter] Error in rate limit middleware:', error);
    }
    // Don't block requests on rate limiter errors
    next();
  }
}

function getClientId(req) {
  // Use multiple factors to create a unique client identifier
  const ip = req.ip || req.connection.remoteAddress || '127.0.0.1';
  const userAgent = req.headers['user-agent'] || 'unknown';
  const forwarded = req.headers['x-forwarded-for'];
  
  // Create a stable identifier
  const identifier = `${forwarded || ip}:${userAgent}`;
  return Buffer.from(identifier).toString('base64').substring(0, 32);
}

// Export both middleware and rate limiter instance for testing
module.exports = {
  rateLimitMiddleware,
  rateLimiter,
  getClientId
};