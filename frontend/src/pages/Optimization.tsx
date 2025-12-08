import React, { useEffect, useState } from 'react';
import { Zap, DollarSign, TrendingDown, CheckCircle, AlertCircle, RefreshCw, Server, Database } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import api from '@/services/api';

interface Recommendation {
  title: string;
  description: string;
  category: string;
  priority: string;
  savingsMonthly: number;
  savingsAnnual: number;
  impact: string;
  effort: string;
  implementationSteps: string[];
  estimatedTimeMinutes?: number;
  resourceType?: string;
  resourceName?: string;
  status?: string;
}

const Optimization: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalSavings, setTotalSavings] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/v1/recommendations');
      setRecommendations(response.data.recommendations || []);
      setTotalSavings(response.data.total_potential_savings || 0);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load recommendations');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const getPriorityColor = (priority: string) => {
    if (!priority) return 'outline';
    switch (priority.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getImpactColor = (impact: string) => {
    if (!impact) return 'text-gray-600';
    switch (impact.toLowerCase()) {
      case 'high':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getCategoryIcon = (category: string) => {
    if (!category) return <Zap className="h-5 w-5" />;
    switch (category.toLowerCase()) {
      case 'compute':
      case 'vm':
        return <Server className="h-5 w-5" />;
      case 'storage':
        return <Database className="h-5 w-5" />;
      case 'cost':
        return <DollarSign className="h-5 w-5" />;
      default:
        return <Zap className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen gradient-bg-light dark:gradient-bg-light p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Azure Cost Optimization
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mt-2">
              AI-powered recommendations to reduce your Azure spending
            </p>
          </div>
          <Button onClick={fetchRecommendations} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Potential Savings</p>
                  <p className="text-3xl font-bold text-slate-900">
                    ${totalSavings.toLocaleString()}
                  </p>
                  <Badge variant="secondary" className="mt-2">Per Month</Badge>
                </div>
                <div className="rounded-full bg-green-500 p-3">
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-yellow-50 to-yellow-100">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Active Recommendations</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {recommendations.length}
                  </p>
                  <Badge variant="secondary" className="mt-2">Ready to Apply</Badge>
                </div>
                <div className="rounded-full bg-ey-yellow p-3">
                  <Zap className="h-6 w-6 text-ey-black" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-gray-50 to-gray-100">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Annual Savings</p>
                  <p className="text-3xl font-bold text-slate-900">
                    ${(totalSavings * 12).toLocaleString()}
                  </p>
                  <Badge variant="secondary" className="mt-2">Projected</Badge>
                </div>
                <div className="rounded-full bg-purple-500 p-3">
                  <TrendingDown className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recommendations List */}
        {loading ? (
          <Card className="border-0 shadow-lg">
            <CardContent className="p-12">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-8 w-8 animate-spin text-blue-500 mr-3" />
                <span className="text-lg text-slate-600">Loading recommendations...</span>
              </div>
            </CardContent>
          </Card>
        ) : recommendations.length === 0 ? (
          <Card className="border-0 shadow-lg">
            <CardContent className="p-12">
              <div className="text-center">
                <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Great job! Your infrastructure is well optimized.
                </h3>
                <p className="text-slate-600">
                  No critical optimization recommendations at this time.
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-blue-100 p-2">
                        {getCategoryIcon(rec.category)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{rec.title}</CardTitle>
                        <CardDescription className="mt-1">{rec.description}</CardDescription>
                      </div>
                    </div>
                    <Badge variant={getPriorityColor(rec.priority)}>
                      {rec.priority}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Monthly Savings</p>
                        <p className="text-xl font-bold text-green-600">
                          ${rec.savingsMonthly?.toLocaleString() || '0'}
                        </p>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Impact</p>
                        <p className={`text-lg font-semibold ${getImpactColor(rec.impact)}`}>
                          {rec.impact || 'N/A'}
                        </p>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Effort</p>
                        <p className="text-lg font-semibold text-purple-600">
                          {rec.effort || 'N/A'}
                        </p>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Category</p>
                        <p className="text-lg font-semibold text-orange-600">
                          {rec.category || 'General'}
                        </p>
                      </div>
                    </div>

                    {/* Implementation Steps */}
                    {rec.implementationSteps && (() => {
                      try {
                        const steps = typeof rec.implementationSteps === 'string'
                          ? JSON.parse(rec.implementationSteps)
                          : rec.implementationSteps;
                        return steps && steps.length > 0 && (
                          <>
                            <Separator />
                            <div>
                              <h4 className="text-sm font-semibold text-slate-900 mb-2">
                                Implementation Steps:
                              </h4>
                              <ol className="space-y-2">
                                {steps.map((step: string, stepIndex: number) => (
                                  <li key={stepIndex} className="flex items-start gap-2 text-sm text-slate-700">
                                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-semibold">
                                      {stepIndex + 1}
                                    </span>
                                    <span>{step}</span>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          </>
                        );
                      } catch (e) {
                        return null;
                      }
                    })()}

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Apply Recommendation
                      </Button>
                      <Button variant="outline" size="sm">
                        Learn More
                      </Button>
                      <Button variant="ghost" size="sm">
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Info Alert */}
        <Alert>
          <Zap className="h-4 w-4" />
          <AlertDescription>
            These recommendations are generated by analyzing your Azure infrastructure usage patterns,
            cost trends, and industry best practices. Implementing these changes can significantly reduce
            your monthly Azure spending.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
};

export default Optimization;
