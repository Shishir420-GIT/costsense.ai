import axios from 'axios';
import { toast } from 'react-hot-toast';

const MCP_API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ComponentRequest {
  name: string;
  variant?: string;
  props?: Record<string, any>;
  children?: string;
}

interface ComponentResponse {
  name: string;
  code: string;
  imports: string[];
  dependencies: string[];
  timestamp: string;
}

interface ComponentTemplate {
  component: string;
  variant: string;
  template: string;
  imports: string[];
  dependencies: string[];
  usage_example: string;
  timestamp: string;
}

interface ComponentVariants {
  component: string;
  variants: string[];
  sizes: string[];
  dependencies: string[];
  imports: string[];
  timestamp: string;
}

// Create axios instance for MCP API
const mcpApi = axios.create({
  baseURL: `${MCP_API_BASE_URL}/api/v1/mcp/shadcn`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
mcpApi.interceptors.request.use(
  (config) => {
    console.log(`📡 MCP API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ MCP Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
mcpApi.interceptors.response.use(
  (response) => {
    console.log(`✅ MCP API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ MCP Response Error:', error);
    const message = error.response?.data?.detail || error.message || 'MCP API error occurred';
    toast.error(`Shadcn MCP: ${message}`);
    return Promise.reject(error);
  }
);

// MCP API methods
export const shadcnMcpApi = {
  // List all available components
  listComponents: async (): Promise<{ components: Record<string, any>; total: number; timestamp: string }> => {
    const response = await mcpApi.get('/components');
    return response.data;
  },

  // Get component variants
  getComponentVariants: async (componentName: string): Promise<ComponentVariants> => {
    const response = await mcpApi.get(`/components/${componentName}/variants`);
    return response.data;
  },

  // Generate a component
  generateComponent: async (request: ComponentRequest): Promise<ComponentResponse> => {
    const response = await mcpApi.post('/components/generate', request);
    return response.data;
  },

  // Get component template
  getComponentTemplate: async (componentName: string, variant: string = 'default'): Promise<ComponentTemplate> => {
    const response = await mcpApi.get(`/components/${componentName}/template`, {
      params: { variant }
    });
    return response.data;
  },

  // Batch generate components
  batchGenerateComponents: async (requests: ComponentRequest[]): Promise<ComponentResponse[]> => {
    const response = await mcpApi.post('/components/batch-generate', requests);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; service: string; version: string; components_available: number; timestamp: string }> => {
    const response = await mcpApi.get('/health');
    return response.data;
  },

  // Helper methods for common components
  generateButton: async (variant: string = 'default', text: string = 'Click me', props?: Record<string, any>) => {
    return shadcnMcpApi.generateComponent({
      name: 'button',
      variant,
      children: text,
      props
    });
  },

  generateCard: async (title?: string, description?: string, content?: string) => {
    const children = title || description || content ? 
      `${title ? `<CardTitle>${title}</CardTitle>` : ''}
       ${description ? `<CardDescription>${description}</CardDescription>` : ''}
       ${content ? `<CardContent>${content}</CardContent>` : ''}` : undefined;

    return shadcnMcpApi.generateComponent({
      name: 'card',
      children
    });
  },

  generateBadge: async (variant: string = 'default', text: string = 'Badge', props?: Record<string, any>) => {
    return shadcnMcpApi.generateComponent({
      name: 'badge',
      variant,
      children: text,
      props
    });
  },

  generateAlert: async (variant: string = 'default', title?: string, description?: string) => {
    const children = title || description ?
      `${title ? `<AlertTitle>${title}</AlertTitle>` : ''}
       ${description ? `<AlertDescription>${description}</AlertDescription>` : ''}` : undefined;

    return shadcnMcpApi.generateComponent({
      name: 'alert',
      variant,
      children
    });
  },

  generateProgress: async (value: number = 50, props?: Record<string, any>) => {
    return shadcnMcpApi.generateComponent({
      name: 'progress',
      props: { value, ...props }
    });
  }
};

// Hook for component generation
export const useShadcnMcp = () => {
  const generateComponent = async (request: ComponentRequest) => {
    try {
      const response = await shadcnMcpApi.generateComponent(request);
      toast.success(`Generated ${request.name} component`);
      return response;
    } catch (error) {
      console.error('Failed to generate component:', error);
      throw error;
    }
  };

  const getTemplate = async (componentName: string, variant: string = 'default') => {
    try {
      const template = await shadcnMcpApi.getComponentTemplate(componentName, variant);
      toast.success(`Retrieved ${componentName} template`);
      return template;
    } catch (error) {
      console.error('Failed to get template:', error);
      throw error;
    }
  };

  const listComponents = async () => {
    try {
      const components = await shadcnMcpApi.listComponents();
      return components;
    } catch (error) {
      console.error('Failed to list components:', error);
      throw error;
    }
  };

  return {
    generateComponent,
    getTemplate,
    listComponents,
    ...shadcnMcpApi
  };
};

export default shadcnMcpApi;