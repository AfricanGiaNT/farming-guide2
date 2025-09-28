import React from 'react';
import { useQuery } from 'react-query';
import { FileText, Sprout, Database, TrendingUp, Users, Activity } from 'lucide-react';
import { DashboardStats } from '../../types';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import StatsCard from '../../components/dashboard/StatsCard';
import ActivityFeed from '../../components/dashboard/ActivityFeed';
import ChartsSection from '../../components/dashboard/ChartsSection';

// Mock API service
const fetchDashboardStats = async (): Promise<DashboardStats> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return {
    totalDocuments: 847,
    totalVarieties: 324,
    recentUploads: 23,
    processingQueue: 5,
    systemHealth: 'healthy',
    storageUsed: 2.1,
    storageLimit: 10.0,
  };
};

function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery(
    'dashboard-stats',
    fetchDashboardStats,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">Failed to load dashboard data</p>
      </div>
    );
  }

  const statsCards = [
    {
      title: 'Total Documents',
      value: stats?.totalDocuments || 0,
      icon: FileText,
      color: 'blue',
      change: '+12.5%',
      changeType: 'increase' as const,
    },
    {
      title: 'Crop Varieties',
      value: stats?.totalVarieties || 0,
      icon: Sprout,
      color: 'green',
      change: '+8.2%',
      changeType: 'increase' as const,
    },
    {
      title: 'Recent Uploads',
      value: stats?.recentUploads || 0,
      icon: TrendingUp,
      color: 'purple',
      change: '+23',
      changeType: 'increase' as const,
    },
    {
      title: 'Processing Queue',
      value: stats?.processingQueue || 0,
      icon: Activity,
      color: 'orange',
      change: '-3',
      changeType: 'decrease' as const,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Dashboard Overview
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your agricultural knowledge base.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((card, index) => (
          <StatsCard key={index} {...card} />
        ))}
      </div>

      {/* System Health */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            System Health
          </h3>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-3 w-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                All systems operational
              </span>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Storage: {stats?.storageUsed}GB / {stats?.storageLimit}GB
            </div>
          </div>
          
          {/* Storage Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
              <span>Storage Usage</span>
              <span>{Math.round(((stats?.storageUsed || 0) / (stats?.storageLimit || 1)) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full"
                style={{
                  width: `${Math.round(((stats?.storageUsed || 0) / (stats?.storageLimit || 1)) * 100)}%`
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartsSection />
        <ActivityFeed />
      </div>
    </div>
  );
}

export default DashboardPage;