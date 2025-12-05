import React, { useState } from 'react';
import { BarChart3, TrendingDown, DollarSign, Clock, Send, Bot, User } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import api from '@/services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AnalysisMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const CostAnalysis: React.FC = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<AnalysisMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! I\'m your Azure Cost Analyst. Ask me anything about your Azure costs, spending patterns, or cost optimization opportunities.',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!query.trim() || loading) return;

    const userMessage: AnalysisMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await api.post('/api/v1/analyze', {
        query: userMessage.content
      });

      const assistantMessage: AnalysisMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.analysis || 'Analysis completed successfully.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: AnalysisMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const quickQueries = [
    'Analyze my Azure costs for the last month',
    'What are my top spending services?',
    'Show me potential cost savings',
    'Which VMs are underutilized?'
  ];

  return (
    <div className="min-h-screen gradient-bg-light dark:gradient-bg-light p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Azure Cost Analysis
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 mt-2">
            AI-powered cost analysis and insights for your Azure infrastructure
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-lg h-[600px] flex flex-col">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  <CardTitle className="text-lg">Cost Analysis AI</CardTitle>
                </div>
              </CardHeader>

              <CardContent className="p-0 flex flex-col flex-1 overflow-hidden">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.role === 'assistant' && (
                        <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                      )}
                      <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                        <div
                          className={`rounded-lg p-4 text-sm ${
                            message.role === 'user'
                              ? 'bg-blue-500 text-white ml-auto'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {message.role === 'user' ? (
                            <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                          ) : (
                            <div className="prose prose-sm max-w-none prose-headings:font-semibold prose-h1:text-lg prose-h2:text-base prose-h3:text-sm prose-p:leading-relaxed prose-strong:font-semibold prose-ul:my-2 prose-ol:my-2 prose-li:my-1">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          )}
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
                  ))}

                  {loading && (
                    <div className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-gray-100 rounded-lg p-4 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                          Analyzing your Azure costs...
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="border-t p-4">
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleAnalyze();
                    }}
                    className="flex gap-2"
                  >
                    <Input
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Ask about your Azure costs..."
                      className="flex-1"
                      disabled={loading}
                    />
                    <Button type="submit" disabled={loading || !query.trim()}>
                      <Send className="h-4 w-4" />
                    </Button>
                  </form>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Side Panel */}
          <div className="space-y-4">
            {/* Quick Queries */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Quick Queries</CardTitle>
                <CardDescription>Common cost analysis questions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickQueries.map((q, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start text-left h-auto p-3"
                    onClick={() => setQuery(q)}
                    disabled={loading}
                  >
                    <div className="text-sm">{q}</div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Analysis Capabilities */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Analysis Capabilities</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <DollarSign className="h-4 w-4 text-blue-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Cost Breakdown</p>
                    <p className="text-xs text-gray-600">Service and resource-level cost analysis</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <TrendingDown className="h-4 w-4 text-green-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Savings Opportunities</p>
                    <p className="text-xs text-gray-600">Identify underutilized resources</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <BarChart3 className="h-4 w-4 text-purple-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Trend Analysis</p>
                    <p className="text-xs text-gray-600">Historical cost patterns</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <Clock className="h-4 w-4 text-orange-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Forecasting</p>
                    <p className="text-xs text-gray-600">Predict future spending</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Status */}
            <Alert>
              <Badge variant="default" className="mr-2">
                Live
              </Badge>
              <AlertDescription>
                Connected to Azure Cost Optimization AI backend
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostAnalysis;
