const iconService = require('./iconService.cjs');

class GeminiProvider {
  constructor() {
    this.apiKey = process.env.GEMINI_API_KEY;
    this.baseUrl = 'https://generativelanguage.googleapis.com/v1beta';
    this.model = 'gemini-1.5-pro-latest';
    this.maxTokens = 8192;
    this.temperature = 0.1; // Low temperature for consistent technical output
  }

  isConfigured() {
    return Boolean(this.apiKey);
  }

  async validateConfiguration() {
    if (!this.isConfigured()) {
      throw new Error('Gemini API key not configured');
    }

    try {
      const response = await this.makeRequest('/models', 'GET');
      return response.models && Array.isArray(response.models);
    } catch (error) {
      throw new Error(`Gemini validation failed: ${error.message}`);
    }
  }

  async generateDSL(prompt, conversationHistory = []) {
    if (!this.isConfigured()) {
      throw new Error('Gemini API key not configured');
    }

    const systemPrompt = this.buildSystemPrompt();
    const contents = this.buildContents(systemPrompt, prompt, conversationHistory);

    try {
      const response = await this.makeRequest(`/models/${this.model}:generateContent`, 'POST', {
        contents,
        generationConfig: {
          temperature: this.temperature,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: this.maxTokens,
        },
        safetySettings: [
          {
            category: 'HARM_CATEGORY_HARASSMENT',
            threshold: 'BLOCK_MEDIUM_AND_ABOVE'
          },
          {
            category: 'HARM_CATEGORY_HATE_SPEECH',
            threshold: 'BLOCK_MEDIUM_AND_ABOVE'
          }
        ]
      });

      const content = response.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!content) {
        throw new Error('No response generated from Gemini');
      }

      return this.parseResponse(content);

    } catch (error) {
      console.error('[Gemini] API Error:', error.message);
      throw error;
    }
  }

  buildSystemPrompt() {
    return `You are VizCode's AI assistant - a friendly, knowledgeable chatbot that specializes in cloud architecture diagrams.

CORE BEHAVIOR:
- Respond naturally to greetings, questions, and general conversation
- Only generate VizCode DSL when specifically asked to create/design/generate a diagram
- Be helpful, conversational, and maintain context from previous messages
- Ask clarifying questions when needed

WHEN GENERATING DIAGRAMS:
Only create DSL when users explicitly request architecture diagrams with phrases like:
- "Create a diagram of..."
- "Generate an architecture for..."  
- "Design a system with..."
- "Build a diagram showing..."

AVAILABLE ICONS (use exact names from manifest):
AWS: EC2, RDS, Lambda, S3, ElasticLoadBalancing, APIGateway, Aurora, DynamoDB, ElastiCache, CloudFront, CloudWatch, ElasticBeanstalk, SQS, SNS, CloudFormation, IAM, VPC, Route53, etc.
Azure: AppServices, StorageAccounts, KeyVaults, ApplicationGateway, serviceCacheRedis, ContainerInstances, KubernetesServices, etc.
GCP: ComputeEngine, CloudSQL, CloudStorage, CloudLoadBalancing, CloudFunctions, GoogleKubernetesEngine, CloudRunForAnthos, etc.
General: cloud, device

IMPORTANT: Use exact icon names from the manifest. If unsure, use:
- "cloud" for generic cloud services
- "device" for user devices/endpoints
- Closest matching service name

FALLBACK RULES:
- If a service isn't in the available icons, use the closest match or "cloud" for generic services
- Use "device" for generic hardware/endpoints
- Create boxes/rectangles for unlisted services

DSL FORMAT:
Cluster: Production Environment
  Cluster: Public Subnet
    Node: ElasticLoadBalancing [name=Load Balancer]
  Cluster: Private Subnet  
    Node: EC2 [name=Web Server]
    Node: RDS [name=Database]
Load Balancer -> Web Server [arrow=solid, label='HTTPS']
Web Server -> Database [arrow=solid, label='SQL']

RESPONSE FORMAT FOR DIAGRAMS:
Return JSON with exactly this structure:
{
  "dsl": "your DSL code here",
  "explanation": "Brief explanation of the architecture"
}

FOR REGULAR CHAT:
Respond normally as a helpful AI assistant. No special formatting needed.`;
  }

  buildContents(systemPrompt, userPrompt, conversationHistory) {
    const parts = [];

    // Add system prompt
    parts.push({ text: systemPrompt });

    // Add conversation history (last 6 messages to stay within token limits)
    const recentHistory = conversationHistory.slice(-6);
    recentHistory.forEach(msg => {
      parts.push({ text: `${msg.from === 'user' ? 'User' : 'Assistant'}: ${msg.text}` });
    });

    // Add current user prompt
    parts.push({ text: `User: ${userPrompt}` });

    return [{ parts }];
  }

  parseResponse(content) {
    try {
      // Try to parse as JSON first (for diagram responses)
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (parsed.dsl && parsed.explanation) {
          // Return diagram response with proper DSL string
          const dslString = typeof parsed.dsl === 'string' ? parsed.dsl : JSON.stringify(parsed.dsl, null, 2);
          return {
            dsl: iconService.validateAndCorrectDSL(dslString),
            explanation: parsed.explanation
          };
        }
      }
    } catch (e) {
      // Fall back to conversational parsing
    }

    // Check if this looks like DSL content
    const isDSLContent = /^\s*Cluster:/m.test(content) || /Node:/m.test(content);
    
    if (isDSLContent) {
      // Extract DSL from code blocks or plain text
      let dsl = content;
      const codeBlockMatch = content.match(/```(?:vizcode|dsl)?\n?([\s\S]*?)```/);
      if (codeBlockMatch) {
        dsl = codeBlockMatch[1].trim();
      }

      // Clean up any remaining markdown
      dsl = dsl.replace(/^```.*$/gm, '').trim();

      return {
        dsl: iconService.validateAndCorrectDSL(dsl),
        explanation: 'Architecture generated using Google Gemini Pro'
      };
    } else {
      // This is a conversational response, not a diagram
      return {
        dsl: null,
        explanation: content.trim()
      };
    }
  }

  async makeRequest(endpoint, method = 'GET', data = null) {
    const url = `${this.baseUrl}${endpoint}${endpoint.includes('?') ? '&' : '?'}key=${this.apiKey}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'VizCode/1.0'
      }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: { message: response.statusText } }));
        const errorMessage = error.error?.message || error.message || `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  }
}

module.exports = GeminiProvider;