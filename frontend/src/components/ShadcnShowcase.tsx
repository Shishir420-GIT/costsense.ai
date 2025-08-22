import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertCircle, CheckCircle, Info, Zap, TrendingUp } from 'lucide-react';

const ShadcnShowcase: React.FC = () => {
  const [progressValue, setProgressValue] = useState(75);

  return (
    <div className="space-y-8 p-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Shadcn UI Component Showcase</h2>
        <p className="text-muted-foreground">Interactive demonstration of available UI components</p>
      </div>

      {/* Cards Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="mr-2 h-5 w-5" />
              Metric Card
            </CardTitle>
            <CardDescription>Sample metric display</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$12,450</div>
            <p className="text-sm text-muted-foreground">Monthly savings</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Progress Tracking</CardTitle>
            <CardDescription>Cost optimization progress</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={progressValue} />
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{progressValue}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Overview</CardTitle>
            <CardDescription>System health indicators</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">AI Agents</span>
              <Badge variant="success">Online</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Data Sync</span>
              <Badge variant="warning">Pending</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Analysis</span>
              <Badge variant="default">Running</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Buttons Section */}
      <Card>
        <CardHeader>
          <CardTitle>Button Variants</CardTitle>
          <CardDescription>Different button styles and states</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button variant="default">Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex flex-wrap gap-3 mt-4">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">
              <Zap className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Badges Section */}
      <Card>
        <CardHeader>
          <CardTitle>Badge Variants</CardTitle>
          <CardDescription>Status indicators and labels</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Badge variant="default">Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="destructive">Destructive</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge variant="success">Success</Badge>
            <Badge variant="warning">Warning</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Section */}
      <div className="space-y-4">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Information</AlertTitle>
          <AlertDescription>
            This is a general information alert with default styling.
          </AlertDescription>
        </Alert>

        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Warning</AlertTitle>
          <AlertDescription>
            This alert warns about potential cost optimization opportunities.
          </AlertDescription>
        </Alert>

        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            This alert indicates a critical system error that needs attention.
          </AlertDescription>
        </Alert>

        <Alert variant="success">
          <CheckCircle className="h-4 w-4" />
          <AlertTitle>Success</AlertTitle>
          <AlertDescription>
            Optimization recommendations have been successfully applied.
          </AlertDescription>
        </Alert>
      </div>

      {/* Form Elements Section */}
      <Card>
        <CardHeader>
          <CardTitle>Form Elements</CardTitle>
          <CardDescription>Input fields and form controls</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="Enter your email" 
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">Budget Limit</Label>
              <Input 
                id="budget" 
                type="number" 
                placeholder="1000" 
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="query">Analysis Query</Label>
            <Input 
              id="query" 
              placeholder="Enter your cost analysis query..." 
              className="w-full"
            />
          </div>
        </CardContent>
      </Card>

      {/* Interactive Demo */}
      <Card>
        <CardHeader>
          <CardTitle>Interactive Demo</CardTitle>
          <CardDescription>Test component interactions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <Button 
              onClick={() => setProgressValue(Math.min(100, progressValue + 10))}
              disabled={progressValue >= 100}
            >
              Increase Progress
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setProgressValue(Math.max(0, progressValue - 10))}
              disabled={progressValue <= 0}
            >
              Decrease Progress
            </Button>
            <Button 
              variant="secondary" 
              onClick={() => setProgressValue(50)}
            >
              Reset
            </Button>
          </div>
          <Progress value={progressValue} className="w-full" />
          <p className="text-sm text-muted-foreground">
            Current progress: {progressValue}%
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default ShadcnShowcase;