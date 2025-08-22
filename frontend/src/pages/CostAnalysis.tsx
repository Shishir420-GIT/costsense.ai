import React from 'react';
import { BarChart3, TrendingDown, DollarSign, Clock } from 'lucide-react';

const CostAnalysis: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cost Analysis</h1>
        <p className="text-gray-600">Detailed AWS cost analysis and trends</p>
      </div>

      <div className="card">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Cost Analysis Dashboard</h3>
            <p className="text-gray-600">This page will contain detailed cost analysis features</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostAnalysis;