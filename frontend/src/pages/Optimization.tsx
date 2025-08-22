import React from 'react';
import { Zap } from 'lucide-react';

const Optimization: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Optimization</h1>
        <p className="text-gray-600">Intelligent AWS cost optimization recommendations</p>
      </div>

      <div className="card">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Zap className="h-12 w-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI-Powered Optimization</h3>
            <p className="text-gray-600">This page will contain optimization features and recommendations</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Optimization;