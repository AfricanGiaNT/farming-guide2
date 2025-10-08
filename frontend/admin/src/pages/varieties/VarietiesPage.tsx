import React from 'react';
import VarietiesManager from '../../components/varieties/VarietiesManager';

function VarietiesPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Crop Varieties
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage crop varieties and their characteristics
          </p>
        </div>
      </div>

      {/* Varieties Manager */}
      <VarietiesManager />
    </div>
  );
}

export default VarietiesPage;