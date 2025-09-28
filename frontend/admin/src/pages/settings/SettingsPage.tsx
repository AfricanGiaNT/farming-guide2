import React from 'react';
import { Settings, Database, Key, Bell } from 'lucide-react';

function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          System Settings
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Configure your agricultural knowledge base system
        </p>
      </div>

      {/* Settings Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* API Configuration */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center space-x-3">
              <Key className="h-8 w-8 text-primary-600" />
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  API Configuration
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Manage API keys and endpoints
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Database Settings */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center space-x-3">
              <Database className="h-8 w-8 text-primary-600" />
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Database
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Database management and backups
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center space-x-3">
              <Bell className="h-8 w-8 text-primary-600" />
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Notifications
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Alert and notification settings
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Settings Panel */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="text-center py-12">
            <Settings className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Settings panel coming soon
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              This section will provide comprehensive system configuration options.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;