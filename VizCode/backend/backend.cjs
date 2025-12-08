// VizCode Backend - Production AI-Powered Architecture Diagram Generator
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { validateEnvironment, shouldLog } = require('./config/aiConfig.cjs');
const { rateLimitMiddleware } = require('./middleware/rateLimiter.cjs');
const { 
  validateInput, 
  securityHeaders, 
  requestLogger, 
  errorHandler,
  requestTimeout 
} = require('./middleware/security.cjs');

const app = express();

// Validate environment on startup
const { missing, warnings } = validateEnvironment();

if (missing.length > 0) {
  console.error('[Startup] Missing required environment variables:');
  missing.forEach(item => console.error(`  - ${item}`));
  if (process.env.NODE_ENV === 'production') {
    process.exit(1);
  }
}

if (warnings.length > 0 && shouldLog('warn')) {
  console.warn('[Startup] Configuration warnings:');
  warnings.forEach(item => console.warn(`  - ${item}`));
}

// Security middleware
app.use(securityHeaders);
app.use(requestTimeout(30000)); // 30 second timeout
app.use(requestLogger);

// CORS configuration
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://viz-code-six.vercel.app', 'https://vizcode.app'] // Update with your domains
    : ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
  credentials: true,
  methods: ['GET', 'POST', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Accept']
}));

// Body parsing with limits
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

let lastPrompt = '';

// Simple parse endpoint (stub) -------------------------------------------------
app.post('/api/backend/parse', async (req, res) => {
  const { prompt } = req.body;
  lastPrompt = prompt;

  if (prompt && typeof prompt === 'string') {
    const lines = prompt.split(/\r?\n/);
    let clusterStack = [];
    let clusterNodes = {};
    let clusters = [];
    for (let line of lines) {
      const indent = (line.match(/^([ \t]*)/)[1] || '').length;
      const clusterMatch = line.match(/^[ \t]*Cluster: (.+)$/);
      if (clusterMatch) {
        const clusterLabel = clusterMatch[1].trim();
        const clusterId = clusterLabel.toLowerCase().replace(/\s+/g, '-');
        while (clusterStack.length && clusterStack[clusterStack.length - 1].indent >= indent) {
          clusterStack.pop();
        }
        let parentId = clusterStack.length ? clusterStack[clusterStack.length - 1].id : null;
        clusters.push({ id: clusterId, label: clusterLabel, parentId });
        clusterNodes[clusterId] = [];
        clusterStack.push({ id: clusterId, indent });
        continue;
      }
      const nodeMatch = line.match(/^[ \t]*Node: (.+)$/);
      if (nodeMatch && clusterStack.length) {
        const nodeText = nodeMatch[1].trim();
        const nameMatch = nodeText.match(/\[name=([^\]]+)\]/);
        let label = nodeText;
        let name = '';
        if (nameMatch) {
          label = nodeText.replace(nameMatch[0], '').trim();
          name = nameMatch[1].trim();
        }
        const nodeId = name ? name.toLowerCase().replace(/\s+/g, '-') : label.toLowerCase().replace(/\s+/g, '-');
        let color = '#e3f2fd';
        let type = label.toLowerCase().replace(/\s+/g, '-');
        if (/database|db/i.test(label)) { color = '#e8f5e9'; type = 'database'; }
        else if (/api/i.test(label)) { color = '#c8e6c9'; type = 'api'; }
        const currentCluster = clusterStack[clusterStack.length - 1].id;
        clusterNodes[currentCluster].push({ id: nodeId, label, name, color, type, clusterId: currentCluster });
      }
    }

    // Improved layout: position clusters and their nodes with better spacing
    let nodes = [];
    let clusterPositions = {};
    function layoutCluster(clusterId, x, y, depth) {
      clusterPositions[clusterId] = { x, y };
      const childClusters = clusters.filter(c => c.parentId === clusterId);
      let childY = y + 120; // Increased vertical spacing between cluster levels
      childClusters.forEach((child, i) => {
        layoutCluster(child.id, x + 150, childY + i * 200, depth + 1); // Better spacing
      });
    }
    clusters.filter(c => !c.parentId).forEach((cluster, i) => {
      layoutCluster(cluster.id, 150 + i * 400, 150, 0); // More spacing between root clusters
    });
    
    clusters.forEach(cluster => {
      const pos = clusterPositions[cluster.id] || { x: 150, y: 150 };
      const nodesInCluster = clusterNodes[cluster.id] || [];
      const nodeSpacingX = 180; // Increased horizontal spacing
      const nodeSpacingY = 100; // Vertical spacing between nodes
      const maxNodesPerRow = 3; // Maximum nodes per row before wrapping
      
      nodesInCluster.forEach((node, j) => {
        const row = Math.floor(j / maxNodesPerRow);
        const col = j % maxNodesPerRow;
        const nodeX = pos.x + col * nodeSpacingX;
        const nodeY = pos.y + 100 + row * nodeSpacingY; // Start nodes below cluster header
        
        nodes.push({ 
          ...node, 
          x: nodeX, 
          y: nodeY, 
          clusterId: cluster.id 
        });
      });
    });

    // parse edges
    const edgeRegex = /^\s*([\w\s]+)->([\w\s]+)\s*(?:\[arrow=(\w+),?\s*label='([^']*)'\])?/gm;
    let edges = [];
    let match;
    while ((match = edgeRegex.exec(prompt)) !== null) {
      function findNodeId(ref) {
        ref = ref.trim();
        let node = nodes.find(n => n.name && n.name === ref);
        if (node) return node.id;
        node = nodes.find(n => n.label === ref);
        if (node) return node.id;
        return ref.toLowerCase().replace(/\s+/g, '-');
      }
      const fromId = findNodeId(match[1]);
      const toId = findNodeId(match[2]);
      edges.push({ id: `e-${fromId}-${toId}`, from: fromId, to: toId, label: match[4] || '', type: match[3] || 'solid' });
    }

    return res.json({ nodes, edges, clusters, icons: [], message: 'Multi-level nested clustering supported.' });
  }

  return res.json({ nodes: [], edges: [], clusters: [], icons: [], message: 'Mocked backend response.' });
});

app.get('/api/backend/last-prompt', (req, res) => { res.json({ prompt: lastPrompt }); });

// AI Chat routes with security middleware
const chatRouter = require('./routes/chat.cjs');
app.use('/api/chat', rateLimitMiddleware, chatRouter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    error: 'Not found',
    code: 'NOT_FOUND',
    path: req.originalUrl
  });
});

// Global error handler (must be last)
app.use(errorHandler);

const PORT = process.env.PORT || 5001;

app.listen(PORT, () => { 
  console.log(`[Startup] VizCode Backend listening on port ${PORT}`);
  console.log(`[Startup] Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`[Startup] Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Shutdown] SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('[Shutdown] SIGINT received, shutting down gracefully');
  process.exit(0);
});
