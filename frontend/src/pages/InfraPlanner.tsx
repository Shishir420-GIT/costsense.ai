import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Network, Loader2, DollarSign, Lightbulb, Code2 } from 'lucide-react';

interface InfraPlan {
  description: string;
  dsl_code: string;
  svg_diagram: string;
  services: string[];
  estimated_monthly_cost: number;
  recommendations: string[];
  timestamp: string;
}

export default function InfraPlanner() {
  const [requirements, setRequirements] = useState('');
  const [plan, setPlan] = useState<InfraPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generatePlan = async () => {
    if (!requirements.trim()) {
      setError('Please enter your infrastructure requirements');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/infra-planner/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements: requirements.trim() })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPlan(data);
    } catch (error) {
      console.error('Failed to generate plan:', error);
      setError('Failed to generate infrastructure plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-ey-yellow rounded-lg">
              <Network className="h-8 w-8 text-ey-black" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-ey-black dark:text-white">
                Infrastructure Planner
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                AI-powered Azure architecture design and cost estimation
              </p>
            </div>
          </div>
        </div>

        {/* Input Section */}
        <Card className="mb-6 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-ey-black to-ey-black-light text-ey-yellow">
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5" />
              Describe Your Infrastructure Requirements
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <Textarea
              placeholder="Example: I need a scalable web application with:
- High availability web tier (3+ instances)
- SQL database with read replicas
- Blob storage for static assets and uploads
- Application monitoring and logging
- Secure secrets management"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              className="min-h-[200px] font-mono text-sm mb-4"
            />

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <Button
              onClick={generatePlan}
              disabled={loading || !requirements.trim()}
              className="w-full bg-ey-yellow text-ey-black hover:bg-ey-yellow-dark font-semibold py-6 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Generating Architecture Plan...
                </>
              ) : (
                <>
                  <Network className="mr-2 h-5 w-5" />
                  Generate Architecture Plan
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results Section */}
        {plan && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Architecture Overview */}
            <Card className="shadow-lg">
              <CardHeader className="bg-gradient-to-r from-ey-black to-ey-black-light text-ey-yellow">
                <CardTitle>Architecture Overview</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                  {plan.description}
                </p>

                <div className="space-y-4">
                  {/* Services */}
                  <div>
                    <h3 className="font-semibold text-ey-black dark:text-white mb-3 flex items-center gap-2">
                      <Network className="h-4 w-4 text-ey-yellow" />
                      Azure Services ({plan.services.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {plan.services.map((service, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-yellow-50 dark:bg-yellow-900/20 text-ey-black dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800 rounded-full text-sm font-medium"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Cost Estimate */}
                  <div className="p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-5 w-5 text-ey-yellow" />
                        <span className="font-semibold text-ey-black dark:text-white">
                          Estimated Monthly Cost
                        </span>
                      </div>
                      <span className="text-2xl font-bold text-ey-black dark:text-white">
                        ${plan.estimated_monthly_cost.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                      Estimate based on standard pricing and typical usage
                    </p>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h3 className="font-semibold text-ey-black dark:text-white mb-3 flex items-center gap-2">
                      <Lightbulb className="h-4 w-4 text-ey-yellow" />
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {plan.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <span className="text-ey-yellow mt-0.5">✓</span>
                          <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* DSL Code & Diagram */}
            <Card className="shadow-lg">
              <CardHeader className="bg-gradient-to-r from-ey-black to-ey-black-light text-ey-yellow">
                <CardTitle>Architecture Diagram</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                {/* SVG Diagram */}
                {plan.svg_diagram && (
                  <div className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-auto">
                    <div dangerouslySetInnerHTML={{ __html: plan.svg_diagram }} />
                  </div>
                )}

                {/* DSL Code */}
                <div>
                  <h3 className="font-semibold text-ey-black dark:text-white mb-3 flex items-center gap-2">
                    <Code2 className="h-4 w-4 text-ey-yellow" />
                    Infrastructure Code (DSL)
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs font-mono border border-gray-700">
                    {plan.dsl_code}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Empty State */}
        {!plan && !loading && (
          <Card className="shadow-lg">
            <CardContent className="p-12 text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="p-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-full">
                  <Network className="h-16 w-16 text-ey-yellow" />
                </div>
                <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300">
                  Ready to Design Your Azure Infrastructure
                </h3>
                <p className="text-gray-600 dark:text-gray-400 max-w-md">
                  Describe your infrastructure requirements above, and our AI will generate
                  an optimized Azure architecture with cost estimates and best practices.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
