import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  TrendingDown, 
  Zap, 
  FileText, 
  Settings,
  Bot,
  DollarSign,
  BarChart3,
  ChevronLeft,
  MessageCircle
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';

interface NavItem {
  to: string;
  icon: React.ElementType;
  label: string;
  badge?: string;
}

const navItems: NavItem[] = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/cost-analysis', icon: BarChart3, label: 'Cost Analysis' },
  { to: '/optimization', icon: Zap, label: 'Optimization', badge: 'AI' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/chat', icon: MessageCircle, label: 'AI Chat', badge: 'NEW' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

const Sidebar: React.FC = () => {
  const { sidebarOpen, setSidebarOpen, currentPage, setCurrentPage } = useAppStore();

  return (
    <div className={`
      fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-50
      ${sidebarOpen ? 'w-64' : 'w-20'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {sidebarOpen && (
          <div className="flex items-center space-x-2">
            <DollarSign className="h-6 w-6 text-primary-600" />
            <span className="font-bold text-gray-900">CostSense</span>
          </div>
        )}
        
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
        >
          <ChevronLeft 
            className={`h-4 w-4 text-gray-500 transition-transform ${
              sidebarOpen ? 'rotate-0' : 'rotate-180'
            }`} 
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="mt-6">
        <div className="px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.to || 
              (item.to === '/' && currentPage === 'dashboard');
            
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setCurrentPage(item.to)}
                className={({ isActive }) => `
                  flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                  ${!sidebarOpen ? 'justify-center' : ''}
                `}
                title={!sidebarOpen ? item.label : undefined}
              >
                <Icon className={`h-5 w-5 ${sidebarOpen ? 'mr-3' : ''}`} />
                
                {sidebarOpen && (
                  <>
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="ml-2 px-2 py-0.5 bg-primary-100 text-primary-700 text-xs rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Agent Status Section */}
        {sidebarOpen && (
          <div className="mt-8 px-3">
            <div className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">
              AI Agents
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center px-3 py-2 text-sm text-gray-600">
                <Bot className="h-4 w-4 mr-3" />
                <span className="flex-1">Cost Analyst</span>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              </div>
              
              <div className="flex items-center px-3 py-2 text-sm text-gray-600">
                <Bot className="h-4 w-4 mr-3" />
                <span className="flex-1">Optimizer</span>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              </div>
              
              <div className="flex items-center px-3 py-2 text-sm text-gray-600">
                <Bot className="h-4 w-4 mr-3" />
                <span className="flex-1">Financial</span>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Bottom Section */}
      {sidebarOpen && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-primary-50 rounded-lg p-4">
            <div className="flex items-center">
              <TrendingDown className="h-5 w-5 text-primary-600 mr-2" />
              <div>
                <div className="text-sm font-medium text-primary-900">
                  Monthly Savings
                </div>
                <div className="text-lg font-bold text-primary-700">
                  $2,450
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;