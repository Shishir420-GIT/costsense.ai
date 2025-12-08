# VizCode - AI-Powered Cloud Architecture Diagrams

Live URL - [VizCode](viz-code-six.vercel.app)

VizCode is a comprehensive tool for creating cloud architecture diagrams through both natural language AI prompts and visual editing. Transform your infrastructure descriptions into professional diagrams instantly.

## Features

- **AI-Powered Generation**: Describe your architecture in plain English, get VizCode DSL
- **Dual AI Providers**: Choose between OpenAI GPT-4 and Google Gemini
- **Multi-Cloud Support**: Extensive icon libraries for AWS, Azure, and GCP services  
- **Interactive Visual Editor**: Drag-and-drop interface with smart edge routing
- **Excel Integration**: Import/export diagrams from spreadsheets
- **Nested Clustering**: Hierarchical organization with parent-child relationships
- **Production Ready**: Rate limiting, security, and error handling built-in

## Tech Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: Node.js + Express
- **AI Integration**: OpenAI GPT-4 & Google Gemini APIs
- **Deployment**: Vercel (frontend + serverless functions)
- **Icons**: 1000+ cloud service icons (AWS, Azure, GCP)

## Prerequisites

- Node.js 18+ and npm
- OpenAI API key (get from [OpenAI](https://platform.openai.com/api-keys))
- Google Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd VizCode
npm install
cd backend && npm install
```

### 2. Environment Setup

**Backend (.env in /backend directory):**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=AIza-your-gemini-key-here
NODE_ENV=development
PORT=5001
```

**Frontend (.env.local in root directory):**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_BACKEND_URL=http://localhost:5001
```

### 3. Run Development

Start both frontend and backend:

```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend  
npm run dev
```

Open http://localhost:5173

## <� Usage

### AI-Powered Diagram Generation

1. **Click the AI chat icon** in the top-right corner
2. **Select your AI provider** (OpenAI or Gemini)
3. **Describe your architecture** in natural language:

```
Create a 3-tier web application on AWS with:
- Application Load Balancer in public subnet
- EC2 instances in private subnet  
- RDS database in database subnet
- All within a VPC
```

4. **AI generates VizCode DSL** automatically
5. **Diagram renders** with full editing capabilities

### Manual DSL Creation

Use the Monaco editor with VizCode syntax:

```
Cluster: Production VPC
  Cluster: Public Subnet
    Node: ApplicationLoadBalancer [name=ALB]
  Cluster: Private Subnet  
    Node: EC2 [name=Web Server]
    Node: RDS [name=Database]
    
ALB -> Web Server [arrow=solid, label='HTTP']
Web Server -> Database [arrow=solid, label='Query']
```

### Excel Integration

- **Export**: Download as Excel with separate sheets for nodes and edges
- **Import**: Upload Excel files with structured node and connection data

##  Deployment to Vercel

### 1. Prepare for Deployment

```bash
# Build the project locally to test
npm run build
```

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login and deploy
vercel login
vercel

# Follow prompts to deploy
```

### 3. Configure Environment Variables

In your Vercel dashboard, add these environment variables:

```
OPENAI_API_KEY=sk-your-openai-key-here  
GEMINI_API_KEY=AIza-your-gemini-key-here
NODE_ENV=production
```

### 4. Update CORS Origins

Edit `backend/backend.cjs` line 40-41 to include your Vercel domain:

```javascript
origin: process.env.NODE_ENV === 'production' 
  ? ['https://your-app.vercel.app'] 
  : ['http://localhost:3000', 'http://localhost:5173'],
```

## = Project Structure

## =' Configuration Options

### AI Provider Settings

**OpenAI Configuration:**
```env
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1
OPENAI_RATE_LIMIT=60
```

**Gemini Configuration:**
```env  
GEMINI_MODEL=gemini-1.5-pro-latest
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.1
GEMINI_RATE_LIMIT=60
```

### Security Settings

```env
LOG_LEVEL=info              # error, warn, info, debug
ENABLE_AI_FALLBACK=true     # Auto-fallback between providers
MAX_CONVERSATION_HISTORY=6  # Messages kept in context
```

## = Production Considerations

- **Rate Limits**: 60 requests/minute per provider (configurable)
- **Security**: Input validation, CORS, security headers included
- **Error Handling**: Graceful fallbacks and user-friendly messages
- **Logging**: Structured logging with configurable levels
- **Memory Management**: Automatic conversation cleanup
- **Monitoring**: Health check endpoint at `/health`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**"AI is busy leveling up" message:**
- Check API keys are correctly set in environment variables
- Verify API keys have sufficient credits/quota
- Check network connectivity to AI providers

**TypeScript errors:**
- Run `npm run build` to check for type errors
- Ensure all dependencies are installed

**Deployment issues:**
- Verify Vercel environment variables are set
- Check function timeout limits (currently 30s)
- Review build logs for specific errors

### Health Check

Visit `/health` endpoint to verify backend status:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z", 
  "version": "1.0.0",
  "environment": "production"
}
```

## Support

- Create an issue for bug reports
- Check existing issues for solutions
- Review logs for error details

---

**Transform your cloud architecture ideas into professional diagrams with VizCode!**