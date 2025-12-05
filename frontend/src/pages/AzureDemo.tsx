import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, CheckCircle, XCircle, DollarSign, Server, Database } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import api from '@/services/api';

const AzureDemo: React.FC = () => {
  const [demoData, setDemoData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDemoData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/v1/demo-data');
      setDemoData(response.data);
      console.log('Demo data loaded:', response.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load demo data');
      console.error('Error loading demo data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemoData();
  }, []);

  return (
    <div className="min-h-screen gradient-bg-light dark:gradient-bg-light p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Azure Cost Demo Data
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mt-2">
              Comprehensive mock data from Azure Cost Optimization backend
            </p>
          </div>
          <Button onClick={fetchDemoData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
        </div>

        {/* Status Alert */}
        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertTitle>Error Loading Data</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {demoData && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertTitle>{demoData.message}</AlertTitle>
            <AlertDescription>All Azure Cost Optimization mock data is working!</AlertDescription>
          </Alert>
        )}

        {/* Summary Cards */}
        {demoData?.summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Total Monthly Cost</p>
                    <p className="text-3xl font-bold text-slate-900">
                      ${demoData.summary.total_monthly_cost?.toLocaleString()}
                    </p>
                    <Badge variant="secondary" className="mt-2">
                      {demoData.summary.monthly_change}
                    </Badge>
                  </div>
                  <div className="rounded-full bg-blue-500 p-3">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Potential Savings</p>
                    <p className="text-3xl font-bold text-slate-900">
                      ${demoData.summary.potential_savings?.toLocaleString()}
                    </p>
                    <Badge variant="secondary" className="mt-2">
                      Monthly
                    </Badge>
                  </div>
                  <div className="rounded-full bg-green-500 p-3">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Total VMs</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {demoData.summary.total_vms}
                    </p>
                    <p className="text-sm text-slate-600 mt-2">
                      {demoData.summary.total_storage_accounts} Storage Accounts
                    </p>
                  </div>
                  <div className="rounded-full bg-purple-500 p-3">
                    <Server className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Detailed Data Sections */}
        {demoData?.data && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Dashboard Data */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Dashboard Data</CardTitle>
                <CardDescription>Real-time cost overview</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Total Cost:</span>
                    <span className="font-semibold">
                      ${demoData.data.dashboard.total_monthly_cost?.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Monthly Change:</span>
                    <span className="font-semibold">
                      {demoData.data.dashboard.monthly_change_percent?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Top Service:</span>
                    <span className="font-semibold">
                      {demoData.data.dashboard.top_services?.[0]?.[0]}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* VM Data */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Virtual Machines</CardTitle>
                <CardDescription>VM utilization and costs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Total Instances:</span>
                    <span className="font-semibold">
                      {demoData.data.virtual_machines.totalInstances}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Monthly Cost:</span>
                    <span className="font-semibold">
                      ${demoData.data.virtual_machines.totalMonthlyCost?.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Potential Savings:</span>
                    <span className="font-semibold text-green-600">
                      ${demoData.data.virtual_machines.potentialSavings?.toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Storage Data */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Storage Accounts</CardTitle>
                <CardDescription>Storage costs and optimization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Total Accounts:</span>
                    <span className="font-semibold">
                      {demoData.data.storage.totalAccounts}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Monthly Cost:</span>
                    <span className="font-semibold">
                      ${demoData.data.storage.totalMonthlyCost?.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Potential Savings:</span>
                    <span className="font-semibold text-green-600">
                      ${demoData.data.storage.potentialSavings?.toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>AI Recommendations</CardTitle>
                <CardDescription>
                  {demoData.summary?.recommendations_count} active recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {demoData.data.recommendations?.slice(0, 3).map((rec: any, index: number) => (
                    <div key={index} className="border-l-4 border-l-orange-500 pl-3 py-2">
                      <p className="text-sm font-medium">{rec.title}</p>
                      <p className="text-xs text-slate-600">
                        Potential savings: ${rec.savings}/month
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* API Endpoints Reference */}
        {demoData?.api_endpoints && (
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Available API Endpoints</CardTitle>
              <CardDescription>Backend endpoints ready for use</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm font-mono">
                {Object.entries(demoData.api_endpoints).map(([key, value]: [string, any]) => (
                  <div key={key} className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-slate-600">{value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Raw JSON Data (Collapsible) */}
        {demoData && (
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Raw JSON Response</CardTitle>
              <CardDescription>Complete API response data</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-auto max-h-96 text-xs">
                {JSON.stringify(demoData, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AzureDemo;
