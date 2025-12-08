const { shouldLog } = require('../config/aiConfig.cjs');

// Input validation middleware
function validateInput(req, res, next) {
  try {
    const { message, provider } = req.body;
    
    // Validate message
    if (!message || typeof message !== 'string') {
      return res.status(400).json({
        error: 'Message is required and must be a string',
        code: 'INVALID_MESSAGE'
      });
    }
    
    if (message.length > 4000) {
      return res.status(400).json({
        error: 'Message too long (maximum 4000 characters)',
        code: 'MESSAGE_TOO_LONG'
      });
    }
    
    if (message.trim().length === 0) {
      return res.status(400).json({
        error: 'Message cannot be empty',
        code: 'EMPTY_MESSAGE'
      });
    }
    
    // Validate provider
    if (provider && !['openai', 'gemini'].includes(provider)) {
      return res.status(400).json({
        error: 'Invalid AI provider. Must be "openai" or "gemini"',
        code: 'INVALID_PROVIDER'
      });
    }
    
    // Sanitize message (remove potential security risks)
    req.body.message = sanitizeInput(message);
    
    next();
    
  } catch (error) {
    if (shouldLog('error')) {
      console.error('[Security] Input validation error:', error);
    }
    return res.status(400).json({
      error: 'Invalid input format',
      code: 'VALIDATION_ERROR'
    });
  }
}

// Sanitize user input
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  
  // Remove null bytes and control characters (except newlines and tabs)
  let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  
  // Limit consecutive whitespace
  sanitized = sanitized.replace(/\s{4,}/g, '   ');
  
  // Prevent excessively long lines
  sanitized = sanitized.split('\n').map(line => 
    line.length > 500 ? line.substring(0, 500) + '...' : line
  ).join('\n');
  
  return sanitized.trim();
}

// Security headers middleware
function securityHeaders(req, res, next) {
  // Basic security headers
  res.set({
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; connect-src 'self' https://api.openai.com https://generativelanguage.googleapis.com; script-src 'self'; style-src 'self' 'unsafe-inline';",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  });
  
  next();
}

// Request logging middleware
function requestLogger(req, res, next) {
  if (!shouldLog('info')) {
    return next();
  }
  
  const startTime = Date.now();
  const clientId = getClientId(req);
  const method = req.method;
  const url = req.originalUrl || req.url;
  
  // Log request
  console.log(`[Security] ${method} ${url} - Client: ${clientId}`);
  
  // Log response
  const originalSend = res.json;
  res.json = function(body) {
    const duration = Date.now() - startTime;
    const status = res.statusCode;
    
    if (shouldLog('info')) {
      console.log(`[Security] ${method} ${url} - ${status} (${duration}ms)`);
    }
    
    // Log errors for monitoring
    if (status >= 400 && shouldLog('warn')) {
      console.warn(`[Security] Error response: ${status} - ${JSON.stringify(body).substring(0, 200)}`);
    }
    
    return originalSend.call(this, body);
  };
  
  next();
}

function getClientId(req) {
  const ip = req.ip || req.connection.remoteAddress || '127.0.0.1';
  const userAgent = req.headers['user-agent'] || 'unknown';
  const forwarded = req.headers['x-forwarded-for'];
  
  const identifier = `${forwarded || ip}:${userAgent}`;
  return Buffer.from(identifier).toString('base64').substring(0, 16);
}

// Error handling middleware
function errorHandler(err, req, res, next) {
  const clientId = getClientId(req);
  
  if (shouldLog('error')) {
    console.error(`[Security] Unhandled error for client ${clientId}:`, {
      message: err.message,
      stack: err.stack,
      url: req.originalUrl,
      method: req.method,
      body: req.body ? JSON.stringify(req.body).substring(0, 200) : 'none'
    });
  }
  
  // Don't expose internal errors to clients
  res.status(500).json({
    error: 'Internal server error',
    code: 'INTERNAL_ERROR',
    timestamp: new Date().toISOString()
  });
}

// Request timeout middleware
function requestTimeout(timeoutMs = 30000) {
  return (req, res, next) => {
    const timer = setTimeout(() => {
      if (!res.headersSent) {
        if (shouldLog('warn')) {
          console.warn(`[Security] Request timeout after ${timeoutMs}ms for ${req.originalUrl}`);
        }
        
        res.status(408).json({
          error: 'Request timeout',
          code: 'REQUEST_TIMEOUT',
          timeout: timeoutMs
        });
      }
    }, timeoutMs);
    
    // Clear timeout when response is sent
    res.on('finish', () => clearTimeout(timer));
    res.on('close', () => clearTimeout(timer));
    
    next();
  };
}

module.exports = {
  validateInput,
  sanitizeInput,
  securityHeaders,
  requestLogger,
  errorHandler,
  requestTimeout,
  getClientId
};