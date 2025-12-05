import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  DollarSign,
  ExternalLink,
  Copy,
  Check,
  Database,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  recommendations?: ComponentRecommendation[];
  solutions?: Solution[];
}

interface ComponentRecommendation {
  service: string;
  component: string;
  description: string;
  pricing: string;
  use_case: string;
  monthly_cost_estimate: number;
  setup_complexity: 'Low' | 'Medium' | 'High';
}

interface Solution {
  name: string;
  architecture: string[];
  total_monthly_cost: number;
  pros: string[];
  cons: string[];
  implementation_time: string;
  confidence: number;
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! I\'m your Azure Cost Optimization AI Assistant. I can help you analyze costs, identify savings opportunities, optimize infrastructure, and provide recommendations for your Azure resources. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Check if this is a simple greeting or non-technical query
      const isSimpleQuery = isGreetingOrSimpleQuery(userMessage.content);
      
      if (isSimpleQuery) {
        // Handle simple conversation without calling the API
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: generateSimpleResponse(userMessage.content),
          timestamp: new Date(),
          recommendations: [],
          solutions: []
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
        return;
      }

      // Make API call to Azure analyze endpoint for technical queries
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get analysis');
      }

      const data = await response.json();

      // Parse the response to extract analysis
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.analysis || 'I\'ve analyzed your requirements.',
        timestamp: new Date(),
        recommendations: [],
        solutions: []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Error handling without mock fallback
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error while analyzing your requirements. Please try again or check if the AI service is available.',
        timestamp: new Date(),
        recommendations: [],
        solutions: []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const isGreetingOrSimpleQuery = (query: string): boolean => {
    const lowerQuery = query.toLowerCase().trim();
    const greetingPatterns = [
      /^(hi|hello|hey|hiya|greetings?)$/,
      /^(good\s+(morning|afternoon|evening|day))$/,
      /^(how\s+are\s+you|how\s+do\s+you\s+do)$/,
      /^(what'?s\s+up|sup)$/,
      /^(nice\s+to\s+meet\s+you)$/,
      /^(thank\s+you|thanks|thx)$/,
      /^(bye|goodbye|see\s+you|farewell)$/,
      /^(help|what\s+can\s+you\s+do\??|what\s+are\s+your\s+capabilities\??)$/,
      /^(who\s+are\s+you\??|what\s+are\s+you\??)$/,
      /^(try\s+again|retry|again)$/,
      /^(ok|okay|sure|yes|no)$/
    ];
    
    // Always check patterns regardless of length for simple queries
    return greetingPatterns.some(pattern => pattern.test(lowerQuery));
  };

  const generateSimpleResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase().trim();
    
    if (/^(hi|hello|hey|hiya|greetings?)$/.test(lowerQuery)) {
      return "Hello! I'm your AWS Component Advisor. I can help you design cloud architectures, recommend AWS services, and estimate costs for your projects. What kind of application or system are you planning to build?";
    }
    
    if (/^(good\s+(morning|afternoon|evening|day))$/.test(lowerQuery)) {
      return "Good day! I'm here to help you with AWS architecture recommendations and cost optimization. What project can I assist you with today?";
    }
    
    if (/^(how\s+are\s+you|how\s+do\s+you\s+do)$/.test(lowerQuery)) {
      return "I'm doing great, thank you for asking! I'm ready to help you design efficient and cost-effective AWS solutions. What kind of system are you looking to build?";
    }
    
    if (/^(what'?s\s+up|sup)$/.test(lowerQuery)) {
      return "Not much, just ready to help you architect some awesome AWS solutions! What project are you working on?";
    }
    
    if (/^(thank\s+you|thanks|thx)$/.test(lowerQuery)) {
      return "You're very welcome! Feel free to ask me about any AWS architecture or cost optimization questions you might have.";
    }
    
    if (/^(bye|goodbye|see\s+you|farewell)$/.test(lowerQuery)) {
      return "Goodbye! Feel free to come back anytime you need help with AWS architecture or cost optimization. Have a great day!";
    }
    
    if (/^(help|what\s+can\s+you\s+do|what\s+are\s+your\s+capabilities)$/.test(lowerQuery)) {
      return "I can help you with:\n\n• AWS component recommendations for your applications\n• Architecture design with pros and cons analysis\n• Cost estimation and optimization strategies\n• Implementation complexity assessment\n• Best practices for scalability and security\n\nJust describe your project requirements, and I'll provide detailed recommendations!";
    }
    
    if (/^(who\s+are\s+you\??|what\s+are\s+you\??)$/.test(lowerQuery)) {
      return "I'm your AWS Component Advisor, an AI assistant specialized in cloud architecture and cost optimization. I help you choose the right AWS services, design efficient architectures, and estimate costs for your projects.";
    }
    
    if (/^(try\s+again|retry|again)$/.test(lowerQuery)) {
      return "Sure! I'm ready to help. What would you like me to assist you with? You can ask me about AWS architecture, component recommendations, or cost optimization for your project.";
    }
    
    if (/^(ok|okay|sure|yes|no)$/.test(lowerQuery)) {
      return "Got it! How can I help you with your AWS project today? Feel free to describe what you're trying to build.";
    }
    
    return "I'm here to help you with AWS architecture recommendations and cost optimization. Could you tell me more about the application or system you're planning to build?";
  };

  const handleQuickQuestion = (question: string) => {
    setInputValue(question);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen gradient-bg-light dark:gradient-bg-light p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100 mb-2">
            Azure AI Chat Assistant
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Get AI-powered Azure cost analysis, optimization recommendations, and infrastructure insights
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="border-0 shadow-lg h-[700px] flex flex-col">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                <div className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  <CardTitle className="text-lg">Azure Cost AI Advisor</CardTitle>
                </div>
              </CardHeader>
              
              <CardContent className="p-0 flex flex-col flex-1 overflow-hidden">
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4 max-w-full">
                    {messages.map((message) => (
                      <div key={message.id} className="space-y-4">
                        <div className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          {message.role === 'assistant' && (
                            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                              <Bot className="h-5 w-5 text-white" />
                            </div>
                          )}
                          <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                            <div className={`rounded-lg p-4 text-sm ${
                              message.role === 'user'
                                ? 'bg-blue-500 text-white ml-auto'
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              <div className="flex items-start justify-between gap-2">
                                {message.role === 'user' ? (
                                  <p className="leading-relaxed">{message.content}</p>
                                ) : (
                                  <div className="prose prose-sm max-w-none prose-headings:font-semibold prose-h1:text-lg prose-h2:text-base prose-h3:text-sm prose-p:leading-relaxed prose-strong:font-semibold prose-ul:my-2 prose-ol:my-2 prose-li:my-1">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                      {message.content}
                                    </ReactMarkdown>
                                  </div>
                                )}
                                {message.role === 'assistant' && (
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => copyToClipboard(message.content, message.id)}
                                    className="h-6 w-6 opacity-50 hover:opacity-100 flex-shrink-0"
                                  >
                                    {copiedMessageId === message.id ? (
                                      <Check className="h-3 w-3" />
                                    ) : (
                                      <Copy className="h-3 w-3" />
                                    )}
                                  </Button>
                                )}
                              </div>
                            </div>
                            <p className="text-xs text-gray-500 mt-1 px-4">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                          {message.role === 'user' && (
                            <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                              <User className="h-5 w-5 text-white" />
                            </div>
                          )}
                        </div>

                        {/* Component Recommendations Table */}
                        {message.recommendations && message.recommendations.length > 0 && (
                          <div className="bg-white border rounded-lg p-4 space-y-4 max-w-full overflow-x-auto">
                            <h4 className="font-semibold flex items-center gap-2">
                              <DollarSign className="h-4 w-4" />
                              AWS Component Recommendations
                            </h4>
                            <div className="overflow-x-auto">
                              <Table className="w-full min-w-[600px]">
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Service</TableHead>
                                  <TableHead>Component</TableHead>
                                  <TableHead>Use Case</TableHead>
                                  <TableHead>Monthly Cost</TableHead>
                                  <TableHead>Complexity</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {message.recommendations.map((rec, index) => (
                                  <TableRow key={index}>
                                    <TableCell className="font-medium">{rec.service}</TableCell>
                                    <TableCell>{rec.component}</TableCell>
                                    <TableCell className="text-sm text-gray-600">{rec.use_case}</TableCell>
                                    <TableCell className="font-mono">
                                      ${rec.monthly_cost_estimate}
                                    </TableCell>
                                    <TableCell>
                                      <Badge variant={
                                        rec.setup_complexity === 'Low' ? 'default' :
                                        rec.setup_complexity === 'Medium' ? 'secondary' : 'destructive'
                                      }>
                                        {rec.setup_complexity}
                                      </Badge>
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                              </Table>
                            </div>
                          </div>
                        )}

                        {/* Top Solutions */}
                        {message.solutions && message.solutions.length > 0 && (
                          <div className="bg-white border rounded-lg p-4 space-y-4 max-w-full">
                            <h4 className="font-semibold">Top 2 Architecture Solutions</h4>
                            <div className="grid gap-4 max-w-full">
                              {message.solutions.map((solution, index) => (
                                <div key={index} className="border rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h5 className="font-medium text-lg">{solution.name}</h5>
                                    <div className="flex items-center gap-2">
                                      <Badge variant="outline">
                                        ${solution.total_monthly_cost}/mo
                                      </Badge>
                                      <Badge variant="default">
                                        {solution.confidence}% confidence
                                      </Badge>
                                    </div>
                                  </div>
                                  
                                  <div className="text-sm text-gray-600 mb-3 break-words">
                                    <strong>Architecture:</strong> <span className="break-all">{solution.architecture.join(' → ')}</span>
                                  </div>
                                  
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                    <div>
                                      <strong className="text-green-600 block mb-1">Advantages:</strong>
                                      <ul className="list-disc list-inside space-y-1">
                                        {solution.pros.map((pro, i) => (
                                          <li key={i} className="text-gray-600">{pro}</li>
                                        ))}
                                      </ul>
                                    </div>
                                    <div>
                                      <strong className="text-orange-600 block mb-1">Considerations:</strong>
                                      <ul className="list-disc list-inside space-y-1">
                                        {solution.cons.map((con, i) => (
                                          <li key={i} className="text-gray-600">{con}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  </div>
                                  
                                  <Separator className="my-3" />
                                  <div className="flex justify-between items-center text-sm text-gray-500">
                                    <span>Implementation: {solution.implementation_time}</span>
                                    <Button variant="ghost" size="sm">
                                      <ExternalLink className="h-3 w-3 mr-1" />
                                      Learn More
                                    </Button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {isLoading && (
                      <div className="flex gap-4">
                        <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                        <div className="bg-gray-100 rounded-lg p-4 text-sm">
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                            Analyzing your requirements...
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  <div ref={messagesEndRef} />
                </ScrollArea>

                <div className="border-t p-4">
                  <form onSubmit={handleSubmit} className="flex gap-2">
                    <Input
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="Describe your application requirements..."
                      className="flex-1"
                      disabled={isLoading}
                    />
                    <Button type="submit" disabled={isLoading || !inputValue.trim()}>
                      <Send className="h-4 w-4" />
                    </Button>
                  </form>
                  <p className="text-xs text-gray-500 mt-2">
                    Example: "I need a web application with user authentication, file uploads, and a database"
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Side Panel */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Quick Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handleQuickQuestion("Analyze my Azure costs for the last month")}
                >
                  <div>
                    <div className="font-medium">Cost Analysis</div>
                    <div className="text-xs text-muted-foreground">Monthly spending breakdown</div>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handleQuickQuestion("What are my top cost-saving opportunities?")}
                >
                  <div>
                    <div className="font-medium">Savings Opportunities</div>
                    <div className="text-xs text-muted-foreground">Find cost reduction options</div>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handleQuickQuestion("Show me underutilized VMs")}
                >
                  <div>
                    <div className="font-medium">VM Optimization</div>
                    <div className="text-xs text-muted-foreground">Right-size virtual machines</div>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handleQuickQuestion("Recommend storage tier optimizations")}
                >
                  <div>
                    <div className="font-medium">Storage Optimization</div>
                    <div className="text-xs text-muted-foreground">Optimize storage costs</div>
                  </div>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Features</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Component recommendations
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Cost estimates & pricing
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Architecture solutions
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Implementation guidance
                </div>
              </CardContent>
            </Card>

            <Alert>
              <Database className="h-4 w-4" />
              <AlertDescription>
                Powered by Azure Cost Optimization AI - providing intelligent analysis and recommendations based on your Azure infrastructure and usage patterns.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;