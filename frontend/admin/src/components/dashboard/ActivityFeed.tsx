import React from 'react';
import { useQuery } from 'react-query';
import { ActivityLog } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { FileText, Sprout, User, Database } from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';

const iconMap = {
  document: FileText,
  variety: Sprout,
  user: User,
  system: Database,
};

const fetchActivityLogs = async (): Promise<ActivityLog[]> => {
  // Mock data for now
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return [
    {
      id: '1',
      action: 'Document uploaded',
      entityType: 'document',
      entityId: 'doc_123',
      userId: 'user_1',
      userEmail: 'admin@example.com',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      details: { filename: 'maize_varieties_2024.pdf' },
    },
    {
      id: '2',
      action: 'Variety updated',
      entityType: 'variety',
      entityId: 'var_456',
      userId: 'user_1',
      userEmail: 'admin@example.com',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      details: { varietyName: 'SC627 Groundnut' },
    },
    {
      id: '3',
      action: 'Database reindexed',
      entityType: 'system',
      entityId: 'sys_789',
      userId: 'user_1',
      userEmail: 'admin@example.com',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      details: { documentsProcessed: 245 },
    },
    {
      id: '4',
      action: 'Bulk import completed',
      entityType: 'variety',
      entityId: 'bulk_001',
      userId: 'user_1',
      userEmail: 'admin@example.com',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      details: { varietiesImported: 23 },
    },
    {
      id: '5',
      action: 'Document deleted',
      entityType: 'document',
      entityId: 'doc_old',
      userId: 'user_1',
      userEmail: 'admin@example.com',
      timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
      details: { filename: 'old_pest_control.pdf' },
    },
  ];
};

function ActivityFeed() {
  const { data: activities, isLoading } = useQuery(
    'activity-logs',
    fetchActivityLogs,
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Recent Activity
        </h3>
      </div>
      <div className="card-body">
        {isLoading ? (
          <div className="flex justify-center py-6">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="flow-root">
            <ul className="-mb-8">
              {activities?.map((activity, index) => {
                const Icon = iconMap[activity.entityType];
                const isLast = index === activities.length - 1;
                
                return (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {!isLast && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                            <Icon className="h-4 w-4 text-primary-600 dark:text-primary-400" />
                          </span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <div>
                            <div className="text-sm text-gray-900 dark:text-gray-100">
                              <span className="font-medium">{activity.action}</span>
                              {activity.details.filename && (
                                <span className="text-gray-600 dark:text-gray-400">
                                  : {activity.details.filename}
                                </span>
                              )}
                              {activity.details.varietyName && (
                                <span className="text-gray-600 dark:text-gray-400">
                                  : {activity.details.varietyName}
                                </span>
                              )}
                              {activity.details.documentsProcessed && (
                                <span className="text-gray-600 dark:text-gray-400">
                                  : {activity.details.documentsProcessed} documents
                                </span>
                              )}
                              {activity.details.varietiesImported && (
                                <span className="text-gray-600 dark:text-gray-400">
                                  : {activity.details.varietiesImported} varieties
                                </span>
                              )}
                            </div>
                            <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
                              {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default ActivityFeed;