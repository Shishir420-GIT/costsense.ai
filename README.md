# 🚀 AWS Cost Optimization Platform - CostSense AI

A production-ready AWS cost optimization platform powered by AI agents using Strands Agents SDK, React, and FastAPI. This comprehensive solution provides real-time cost analysis, intelligent optimization recommendations, and automated insights to help you minimize your AWS spending.

![Platform Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![AI Powered](https://img.shields.io/badge/AI-Multi%20Agent%20System-green)
![Real-time](https://img.shields.io/badge/Real--time-WebSocket-orange)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

### 🤖 Multi-Agent AI System
- **Specialized Agents**: Dedicated agents for cost analysis, infrastructure optimization, financial calculations, and remediation planning
- **Intelligent Orchestration**: Smart task routing and result synthesis
- **Local LLM Processing**: Privacy-focused processing with Ollama (Llama 2/Code Llama)
- **Parallel Analysis**: Concurrent multi-agent processing for comprehensive insights

### 📊 Advanced Analytics & Visualizations
- **Interactive D3.js Charts**: Cost trends, service breakdowns, utilization heatmaps
- **Real-time Dashboards**: Live cost monitoring and agent status
- **Savings Projections**: Future cost predictions and optimization impact
- **Custom Reports**: Automated report generation with multiple export formats

### ⚡ Real-time Communication
- **WebSocket Integration**: Live progress updates and streaming responses
- **Agent Status Monitoring**: Real-time health checks and performance metrics
- **Progressive Analysis**: Step-by-step analysis with live feedback

### 🔧 AWS Integration
- **Comprehensive Service Coverage**: EC2, S3, RDS, Lambda, and more
- **Read-only Operations**: Safe analysis without infrastructure changes
- **Cost Explorer Integration**: Historical and current spending analysis
- **Resource Utilization Metrics**: CloudWatch integration for performance data

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and builds
- **Tailwind CSS** for modern UI design
- **D3.js** & **Chart.js** for advanced visualizations
- **Zustand** for state management
- **React Query** for server state management
- **Framer Motion** for smooth animations

### Backend
- **FastAPI** with Python 3.11+
- **Strands Agents SDK** for multi-agent orchestration
- **Ollama** for local LLM processing
- **WebSocket** for real-time communication
- **PostgreSQL** for data persistence
- **Redis** for caching and session storage

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Nginx** for production deployment
- **AWS Boto3** for AWS service integration

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Python** 3.11+
- **Node.js** 18+
- **AWS CLI** configured with appropriate permissions

### AWS Permissions Required

Your AWS credentials need the following read-only permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetUsageReport",
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "cloudwatch:GetMetricStatistics",
                "rds:DescribeDBInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CostSense-AI

# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

Edit `backend/.env` with your AWS credentials:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Other settings are pre-configured for local development
```

### 3. Start the Platform

```bash
# Option 1: Use the convenient development script
./start-dev.sh

# Option 2: Manual startup
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 4. Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **System Health**: http://localhost:8000/health

## 🏗️ Architecture

### Multi-Agent System

```mermaid
graph TD
    A[User Query] --> B[Orchestrator Agent]
    B --> C[Cost Analysis Agent]
    B --> D[Infrastructure Agent]  
    B --> E[Financial Agent]
    B --> F[Remediation Agent]
    
    C --> G[AWS Cost Explorer]
    D --> H[EC2 Metrics]
    D --> I[S3 Analysis]
    E --> J[Savings Calculator]
    F --> K[Action Plans]
    
    C --> L[Synthesis Engine]
    D --> L
    E --> L
    F --> L
    
    L --> M[Final Recommendations]
```

### System Components

- **Orchestrator Agent**: Intelligent task routing and coordination
- **Cost Analysis Agent**: AWS spending pattern analysis and trends
- **Infrastructure Agent**: Resource optimization and rightsizing
- **Financial Agent**: Precise calculations, ROI analysis, projections
- **Remediation Agent**: Actionable implementation plans and roadmaps

### Real-time Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant W as WebSocket
    participant O as Orchestrator
    participant A as Agents
    
    U->>F: Submit Analysis Request
    F->>W: WebSocket Message
    W->>O: Route to Orchestrator
    O->>A: Distribute to Agents
    A-->>O: Stream Results
    O-->>W: Progress Updates
    W-->>F: Real-time Updates
    F-->>U: Live Dashboard Updates
```

## 📊 Usage Examples

### Cost Analysis
```typescript
// Request comprehensive cost analysis
const analysis = await costApi.analyzeCosts({
  query: "Analyze my AWS costs for the last 90 days and identify trends",
  time_period: "90_days"
});
```

### Real-time Optimization
```typescript
// Start real-time optimization analysis
webSocketService.requestComprehensiveAnalysis(
  "Provide detailed optimization recommendations for my infrastructure"
);

// Listen for updates
webSocketService.on('status', (update) => {
  console.log(`Progress: ${update.progress}% - ${update.message}`);
});
```

### Multi-Agent Parallel Processing
```typescript
// Execute multiple agents simultaneously
const results = await agentsApi.executeMultiAgent(
  "Comprehensive cost optimization analysis",
  "parallel"
);
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test categories
python -m pytest -m unit
python -m pytest -m integration
```

### Frontend Tests
```bash
cd frontend

# Install test dependencies (if not already installed)
npm install

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 🚢 Production Deployment

### Docker Production Build
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### AWS Deployment Options

#### Option 1: ECS with Fargate
```bash
# Build and push images
docker build -t costense-backend ./backend
docker build -t costense-frontend ./frontend

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag costense-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/costense-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/costense-backend:latest
```

#### Option 2: EC2 Deployment
```bash
# On EC2 instance
git clone <repository>
cd CostSense-AI
./setup.sh
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

#### Backend Configuration
```bash
# AWS Settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Ollama Settings  
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Database Settings
POSTGRES_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

#### Frontend Configuration
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Performance Tuning

#### Ollama Optimization
```bash
# Download optimal model for your hardware
docker exec cost-optimizer-ollama ollama pull llama2:7b
docker exec cost-optimizer-ollama ollama pull codellama:7b
```

#### Database Optimization
```sql
-- PostgreSQL performance tuning
shared_buffers = '256MB'
effective_cache_size = '1GB'
maintenance_work_mem = '128MB'
```

## 📈 Monitoring & Observability

### Health Checks
```bash
# Check system health
curl http://localhost:8000/health

# Check agent status
curl http://localhost:8000/api/v1/agents/status
```

### Logging
```bash
# View backend logs
tail -f backend/logs/app_*.log

# View Docker logs  
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Metrics
- Agent execution times and success rates
- WebSocket connection statistics  
- Cost analysis accuracy metrics
- API response times and error rates

## 🔒 Security

### Data Protection
- **Local Processing**: All AI processing done locally with Ollama
- **Read-only AWS**: No modifications to your AWS infrastructure
- **Encrypted Storage**: Sensitive data encrypted at rest
- **Secure Communication**: HTTPS/WSS in production

### Access Control
- API rate limiting
- Request validation and sanitization
- CORS protection
- Input validation on all endpoints

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `./run-tests.sh`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow TypeScript/Python best practices
- Write comprehensive tests for new features
- Update documentation for API changes
- Use conventional commit messages
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

#### Ollama Model Download Fails
```bash
# Manual model download
docker exec -it cost-optimizer-ollama ollama pull llama2
```

#### WebSocket Connection Issues  
```bash
# Check firewall settings
sudo ufw allow 8000
sudo ufw allow 3000
```

#### AWS Permission Errors
```bash
# Test AWS credentials
aws sts get-caller-identity
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost
```

### Getting Help

- **Documentation**: Check the `/docs` folder for detailed guides
- **API Reference**: Visit http://localhost:8000/docs when running
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions for questions and tips

---

## 🌟 Acknowledgments

- **Strands Agents SDK** for the multi-agent framework
- **Ollama** for local LLM capabilities  
- **FastAPI** for the excellent Python web framework
- **React & Vite** for the modern frontend experience
- **D3.js** for powerful data visualizations

---

<div align="center">

**Built with ❤️ by the CostSense AI Team**

[⭐ Star this repo](https://github.com/your-repo/CostSense-AI) | [🐛 Report Bug](https://github.com/your-repo/CostSense-AI/issues) | [💡 Request Feature](https://github.com/your-repo/CostSense-AI/issues)

</div>