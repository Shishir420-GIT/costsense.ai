import React, { useEffect, useState } from 'react';
import { 
  DollarSign, 
  TrendingDown, 
  TrendingUp, 
  Zap,
  Activity,
  AlertCircle,
  CheckCircle,
  Calendar,
  Filter,
  Download,
  MoreVertical,
  Info,
  ChevronDown,
  Settings,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip';
import { Separator } from '@/components/ui/separator';
import { 
  Sheet, 
  SheetContent, 
  SheetDescription, 
  SheetHeader, 
  SheetTitle, 
  SheetTrigger 
} from '@/components/ui/sheet';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { useCostStore } from '@/store/costStore';
import { useAgentStore } from '@/store/agentStore';
import CostTrendChart from '@/components/Charts/CostTrendChart';
import ServiceBreakdownChart from '@/components/Charts/ServiceBreakdownChart';

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30_days');
  const [selectedTab, setSelectedTab] = useState('overview');
  
  const { 
    costSummary, 
    infrastructureAnalysis, 
    fetchCostData, 
    fetchInfrastructureAnalysis,
    loadingCostData,
    loadingInfrastructure 
  } = useCostStore();
  
  const { 
    agentStatus, 
    fetchAgentStatus,
    isConnected 
  } = useAgentStore();

  useEffect(() => {
    fetchCostData(timeRange);
    fetchInfrastructureAnalysis();
    fetchAgentStatus();
  }, [timeRange]);

  const handleRefreshData = () => {
    fetchCostData(timeRange);
    fetchInfrastructureAnalysis();
    fetchAgentStatus();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getServiceCostData = () => {
    if (!costSummary?.top_services) return [];
    
    const total = costSummary.total_cost;
    return costSummary.top_services.slice(0, 5).map(([service, cost]) => ({
      service,
      cost,
      percentage: (cost / total) * 100
    }));
  };

  return (
    <TooltipProvider>
      <div className="space-y-6">
        {/* Enhanced Header with Controls */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Cost Analytics Dashboard</h1>
            <p className="text-muted-foreground">Real-time Azure cost optimization insights and recommendations</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[140px]">
                <Calendar className="mr-2 h-4 w-4" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7_days">Last 7 days</SelectItem>
                <SelectItem value="30_days">Last 30 days</SelectItem>
                <SelectItem value="90_days">Last 90 days</SelectItem>
                <SelectItem value="1_year">Last year</SelectItem>
              </SelectContent>
            </Select>
            
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={handleRefreshData}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Refresh data</p>
              </TooltipContent>
            </Tooltip>
            
            <ThemeToggle />
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuItem>
                  <Download className="mr-2 h-4 w-4" />
                  Export Report
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Configure Alerts
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <Filter className="mr-2 h-4 w-4" />
                  Advanced Filters
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex-shrink-0">
              <DollarSign className="h-8 w-8 text-primary" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Total Spend (30d)</p>
              <p className="text-2xl font-semibold">
                {costSummary ? formatCurrency(costSummary.total_cost) : '$--'}
              </p>
              {!loadingCostData && (
                <div className="flex items-center text-sm text-green-600 mt-1">
                  <TrendingDown className="h-4 w-4 mr-1" />
                  <Badge variant="success" className="text-xs">5.2% vs last period</Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex-shrink-0">
              <Zap className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Potential Savings</p>
              <p className="text-2xl font-semibold">
                {infrastructureAnalysis ? 
                  formatCurrency(
                    (infrastructureAnalysis.ec2_analysis?.potential_monthly_savings || 0) +
                    (infrastructureAnalysis.s3_analysis?.buckets?.length * 20 || 0)
                  ) : 
                  '$--'
                }
              </p>
              {!loadingInfrastructure && (
                <Badge variant="warning" className="text-xs mt-1">
                  Monthly optimization opportunity
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex-shrink-0">
              <Activity className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Active Resources</p>
              <p className="text-2xl font-semibold">
                {infrastructureAnalysis?.ec2_analysis?.total_instances || '--'}
              </p>
              <p className="text-sm text-muted-foreground">
                EC2 instances monitored
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex-shrink-0">
              {isConnected ? (
                <CheckCircle className="h-8 w-8 text-green-600" />
              ) : (
                <AlertCircle className="h-8 w-8 text-red-600" />
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">AI Agents</p>
              <p className="text-2xl font-semibold">
                {agentStatus ? `${agentStatus.healthy_agents}/${agentStatus.total_agents}` : '--'}
              </p>
              <Badge variant={isConnected ? 'success' : 'destructive'} className="text-xs mt-1">
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Trends</CardTitle>
            <CardDescription>Daily spending over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingCostData ? (
              <div className="h-64 flex items-center justify-center">
                <div className="loading-spinner"></div>
              </div>
            ) : costSummary?.daily_costs ? (
              <CostTrendChart 
                data={costSummary.daily_costs}
                width={400}
                height={300}
              />
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No cost data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Service Breakdown Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Service Breakdown</CardTitle>
            <CardDescription>Top spending services this month</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingCostData ? (
              <div className="h-64 flex items-center justify-center">
                <div className="loading-spinner"></div>
              </div>
            ) : getServiceCostData().length > 0 ? (
              <ServiceBreakdownChart data={getServiceCostData()} />
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No service data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Top Recommendations</CardTitle>
          <CardDescription>AI-powered cost optimization suggestions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {infrastructureAnalysis?.ec2_analysis?.instances
              ?.filter(instance => instance.recommendation !== 'Optimal')
              .slice(0, 3)
              .map((instance, index) => (
                <Alert key={index} variant="warning">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>EC2 Instance Optimization</AlertTitle>
                  <AlertDescription>
                    {instance.recommendation} for instance {instance.instance_id}
                    (CPU: {instance.avg_cpu_utilization.toFixed(1)}%)
                    <div className="mt-2">
                      <Badge variant="outline" className="text-xs">
                        Potential savings: ~$50/month
                      </Badge>
                    </div>
                  </AlertDescription>
                </Alert>
              ))
            }
            
            {(!infrastructureAnalysis || loadingInfrastructure) && (
              <div className="flex items-center justify-center py-8">
                <div className="loading-spinner mr-2"></div>
                <span className="text-muted-foreground">Loading recommendations...</span>
              </div>
            )}
            
            {infrastructureAnalysis && 
             !loadingInfrastructure && 
             !infrastructureAnalysis.ec2_analysis?.instances?.some(i => i.recommendation !== 'Optimal') && (
              <div className="text-center py-8 text-muted-foreground">
                No optimization recommendations at this time
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Agent Status */}
      {agentStatus && (
        <Card>
          <CardHeader>
            <CardTitle>AI Agent Status</CardTitle>
            <CardDescription>Real-time status of cost optimization agents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(agentStatus.agents).map(([agentName, status]) => (
                <div key={agentName} className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                  <div className={`w-3 h-3 rounded-full ${
                    status === 'healthy' ? 'bg-green-400' : 'bg-red-400'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium capitalize">
                      {agentName.replace('_', ' ')}
                    </p>
                    <Badge 
                      variant={status === 'healthy' ? 'success' : 'destructive'} 
                      className="text-xs"
                    >
                      {status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      </div>
    </TooltipProvider>
  );
};

export default Dashboard;