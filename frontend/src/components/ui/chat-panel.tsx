import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  MessageCircle, 
  X, 
  Minimize2, 
  Maximize2,
  Bot,
  User,
  DollarSign,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Separator } from '@/components/ui/separator';

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

interface ChatPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ isOpen, onToggle }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! I\'m your AWS Component Advisor. Describe your application requirements and I\'ll recommend the best AWS components with pricing and top solutions.',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
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
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

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
      // Make API call to component recommendation agent
      const response = await fetch('/api/v1/agents/component-advisor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          context: 'component_recommendation'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendation');
      }

      const data = await response.json();
      
      // Parse the response to extract recommendations and solutions
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I\'ve analyzed your requirements and prepared recommendations below.',
        timestamp: new Date(),
        recommendations: data.recommendations || generateMockRecommendations(userMessage.content),
        solutions: data.solutions || generateMockSolutions(userMessage.content)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Fallback with mock data for demonstration
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I\'ve analyzed your requirements and prepared AWS component recommendations with pricing analysis.',
        timestamp: new Date(),
        recommendations: generateMockRecommendations(userMessage.content),
        solutions: generateMockSolutions(userMessage.content)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockRecommendations = (query: string): ComponentRecommendation[] => {
    const isWebApp = query.toLowerCase().includes('web') || query.toLowerCase().includes('app');
    const isDatabase = query.toLowerCase().includes('database') || query.toLowerCase().includes('data');
    const isApi = query.toLowerCase().includes('api') || query.toLowerCase().includes('backend');

    const recommendations: ComponentRecommendation[] = [];

    if (isWebApp) {
      recommendations.push({
        service: 'Amazon EC2',
        component: 't3.medium instance',
        description: 'General purpose compute for web applications',
        pricing: '$0.0416/hour',
        use_case: 'Web application hosting',
        monthly_cost_estimate: 30,
        setup_complexity: 'Low'
      });
      
      recommendations.push({
        service: 'Amazon CloudFront',
        component: 'CDN Distribution',
        description: 'Global content delivery network',
        pricing: '$0.085/GB',
        use_case: 'Static content delivery',
        monthly_cost_estimate: 15,
        setup_complexity: 'Low'
      });
    }

    if (isDatabase || isWebApp) {
      recommendations.push({
        service: 'Amazon RDS',
        component: 'db.t3.micro PostgreSQL',
        description: 'Managed relational database',
        pricing: '$0.018/hour',
        use_case: 'Application database',
        monthly_cost_estimate: 13,
        setup_complexity: 'Low'
      });
    }

    if (isApi || isWebApp) {
      recommendations.push({
        service: 'AWS Lambda',
        component: 'Serverless Functions',
        description: 'Event-driven compute service',
        pricing: '$0.20/1M requests',
        use_case: 'API endpoints & background tasks',
        monthly_cost_estimate: 8,
        setup_complexity: 'Medium'
      });
    }

    recommendations.push({
      service: 'Amazon S3',
      component: 'Standard Storage',
      description: 'Object storage service',
      pricing: '$0.023/GB',
      use_case: 'File storage & backups',
      monthly_cost_estimate: 5,
      setup_complexity: 'Low'
    });

    return recommendations;
  };

  const generateMockSolutions = (query: string): Solution[] => {
    return [
      {
        name: 'Serverless-First Solution',
        architecture: ['AWS Lambda', 'API Gateway', 'DynamoDB', 'S3', 'CloudFront'],
        total_monthly_cost: 45,
        pros: ['Low operational overhead', 'Auto-scaling', 'Pay-per-use pricing'],
        cons: ['Cold start latency', 'Vendor lock-in'],
        implementation_time: '2-3 weeks',
        confidence: 92
      },
      {
        name: 'Traditional EC2 Solution',
        architecture: ['EC2 (t3.medium)', 'RDS PostgreSQL', 'S3', 'CloudFront', 'ALB'],
        total_monthly_cost: 68,
        pros: ['Full control', 'Predictable performance', 'Easy debugging'],
        cons: ['Requires server management', 'Fixed costs'],
        implementation_time: '3-4 weeks',
        confidence: 88
      }
    ];
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

  if (!isOpen) {
    return (
      <Button
        onClick={() => {
          console.log('Chat panel toggle button clicked');
          onToggle();
        }}
        className="fixed bottom-6 right-6 rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all z-50"
        size="icon"
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    );
  }

  return (
    <Card className={`fixed bottom-6 right-6 shadow-2xl border-0 z-50 transition-all duration-300 ${
      isMinimized ? 'h-14' : 'h-96 w-96'
    }`}>
      <CardHeader className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            <CardTitle className="text-sm font-medium">AWS Component Advisor</CardTitle>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-6 w-6 text-white hover:bg-white/20"
            >
              {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="h-6 w-6 text-white hover:bg-white/20"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>

      {!isMinimized && (
        <CardContent className="p-0 flex flex-col h-80">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className="space-y-3">
                  <div className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {message.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                      <div className={`rounded-lg p-3 text-sm ${
                        message.role === 'user' 
                          ? 'bg-blue-500 text-white ml-auto' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <div className="flex items-start justify-between gap-2">
                          <p>{message.content}</p>
                          {message.role === 'assistant' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => copyToClipboard(message.content, message.id)}
                              className="h-5 w-5 opacity-50 hover:opacity-100 flex-shrink-0"
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
                      <p className="text-xs text-gray-500 mt-1 px-3">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Component Recommendations Table */}
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="bg-white border rounded-lg p-3 space-y-3">
                      <h4 className="font-semibold text-sm flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        AWS Component Recommendations
                      </h4>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="text-xs">Service</TableHead>
                            <TableHead className="text-xs">Component</TableHead>
                            <TableHead className="text-xs">Monthly Cost</TableHead>
                            <TableHead className="text-xs">Complexity</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {message.recommendations.map((rec, index) => (
                            <TableRow key={index}>
                              <TableCell className="text-xs font-medium">{rec.service}</TableCell>
                              <TableCell className="text-xs">{rec.component}</TableCell>
                              <TableCell className="text-xs font-mono">
                                ${rec.monthly_cost_estimate}
                              </TableCell>
                              <TableCell className="text-xs">
                                <Badge variant={
                                  rec.setup_complexity === 'Low' ? 'default' :
                                  rec.setup_complexity === 'Medium' ? 'secondary' : 'destructive'
                                } className="text-xs">
                                  {rec.setup_complexity}
                                </Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}

                  {/* Top Solutions */}
                  {message.solutions && message.solutions.length > 0 && (
                    <div className="bg-white border rounded-lg p-3 space-y-3">
                      <h4 className="font-semibold text-sm">Top 2 Architecture Solutions</h4>
                      <div className="space-y-3">
                        {message.solutions.map((solution, index) => (
                          <div key={index} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <h5 className="font-medium text-sm">{solution.name}</h5>
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs">
                                  ${solution.total_monthly_cost}/mo
                                </Badge>
                                <Badge variant="default" className="text-xs">
                                  {solution.confidence}% confidence
                                </Badge>
                              </div>
                            </div>
                            <div className="text-xs text-gray-600 mb-2">
                              <strong>Architecture:</strong> {solution.architecture.join(' → ')}
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div>
                                <strong className="text-green-600">Pros:</strong>
                                <ul className="list-disc list-inside mt-1 space-y-1">
                                  {solution.pros.slice(0, 2).map((pro, i) => (
                                    <li key={i} className="text-gray-600">{pro}</li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <strong className="text-orange-600">Considerations:</strong>
                                <ul className="list-disc list-inside mt-1 space-y-1">
                                  {solution.cons.slice(0, 2).map((con, i) => (
                                    <li key={i} className="text-gray-600">{con}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                            <Separator className="my-2" />
                            <div className="flex justify-between items-center text-xs text-gray-500">
                              <span>Implementation: {solution.implementation_time}</span>
                              <Button variant="ghost" size="icon" className="h-4 w-4">
                                <ExternalLink className="h-3 w-3" />
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
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                      Analyzing requirements...
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </ScrollArea>

          <div className="border-t p-3">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Describe your application requirements..."
                className="flex-1 text-sm"
                disabled={isLoading}
              />
              <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
            <p className="text-xs text-gray-500 mt-1">
              Powered by AWS Component Advisor AI
            </p>
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default ChatPanel;