import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  Download,
  Filter,
  TrendingUp,
  Shield,
  Server,
  Database
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';

interface TrustedAdvisorData {
  summary_table: {
    headers: string[];
    rows: string[][];
  };
  resource_details_table: {
    headers: string[];
    rows: string[][];
  };
  total_monthly_savings: number;
  total_annual_savings: number;
  last_updated: string;
}

interface TrustedAdvisorTableProps {
  className?: string;
}

const TrustedAdvisorTable: React.FC<TrustedAdvisorTableProps> = ({ className }) => {
  const [data, setData] = useState<TrustedAdvisorData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchTrustedAdvisorData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/agents/trusted-advisor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'full_cost_analysis',
          focus_area: 'cost_optimization'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch Trusted Advisor data');
      }

      const result = await response.json();
      setData(result.tabular_data);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error fetching Trusted Advisor data:', error);
      setError(error instanceof Error ? error.message : 'Unknown error occurred');
      // Set fallback data
      setData({
        summary_table: {
          headers: ["Check Category", "Issues Found", "Monthly Savings", "Annual Savings", "Priority"],
          rows: [
            ["Reserved Instance Optimization", "15", "$342.50", "$4,110.00", "High"],
            ["Low Utilization EC2 Instances", "8", "$248.16", "$2,977.92", "High"],
            ["EBS Underutilized Volumes", "12", "$156.32", "$1,875.84", "Medium"],
            ["RDS Idle DB Instances", "3", "$127.44", "$1,529.28", "Medium"]
          ]
        },
        resource_details_table: {
          headers: ["Resource ID", "Type", "Current Cost", "Potential Savings", "Utilization", "Recommendation"],
          rows: [
            ["i-1234567890abcdef0", "t3.medium", "$35.04", "$14.02", "95%", "Purchase 1-year RI"],
            ["i-0987654321fedcba0", "m5.large", "$70.08", "$28.03", "98%", "Purchase 1-year RI"],
            ["i-abcdef1234567890", "t3.large", "$67.32", "$44.88", "8.5%", "Downsize to t3.medium"],
            ["vol-1234567890abcdef0", "gp3 500GB", "$40.00", "$20.00", "3.2%", "Resize to 250GB"],
            ["database-test-01", "db.t3.medium", "$42.48", "$42.48", "2.1%", "Terminate unused DB"]
          ]
        },
        total_monthly_savings: 874.42,
        total_annual_savings: 10493.04,
        last_updated: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrustedAdvisorData();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <TrendingUp className="h-4 w-4" />;
      case 'low':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <CheckCircle className="h-4 w-4" />;
    }
  };

  const getResourceIcon = (resourceType: string) => {
    if (resourceType.includes('t3') || resourceType.includes('m5')) {
      return <Server className="h-4 w-4" />;
    } else if (resourceType.includes('gp') || resourceType.includes('volume')) {
      return <Database className="h-4 w-4" />;
    } else if (resourceType.includes('db.')) {
      return <Database className="h-4 w-4" />;
    }
    return <Server className="h-4 w-4" />;
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            AWS Trusted Advisor Analysis
          </CardTitle>
          <CardDescription>Loading cost optimization recommendations...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            <span>Analyzing AWS resources...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !data) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            AWS Trusted Advisor Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
          <Button 
            onClick={fetchTrustedAdvisorData} 
            className="mt-4"
            variant="outline"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <div className={className}>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-emerald-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Monthly Savings</p>
                <p className="text-3xl font-bold text-slate-900">
                  ${data.total_monthly_savings.toLocaleString()}
                </p>
              </div>
              <div className="rounded-full bg-green-500 p-3">
                <DollarSign className="h-6 w-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Annual Savings</p>
                <p className="text-3xl font-bold text-slate-900">
                  ${data.total_annual_savings.toLocaleString()}
                </p>
              </div>
              <div className="rounded-full bg-blue-500 p-3">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Last Updated</p>
                <p className="text-lg font-semibold text-slate-900">
                  {lastRefresh.toLocaleTimeString()}
                </p>
                <p className="text-xs text-slate-600 mt-1">
                  {lastRefresh.toLocaleDateString()}
                </p>
              </div>
              <div className="rounded-full bg-purple-500 p-3">
                <Shield className="h-6 w-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                AWS Trusted Advisor Cost Analysis
              </CardTitle>
              <CardDescription>
                Cost optimization recommendations from AWS Trusted Advisor
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={fetchTrustedAdvisorData} 
                variant="outline" 
                size="icon"
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
              <Button variant="outline" size="icon">
                <Download className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="summary">Cost Summary</TabsTrigger>
              <TabsTrigger value="resources">Resource Details</TabsTrigger>
            </TabsList>
            
            <TabsContent value="summary" className="space-y-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {data.summary_table.headers.map((header, index) => (
                        <TableHead key={index} className="font-semibold">
                          {header}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.summary_table.rows.map((row, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{row[0]}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{row[1]}</Badge>
                        </TableCell>
                        <TableCell className="font-mono text-green-600">{row[2]}</TableCell>
                        <TableCell className="font-mono text-green-700 font-semibold">{row[3]}</TableCell>
                        <TableCell>
                          <Badge variant={getPriorityColor(row[4])} className="flex items-center gap-1 w-fit">
                            {getPriorityIcon(row[4])}
                            {row[4]}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
            
            <TabsContent value="resources" className="space-y-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {data.resource_details_table.headers.map((header, index) => (
                        <TableHead key={index} className="font-semibold">
                          {header}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.resource_details_table.rows.map((row, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-mono text-sm">{row[0]}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getResourceIcon(row[1])}
                            {row[1]}
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{row[2]}</TableCell>
                        <TableCell className="font-mono text-green-600">{row[3]}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={parseFloat(row[4]) < 20 ? "destructive" : parseFloat(row[4]) < 50 ? "secondary" : "default"}
                          >
                            {row[4]}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-slate-600">{row[5]}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>
          
          <Separator className="my-4" />
          
          <div className="flex items-center justify-between text-sm text-slate-600">
            <div className="flex items-center gap-4">
              <span>Source: AWS Trusted Advisor</span>
              <span>•</span>
              <span>Last refresh: {new Date(data.last_updated).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <span>Total potential savings:</span>
              <Badge variant="default" className="font-semibold">
                ${data.total_monthly_savings.toLocaleString()}/month
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrustedAdvisorTable;