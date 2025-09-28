import React from 'react';
import { FileText, Upload, Search, Filter } from 'lucide-react';

function DocumentsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Document Management
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage your agricultural knowledge base documents
          </p>
        </div>
        <button className="btn-primary inline-flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Upload Documents
        </button>
      </div>

      {/* Search and Filter */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents..."
                className="form-input pl-10"
              />
            </div>
            <button className="btn-secondary inline-flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Documents Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            All Documents
          </h3>
        </div>
        <div className="card-body">
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Document management coming soon
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              This section will allow you to upload, manage, and organize your agricultural documents.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentsPage;