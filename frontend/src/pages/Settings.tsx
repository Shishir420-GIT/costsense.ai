import React from 'react';
import { Settings as SettingsIcon } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure your cost optimization preferences</p>
      </div>

      <div className="card">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <SettingsIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Platform Settings</h3>
            <p className="text-gray-600">This page will contain configuration and preference settings</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;