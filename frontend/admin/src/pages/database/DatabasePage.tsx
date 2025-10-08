import React from 'react';
import KnowledgeBaseManager from '../../components/database/KnowledgeBaseManager';

function DatabasePage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Knowledge Base Management
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Upload, process, and manage agricultural documents for AI querying
          </p>
        </div>
      </div>

      {/* Knowledge Base Manager */}
      <KnowledgeBaseManager />
    </div>
  );
}

export default DatabasePage;