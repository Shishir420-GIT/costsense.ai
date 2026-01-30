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
  Settings,
  RefreshCw,
  Server,
  Database,
  Cloud,
  Shield
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
import TrustedAdvisorTable from '@/components/TrustedAdvisorTable';
import { useCostStore } from '@/store/costStore';
import { useAgentStore } from '@/store/agentStore';
import CostTrendChart from '@/components/Charts/CostTrendChart';
import ServiceBreakdownChart from '@/components/Charts/ServiceBreakdownChart';

const EnhancedDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30_days');
  const [activeView, setActiveView] = useState('chat'); // Temporarily set to chat to show it immediately
  const [logsEnabled, setLogsEnabled] = useState(true);
  const [remediationMode, setRemediationMode] = useState(false);
  
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
    return costSummary.top_services.slice(0, 5).map(([service, cost]: [string, number]) => ({
      service,
      cost,
      percentage: (cost / total) * 100
    }));
  };

  // Mock data for detailed resource table
  const resourceData = [
    { id: 'i-1234567890abcdef0', name: 'web-server-01', type: 't3.medium', region: 'us-east-1', cost: 87.20, utilization: 45, recommendation: 'Downsize' },
    { id: 'i-0987654321fedcba0', name: 'api-server-01', type: 'm5.large', region: 'us-east-1', cost: 142.40, utilization: 78, recommendation: 'Optimal' },
    { id: 'i-abcdef1234567890', name: 'database-01', type: 'r5.xlarge', region: 'us-west-2', cost: 284.80, utilization: 92, recommendation: 'Consider Reserved' },
    { id: 'i-fedcba0987654321', name: 'cache-server-01', type: 't3.small', region: 'us-east-1', cost: 21.80, utilization: 23, recommendation: 'Terminate' },
  ];

  return (
    <TooltipProvider>
      <div className="min-h-screen gradient-bg-light dark:gradient-bg-light p-6">
        <div className="mx-auto max-w-7xl space-y-8">

          {/* Enhanced Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
                Cost Intelligence Center
              </h1>
              <p className="text-lg text-slate-600 dark:text-slate-400 mt-2">
                Advanced Azure cost optimization and infrastructure analytics
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-[160px]">
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
                  <p>Refresh all data</p>
                </TooltipContent>
              </Tooltip>
              
              <ThemeToggle />
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={logsEnabled ? "default" : "outline"} 
                    size="icon"
                    onClick={() => setLogsEnabled(!logsEnabled)}
                  >
                    <Settings className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{logsEnabled ? 'Disable' : 'Enable'} Analysis Logs</p>
                </TooltipContent>
              </Tooltip>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={remediationMode ? "destructive" : "outline"} 
                    size="icon"
                    onClick={() => setRemediationMode(!remediationMode)}
                  >
                    <Shield className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{remediationMode ? 'Exit' : 'Enter'} Remediation Mode</p>
                </TooltipContent>
              </Tooltip>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Quick Actions</DropdownMenuLabel>
                  <DropdownMenuItem>
                    <Download className="mr-2 h-4 w-4" />
                    Export Dashboard
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    Configuration
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

          {/* Status Bar */}
          <div className="flex items-center justify-between rounded-lg border bg-white/60 backdrop-blur-sm p-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <Separator orientation="vertical" className="h-6" />
              <div className="text-sm text-slate-600 dark:text-slate-400">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
              {remediationMode && (
                <>
                  <Separator orientation="vertical" className="h-6" />
                  <Badge variant="destructive" className="animate-pulse">
                    🛠️ Remediation Mode Active
                  </Badge>
                </>
              )}
              {logsEnabled && (
                <>
                  <Separator orientation="vertical" className="h-6" />
                  <Badge variant="outline">
                    📝 Logs Enabled
                  </Badge>
                </>
              )}
            </div>
            <Badge variant={isConnected ? "default" : "destructive"}>
              {agentStatus ? `${agentStatus.healthy_agents}/${agentStatus.total_agents} Agents Active` : 'Checking...'}
            </Badge>
          </div>

          {/* Available Tasks/Portal Functions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 hover:shadow-xl transition-all cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-blue-500 p-3">
                    <TrendingUp className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Cost Analysis</h3>
                    <p className="text-sm text-slate-600">Azure Advisor insights</p>
                    <Badge variant="outline" className="mt-2">Ready</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 hover:shadow-xl transition-all cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-green-500 p-3">
                    <Server className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Infrastructure Review</h3>
                    <p className="text-sm text-slate-600">Resource optimization analysis</p>
                    <Badge variant="outline" className="mt-2">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 hover:shadow-xl transition-all cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-purple-500 p-3">
                    <Database className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Component Advisor</h3>
                    <p className="text-sm text-slate-600">AI-powered Azure recommendations</p>
                    <Badge variant="outline" className="mt-2">Chat Available</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 hover:shadow-xl transition-all cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-orange-500 p-3">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Cleanup Scripts</h3>
                    <p className="text-sm text-slate-600">Automated remediation tools</p>
                    <Badge variant={remediationMode ? "default" : "secondary"} className="mt-2">
                      {remediationMode ? "Active" : "Standby"}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Metrics Cards */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-indigo-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Total Spend</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {costSummary ? formatCurrency(costSummary.total_cost) : '$--'}
                    </p>
                    <div className="flex items-center mt-2">
                      <TrendingDown className="h-4 w-4 text-green-600 mr-1" />
                      <Badge variant="secondary" className="text-xs">
                        5.2% vs last period
                      </Badge>
                    </div>
                  </div>
                  <div className="rounded-full bg-blue-500 p-3">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-amber-50 to-orange-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Savings Opportunity</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {infrastructureAnalysis ? 
                        formatCurrency(
                          (infrastructureAnalysis.ec2_analysis?.potential_monthly_savings || 0) +
                          (infrastructureAnalysis.s3_analysis?.buckets?.length * 20 || 0)
                        ) : 
                        '$--'
                      }
                    </p>
                    <Badge variant="outline" className="text-xs mt-2">
                      Monthly potential
                    </Badge>
                  </div>
                  <div className="rounded-full bg-amber-500 p-3">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-emerald-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Active Resources</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {infrastructureAnalysis?.ec2_analysis?.total_instances || '--'}
                    </p>
                    <p className="text-sm text-slate-600 mt-2">
                      EC2 instances monitored
                    </p>
                  </div>
                  <div className="rounded-full bg-green-500 p-3">
                    <Server className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-violet-100">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">AI Optimization</p>
                    <p className="text-3xl font-bold text-slate-900">98%</p>
                    <div className="flex items-center mt-2">
                      <Shield className="h-4 w-4 text-green-600 mr-1" />
                      <Badge variant="secondary" className="text-xs">
                        System Health
                      </Badge>
                    </div>
                  </div>
                  <div className="rounded-full bg-purple-500 p-3">
                    <Activity className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeView} onValueChange={setActiveView} className="space-y-6">
            <TabsList className="grid w-full grid-cols-5 h-auto">
              <TabsTrigger value="overview" className="text-xs md:text-sm">Overview</TabsTrigger>
              <TabsTrigger value="resources" className="text-xs md:text-sm">Resources</TabsTrigger>
              <TabsTrigger value="optimization" className="text-xs md:text-sm">Optimization</TabsTrigger>
              <TabsTrigger value="chat" className="text-xs md:text-sm font-semibold bg-blue-50">💬 AI Chat</TabsTrigger>
              <TabsTrigger value="analytics" className="text-xs md:text-sm">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Cost Trends
                    </CardTitle>
                    <CardDescription>Daily spending analysis over time</CardDescription>
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
                      <div className="h-64 flex items-center justify-center text-slate-500">
                        No cost data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Cloud className="h-5 w-5" />
                      Service Distribution
                    </CardTitle>
                    <CardDescription>Top cost-contributing services</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {loadingCostData ? (
                      <div className="h-64 flex items-center justify-center">
                        <div className="loading-spinner"></div>
                      </div>
                    ) : getServiceCostData().length > 0 ? (
                      <ServiceBreakdownChart data={getServiceCostData()} />
                    ) : (
                      <div className="h-64 flex items-center justify-center text-slate-500">
                        No service data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions & Recommendations */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="border-0 shadow-lg lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Priority Recommendations</CardTitle>
                    <CardDescription>AI-powered optimization suggestions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {infrastructureAnalysis?.ec2_analysis?.instances
                        ?.filter(instance => instance.recommendation !== 'Optimal')
                        .slice(0, 3)
                        .map((instance, index) => (
                          <Alert key={index} className="border-l-4 border-l-orange-500">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle className="text-sm font-medium">
                              {instance.recommendation} - {instance.instance_id}
                            </AlertTitle>
                            <AlertDescription className="text-sm">
                              CPU utilization: {instance.avg_cpu_utilization.toFixed(1)}% 
                              <Badge variant="outline" className="ml-2 text-xs">
                                Est. savings: $50/month
                              </Badge>
                            </AlertDescription>
                          </Alert>
                        ))
                      }
                      
                      {(!infrastructureAnalysis || loadingInfrastructure) && (
                        <div className="flex items-center justify-center py-8">
                          <div className="loading-spinner mr-2"></div>
                          <span className="text-slate-500">Loading recommendations...</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button className="w-full justify-start" variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export Cost Report
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Settings className="mr-2 h-4 w-4" />
                      Configure Budgets
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Shield className="mr-2 h-4 w-4" />
                      Security Audit
                    </Button>
                    <Separator />
                    <Sheet>
                      <SheetTrigger asChild>
                        <Button className="w-full" variant="default">
                          <Database className="mr-2 h-4 w-4" />
                          Detailed Analysis
                        </Button>
                      </SheetTrigger>
                      <SheetContent className="w-[400px] sm:w-[540px]">
                        <SheetHeader>
                          <SheetTitle>Detailed Cost Analysis</SheetTitle>
                          <SheetDescription>
                            Comprehensive breakdown of your cloud spending patterns
                          </SheetDescription>
                        </SheetHeader>
                        <div className="mt-6 space-y-4">
                          <div className="rounded-lg border p-4">
                            <h4 className="font-medium">Cost by Region</h4>
                            <div className="mt-2 space-y-2">
                              <div className="flex justify-between text-sm">
                                <span>us-east-1</span>
                                <span>$1,234.56 (45%)</span>
                              </div>
                              <Progress value={45} className="h-2" />
                              <div className="flex justify-between text-sm">
                                <span>us-west-2</span>
                                <span>$987.43 (35%)</span>
                              </div>
                              <Progress value={35} className="h-2" />
                            </div>
                          </div>
                        </div>
                      </SheetContent>
                    </Sheet>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="resources" className="space-y-6">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle>Resource Inventory</CardTitle>
                  <CardDescription>Detailed view of all monitored resources</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Resource ID</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Region</TableHead>
                        <TableHead>Monthly Cost</TableHead>
                        <TableHead>Utilization</TableHead>
                        <TableHead>Recommendation</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {resourceData.map((resource) => (
                        <TableRow key={resource.id}>
                          <TableCell className="font-mono text-xs">{resource.id}</TableCell>
                          <TableCell className="font-medium">{resource.name}</TableCell>
                          <TableCell>{resource.type}</TableCell>
                          <TableCell>{resource.region}</TableCell>
                          <TableCell>{formatCurrency(resource.cost)}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Progress value={resource.utilization} className="h-2 w-16" />
                              <span className="text-sm">{resource.utilization}%</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge 
                              variant={
                                resource.recommendation === 'Optimal' ? 'default' :
                                resource.recommendation === 'Terminate' ? 'destructive' : 'secondary'
                              }
                            >
                              {resource.recommendation}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="optimization" className="space-y-6">
              <TrustedAdvisorTable />
            </TabsContent>

            <TabsContent value="chat" className="space-y-6">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Azure Component Advisor
                  </CardTitle>
                  <CardDescription>
                    Get AI-powered Azure component recommendations with pricing and architecture solutions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chat Interface */}
                    <div className="lg:col-span-2">
                      <div className="border rounded-lg p-4 h-96 flex flex-col">
                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                          <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                              <Database className="h-4 w-4 text-white" />
                            </div>
                            <div className="bg-gray-100 rounded-lg p-3 text-sm max-w-[80%]">
                              <p>Hi! I'm your Azure Component Advisor. Describe your application requirements and I'll recommend the best Azure components with pricing and top 2 solutions.</p>
                            </div>
                          </div>
                        </div>
                        
                        {/* Input Area */}
                        <div className="border-t pt-4">
                          <div className="flex gap-2">
                            <Input
                              placeholder="Describe your application requirements..."
                              className="flex-1"
                            />
                            <Button size="icon">
                              <Database className="h-4 w-4" />
                            </Button>
                          </div>
                          <p className="text-xs text-gray-500 mt-2">
                            Example: "I need a web application with user authentication, file uploads, and a database"
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions Panel */}
                    <div className="space-y-4">
                      <Card>
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base">Quick Questions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                          <Button variant="outline" className="w-full justify-start text-left h-auto p-3" size="sm">
                            <div>
                              <div className="font-medium">Web Application</div>
                              <div className="text-xs text-muted-foreground">Full-stack web app with database</div>
                            </div>
                          </Button>
                          <Button variant="outline" className="w-full justify-start text-left h-auto p-3" size="sm">
                            <div>
                              <div className="font-medium">API Service</div>
                              <div className="text-xs text-muted-foreground">RESTful API with authentication</div>
                            </div>
                          </Button>
                          <Button variant="outline" className="w-full justify-start text-left h-auto p-3" size="sm">
                            <div>
                              <div className="font-medium">Data Analytics</div>
                              <div className="text-xs text-muted-foreground">Big data processing pipeline</div>
                            </div>
                          </Button>
                          <Button variant="outline" className="w-full justify-start text-left h-auto p-3" size="sm">
                            <div>
                              <div className="font-medium">Mobile Backend</div>
                              <div className="text-xs text-muted-foreground">Serverless mobile app backend</div>
                            </div>
                          </Button>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base">Features</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2 text-sm">
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
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analytics">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle>Advanced Analytics</CardTitle>
                  <CardDescription>Deep insights and forecasting</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-slate-500">
                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Advanced analytics coming soon...</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

      </div>
    </TooltipProvider>
  );
};

export default EnhancedDashboard;