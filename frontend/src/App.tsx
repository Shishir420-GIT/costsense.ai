import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from '@/components/Layout/Layout';
import Dashboard from '@/pages/Dashboard';
import EnhancedDashboard from '@/pages/EnhancedDashboard';
import CostAnalysis from '@/pages/CostAnalysis';
import Optimization from '@/pages/Optimization';
import Reports from '@/pages/Reports';
import Settings from '@/pages/Settings';
import AIChat from '@/pages/AIChat';
import AzureDemo from '@/pages/AzureDemo';
import ShadcnShowcase from '@/components/ShadcnShowcase';
import { ThemeProvider } from '@/components/theme-provider';
import { useAppStore } from '@/store/appStore';
import { useAgentStore } from '@/store/agentStore';

function App() {
  const { fetchSystemHealth, setTheme, theme } = useAppStore();
  const { connectWebSocket, fetchAgentStatus, fetchAgentCapabilities } = useAgentStore();

  useEffect(() => {
    // Initialize app
    fetchSystemHealth();
    fetchAgentStatus();
    fetchAgentCapabilities();
    
    // Connect WebSocket
    connectWebSocket();
    
    // Apply theme
    setTheme(theme);
    
    // Cleanup WebSocket on unmount
    return () => {
      // WebSocket cleanup handled in store
    };
  }, []);

  return (
    <ThemeProvider defaultTheme="light" storageKey="costsense-ui-theme">
      <div className="App min-h-screen bg-background">
        <Layout>
          <Routes>
            <Route path="/" element={<AzureDemo />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/enhanced" element={<EnhancedDashboard />} />
            <Route path="/cost-analysis" element={<CostAnalysis />} />
            <Route path="/optimization" element={<Optimization />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/chat" element={<AIChat />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/components" element={<ShadcnShowcase />} />
            <Route path="/demo" element={<AzureDemo />} />
          </Routes>
        </Layout>
      </div>
    </ThemeProvider>
  );
}

export default App;