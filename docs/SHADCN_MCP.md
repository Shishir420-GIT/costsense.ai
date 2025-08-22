# 🎨 Shadcn UI MCP Server Integration

## Overview

The CostSense AI platform now includes a comprehensive **Model Context Protocol (MCP) Server** for Shadcn UI components. This integration provides:

- **Dynamic Component Generation**: Create UI components programmatically via API
- **Real-time Component Templates**: Get pre-configured component code with variants
- **Batch Operations**: Generate multiple components simultaneously
- **Component Library Management**: Browse and discover available components
- **Theme Integration**: Seamless dark/light theme support

## 🚀 Features

### Core Components Available

- **Button**: Multiple variants (default, destructive, outline, secondary, ghost, link)
- **Card**: Flexible card layouts with header, content, and footer
- **Badge**: Status indicators with success, warning, destructive variants  
- **Progress**: Animated progress bars with customizable values
- **Alert**: Contextual alerts with multiple severity levels
- **Input**: Form inputs with proper styling and validation states
- **Label**: Accessible form labels

### MCP Server Capabilities

- **Component Discovery**: List all available components and their variants
- **Template Generation**: Get complete JSX templates with imports
- **Batch Processing**: Generate multiple components in one request
- **Health Monitoring**: Real-time server status and diagnostics
- **Type Safety**: Full TypeScript support with proper interfaces

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/v1/mcp/shadcn
```

### Available Endpoints

#### 1. List Components
```http
GET /components
```

**Response:**
```json
{
  "components": {
    "button": {
      "variants": ["default", "destructive", "outline", "secondary", "ghost", "link"],
      "sizes": ["default", "sm", "lg", "icon"],
      "dependencies": ["@radix-ui/react-slot", "class-variance-authority"],
      "imports": ["Button", "buttonVariants"]
    }
  },
  "total": 7,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Generate Component
```http
POST /components/generate
```

**Request:**
```json
{
  "name": "button",
  "variant": "default",
  "props": {
    "size": "lg",
    "disabled": false
  },
  "children": "Click me"
}
```

**Response:**
```json
{
  "name": "button",
  "code": "<Button variant=\"default\" size=\"lg\">Click me</Button>",
  "imports": ["Button", "buttonVariants"],
  "dependencies": ["@radix-ui/react-slot", "class-variance-authority"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. Get Component Template
```http
GET /components/{component_name}/template?variant=default
```

**Response:**
```json
{
  "component": "button",
  "variant": "default", 
  "template": "<Button variant=\"default\">Click me</Button>",
  "imports": ["Button"],
  "dependencies": ["@radix-ui/react-slot"],
  "usage_example": "import { Button } from '@/components/ui/button'\n\nexport function Example() {\n  return (\n    <Button variant=\"default\">Click me</Button>\n  )\n}",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 4. Batch Generate
```http
POST /components/batch-generate
```

**Request:**
```json
[
  {
    "name": "button",
    "variant": "default",
    "children": "Submit"
  },
  {
    "name": "badge", 
    "variant": "success",
    "children": "Online"
  }
]
```

## 🔧 Frontend Integration

### API Client Usage

```typescript
import { shadcnMcpApi, useShadcnMcp } from '@/services/shadcnMcpApi';

// Using the hook
const { generateComponent, getTemplate, listComponents } = useShadcnMcp();

// Generate a button component
const buttonComponent = await generateComponent({
  name: 'button',
  variant: 'default',
  children: 'Analyze Costs',
  props: { size: 'lg' }
});

// Get a template
const template = await getTemplate('card', 'default');

// List all components
const components = await listComponents();
```

### Direct API Usage

```typescript
// Generate a success badge
const badge = await shadcnMcpApi.generateBadge('success', 'Connected');

// Generate a card with custom content
const card = await shadcnMcpApi.generateCard(
  'Cost Analysis',
  'Monthly spending overview',
  '<p>Your costs have decreased by 15%</p>'
);

// Generate a progress bar
const progress = await shadcnMcpApi.generateProgress(75, { className: 'w-full' });
```

## 🎨 Theme Integration

### Theme Provider Setup

```tsx
import { ThemeProvider } from '@/components/theme-provider';

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="costsense-ui-theme">
      {/* Your app content */}
    </ThemeProvider>
  );
}
```

### Using Theme Context

```tsx
import { useTheme } from '@/components/theme-provider';

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <Button
      variant="outline"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      Toggle Theme
    </Button>
  );
}
```

## 🧪 Component Showcase

Access the interactive component showcase at:
```
http://localhost:3000/components
```

This page demonstrates:
- All available component variants
- Interactive examples
- Theme switching capabilities
- Real-time component generation

## ⚙️ Configuration

### Backend Requirements

Add to `backend/requirements.txt`:
```txt
# Already included in main requirements.txt
fastapi==0.104.1
pydantic==2.5.0
```

### Frontend Dependencies

Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "tailwindcss-animate": "^1.0.7"
  }
}
```

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ... other colors
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## 🔍 Health Monitoring

### Server Health Check

```http
GET /api/v1/mcp/shadcn/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "shadcn-mcp-server", 
  "version": "1.0.0",
  "components_available": 7,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Frontend Health Check

```typescript
const checkMcpHealth = async () => {
  try {
    const health = await shadcnMcpApi.healthCheck();
    console.log(`MCP Server: ${health.status} - ${health.components_available} components available`);
  } catch (error) {
    console.error('MCP Server unavailable:', error);
  }
};
```

## 🚀 Production Deployment

### Environment Variables

```bash
# Backend .env
MCP_ENABLED=true
SHADCN_COMPONENTS_PATH=/app/frontend/src/components/ui

# Frontend .env
VITE_MCP_ENABLED=true
VITE_API_URL=http://localhost:8000
```

### Docker Configuration

The MCP server is automatically included in the existing Docker setup:

```yaml
# docker-compose.yml
services:
  backend:
    # ... existing configuration
    environment:
      - MCP_ENABLED=true
```

## 🎯 Use Cases

### 1. Dynamic Dashboard Generation
```typescript
// Generate dashboard cards based on metrics
const generateMetricCard = async (title: string, value: string, trend: 'up' | 'down') => {
  return await shadcnMcpApi.generateCard(
    title,
    `Current value: ${value}`,
    `<Badge variant="${trend === 'up' ? 'success' : 'warning'}">${trend}</Badge>`
  );
};
```

### 2. Alert System Integration
```typescript
// Generate alerts based on cost thresholds
const generateCostAlert = async (severity: 'warning' | 'destructive', message: string) => {
  return await shadcnMcpApi.generateAlert(
    severity,
    'Cost Alert',
    message
  );
};
```

### 3. Real-time Progress Tracking
```typescript
// Update progress bars for analysis tasks
const updateAnalysisProgress = async (progress: number) => {
  return await shadcnMcpApi.generateProgress(progress, {
    className: 'w-full h-2'
  });
};
```

## 🐛 Troubleshooting

### Common Issues

1. **Component Not Found**
   ```
   Error: Component 'custom-button' not found
   ```
   **Solution**: Use `listComponents()` to see available components

2. **Invalid Variant**
   ```
   Error: Variant 'custom' not available for button
   ```
   **Solution**: Use `getComponentVariants()` to see valid variants

3. **MCP Server Unavailable**
   ```
   Error: connect ECONNREFUSED 127.0.0.1:8000
   ```
   **Solution**: Ensure backend server is running

### Debug Mode

Enable debug logging:
```typescript
// Add to your app initialization
if (import.meta.env.DEV) {
  shadcnMcpApi.interceptors.request.use(config => {
    console.log('MCP Request:', config);
    return config;
  });
}
```

## 📚 Examples

### Complete Integration Example

```tsx
import React, { useState } from 'react';
import { useShadcnMcp } from '@/services/shadcnMcpApi';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function ComponentGenerator() {
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const { generateComponent } = useShadcnMcp();

  const handleGenerateButton = async () => {
    const component = await generateComponent({
      name: 'button',
      variant: 'default',
      children: 'Generated Button',
      props: { size: 'lg' }
    });
    setGeneratedCode(component.code);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Component Generator</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={handleGenerateButton}>
          Generate Button Component
        </Button>
        
        {generatedCode && (
          <pre className="bg-muted p-4 rounded-md overflow-x-auto">
            <code>{generatedCode}</code>
          </pre>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 🎉 Success!

The Shadcn MCP Server is now fully integrated into your CostSense AI platform, providing:

- ✅ **Dynamic UI Generation**: Create components via API calls
- ✅ **Theme Support**: Seamless dark/light mode switching  
- ✅ **Type Safety**: Full TypeScript integration
- ✅ **Production Ready**: Docker deployment and health monitoring
- ✅ **Interactive Showcase**: Component library at `/components`

Visit the showcase page to explore all available components and their variants!