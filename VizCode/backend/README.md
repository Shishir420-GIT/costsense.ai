# VizCode Backend - AI-Powered Architecture Diagram Generator

Production-ready Express.js backend with dual AI provider support for generating VizCode DSL from natural language descriptions.

## Features

- **Dual AI Providers**: OpenAI GPT-4 and Google Gemini with automatic fallback
- **Production Security**: Rate limiting, input validation, security headers, CORS
- **Error Handling**: Comprehensive error handling with structured logging
- **Health Monitoring**: Built-in health check endpoint
- **Configuration**: Environment-based configuration with validation

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=AIza-your-gemini-key-here
```

### 3. Start Server
```bash
npm start
```

Server runs on http://localhost:5001

## API Endpoints

### Chat API
- `GET /api/chat/status` - AI provider status
- `POST /api/chat/generate` - Generate VizCode DSL from description

### Core API
- `POST /api/backend/parse` - Parse VizCode DSL to diagram data
- `GET /api/backend/last-prompt` - Get last processed prompt
- `GET /health` - Health check

## Configuration

### AI Provider Settings
```env
# OpenAI Configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1
OPENAI_RATE_LIMIT=60

# Gemini Configuration  
GEMINI_MODEL=gemini-1.5-pro-latest
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.1
GEMINI_RATE_LIMIT=60
```

### Security & Performance
```env
LOG_LEVEL=info                    # error, warn, info, debug
ENABLE_AI_FALLBACK=true          # Auto-fallback between providers
MAX_CONVERSATION_HISTORY=6       # Context messages kept
NODE_ENV=development             # development, production
```

## Architecture

```
backend/
├── services/           # AI service layer
│   ├── aiService.cjs      # Provider abstraction
│   ├── openaiProvider.cjs # OpenAI integration
│   └── geminiProvider.cjs # Gemini integration
├── controllers/        # API controllers
│   └── chatController.cjs # Chat endpoint logic
├── middleware/         # Express middleware
│   ├── security.cjs       # Security headers, validation
│   └── rateLimiter.cjs    # Rate limiting
├── config/            # Configuration
│   └── aiConfig.cjs      # AI provider config
└── routes/            # API routes
    └── chat.cjs          # Chat routes
```

## Security Features

- **Rate Limiting**: 60 requests/minute per provider per client
- **Input Validation**: Message length, content sanitization
- **Security Headers**: XSS protection, CORS, CSP
- **Error Handling**: No sensitive data exposure
- **Request Timeout**: 30-second timeout protection

## Development

```bash
# Start in development mode
npm run dev

# Check logs
tail -f logs/backend.log

# Test endpoints
curl http://localhost:5001/health
curl http://localhost:5001/api/chat/status
```

## Troubleshooting

**"Missing required environment variables" error:**
- Ensure `.env` file exists with valid API keys
- Check API key formats (OpenAI: `sk-`, Gemini: `AIza`)

**"Port already in use" error:**
```bash
lsof -ti:5001 | xargs kill -9
```

**Rate limit errors:**
- Check rate limits in `.env` configuration
- Wait for rate limit window to reset
