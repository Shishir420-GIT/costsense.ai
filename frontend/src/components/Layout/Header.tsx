import React from 'react';
import { Menu, Bell, Settings, User, Wifi, WifiOff } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useAgentStore } from '@/store/agentStore';

const Header: React.FC = () => {
  const { sidebarOpen, setSidebarOpen, systemHealth } = useAppStore();
  const { isConnected, agentStatus } = useAgentStore();

  const getHealthBadge = () => {
    if (!systemHealth) return 'bg-gray-500';
    
    switch (systemHealth.status) {
      case 'healthy':
        return 'bg-green-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-yellow-500';
    }
  };

  const getAgentHealthBadge = () => {
    if (!agentStatus) return 'bg-gray-500';
    
    switch (agentStatus.overall_health) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md hover:bg-gray-100 transition-colors"
          >
            <Menu className="h-5 w-5 text-gray-500" />
          </button>
          
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-semibold text-gray-900">
              CostSense AI
            </h1>
            <span className="text-sm text-gray-500">|</span>
            <span className="text-sm text-gray-600">Azure Cost Optimization</span>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-500" />
            )}
            <span className="text-xs text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* System Health */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getHealthBadge()}`}></div>
            <span className="text-xs text-gray-600">System</span>
          </div>

          {/* Agent Health */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getAgentHealthBadge()}`}></div>
            <span className="text-xs text-gray-600">
              Agents ({agentStatus?.healthy_agents || 0}/{agentStatus?.total_agents || 0})
            </span>
          </div>

          {/* Notifications */}
          <button className="p-2 rounded-md hover:bg-gray-100 transition-colors relative">
            <Bell className="h-5 w-5 text-gray-500" />
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
              3
            </span>
          </button>

          {/* Settings */}
          <button className="p-2 rounded-md hover:bg-gray-100 transition-colors">
            <Settings className="h-5 w-5 text-gray-500" />
          </button>

          {/* User Menu */}
          <button className="p-2 rounded-md hover:bg-gray-100 transition-colors">
            <User className="h-5 w-5 text-gray-500" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;