import React, { useState, useEffect } from 'react';
import { varietiesService } from '../../services/varietiesService';
import {
  Variety,
  VarietiesStatus,
  ExtractionStats,
  ExtractionPreview,
  ExtractedVarietyPreview,
} from '../../types';
import VarietyValidationModal from './VarietyValidationModal';

const VarietiesManager: React.FC = () => {
  const [status, setStatus] = useState<VarietiesStatus | null>(null);
  const [varieties, setVarieties] = useState<Variety[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'varieties' | 'organized' | 'extract'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [cropFilter, setCropFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total_count: 0,
    total_pages: 0
  });
  const [extracting, setExtracting] = useState(false);
  const [extractionStats, setExtractionStats] = useState<ExtractionStats | null>(null);
  const [extractionPreview, setExtractionPreview] = useState<ExtractionPreview | null>(null);
  const [validationModalOpen, setValidationModalOpen] = useState(false);
  const [validating, setValidating] = useState(false);
  const [expandedCrops, setExpandedCrops] = useState<Set<string>>(new Set());

  const loadStatus = async () => {
    try {
      const statusData = await varietiesService.getStatus();
      setStatus(statusData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load status');
    }
  };

  const loadVarieties = async () => {
    try {
      setLoading(true);
      const data = await varietiesService.getVarieties({
        page: currentPage,
        per_page: 20,
        crop: cropFilter || undefined,
        search: searchQuery || undefined
      });
      setVarieties(data.varieties);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load varieties');
    } finally {
      setLoading(false);
    }
  };

  const loadAllVarieties = async () => {
    try {
      setLoading(true);
      // Load all varieties without any filters or pagination
      const data = await varietiesService.getVarieties({
        per_page: 1000  // Large number to get all varieties
      });
      console.log('Loaded varieties for organized view:', data.varieties.length);
      setVarieties(data.varieties);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load varieties');
    } finally {
      setLoading(false);
    }
  };

  const handleExtractVarieties = async (clearExisting: boolean = false) => {
    try {
      setExtracting(true);
      setError(null);
      
      const result = await varietiesService.extractVarieties({
        clear_existing: clearExisting
      });
      
      setExtractionPreview(result.data);
      setExtractionStats(result.data.stats);

      if (result.data.session_id && result.data.varieties.length > 0) {
        setValidationModalOpen(true);
      } else {
        await loadStatus();
        await loadVarieties();
        alert(result.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract varieties');
    } finally {
      setExtracting(false);
    }
  };

  const handleValidateVarieties = async (selected: ExtractedVarietyPreview[]) => {
    if (!extractionPreview || !extractionPreview.session_id) {
      setError('Validation session not found. Please extract varieties again.');
      return;
    }

    try {
      setValidating(true);
      setError(null);

      const response = await varietiesService.validateVarieties({
        session_id: extractionPreview.session_id,
        selected_varieties: selected,
      });

      await loadStatus();
      await loadVarieties();
      alert(response.message);
      setValidationModalOpen(false);
      setExtractionPreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate varieties');
    } finally {
      setValidating(false);
    }
  };

  const handleClearVarieties = async () => {
    if (!confirm('Are you sure you want to clear all varieties? This action cannot be undone.')) {
      return;
    }

    try {
      setExtracting(true);
      await varietiesService.clearVarieties();
      await loadStatus();
      await loadVarieties();
      alert('Varieties database cleared successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear varieties');
    } finally {
      setExtracting(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  useEffect(() => {
    if (activeTab === 'varieties') {
      loadVarieties();
    } else if (activeTab === 'organized') {
      loadAllVarieties();
    }
  }, [activeTab, currentPage, searchQuery, cropFilter]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getCropOptions = () => {
    if (!status) return [];
    return status.crop_counts.map(item => item.crop);
  };

  const groupVarietiesBySeries = (varieties: Variety[]) => {
    const grouped: { [crop: string]: { [series: string]: Variety[] } } = {};
    
    varieties.forEach(variety => {
      const crop = variety.crop_name;
      if (!grouped[crop]) {
        grouped[crop] = {};
      }
      
      const series = getVarietySeries(variety.variety_name, crop);
      if (!grouped[crop][series]) {
        grouped[crop][series] = [];
      }
      grouped[crop][series].push(variety);
    });
    
    return grouped;
  };

  const getVarietySeries = (varietyName: string, crop: string): string => {
    const name = varietyName.toUpperCase();
    
    // Maize series
    if (crop === 'maize') {
      if (name.startsWith('SC')) return 'SC Series (Seed Co)';
      if (name.startsWith('PAN')) return 'PAN Series (PANAR)';
      if (name.startsWith('MH')) return 'MH Series (Malawi Hybrid)';
      if (name.startsWith('ZM')) return 'ZM Series';
      if (name.startsWith('DK')) return 'DK Series';
      return 'Local Varieties';
    }
    
    // Groundnut series
    if (crop === 'groundnut') {
      if (name.startsWith('CG')) return 'CG Series (Chitedze Groundnut)';
      if (name.startsWith('ICGV-SM')) return 'ICGV-SM Series (International)';
      if (name.startsWith('CHALIMBANA')) return 'Chalimbana Series';
      return 'Local Varieties';
    }
    
    // Soybean series
    if (crop === 'soybean') {
      if (name.startsWith('SB')) return 'SB Series';
      if (name.startsWith('TGX')) return 'TGX Series';
      return 'Local Varieties';
    }
    
    // Rice series
    if (crop === 'rice') {
      if (name.startsWith('IR')) return 'IR Series';
      if (name.startsWith('NERICA')) return 'NERICA Series';
      return 'Local Varieties';
    }
    
    // Default fallback
    return 'Other Varieties';
  };

  const getSeriesColor = (series: string): string => {
    if (series.includes('SC Series')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
    if (series.includes('PAN Series')) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
    if (series.includes('MH Series')) return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
    if (series.includes('CG Series')) return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
    if (series.includes('ICGV-SM Series')) return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300';
    if (series.includes('Chalimbana Series')) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
    if (series.includes('Local Varieties')) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  const toggleCropExpansion = (crop: string) => {
    const newExpanded = new Set(expandedCrops);
    if (newExpanded.has(crop)) {
      newExpanded.delete(crop);
    } else {
      newExpanded.add(crop);
    }
    setExpandedCrops(newExpanded);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Varieties Management
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3 py-1 rounded-md text-sm font-medium ${
              activeTab === 'overview'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('varieties')}
            className={`px-3 py-1 rounded-md text-sm font-medium ${
              activeTab === 'varieties'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Varieties Database
          </button>
          <button
            onClick={() => {
              setActiveTab('organized');
              setSearchQuery('');
              setCropFilter('');
              setCurrentPage(1);
            }}
            className={`px-3 py-1 rounded-md text-sm font-medium ${
              activeTab === 'organized'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Organized View
          </button>
          <button
            onClick={() => setActiveTab('extract')}
            className={`px-3 py-1 rounded-md text-sm font-medium ${
              activeTab === 'extract'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Extract Varieties
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && status && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">V</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Total Varieties
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {status.total_varieties.toLocaleString()}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">+</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Recent Additions (7 days)
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {status.recent_additions}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">C</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Crop Types
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {status.crop_counts.length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Crop Distribution */}
      {activeTab === 'overview' && status && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
              Varieties by Crop
            </h3>
            <div className="mt-5">
              <div className="space-y-3">
                {status.crop_counts.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                      {item.crop.replace('_', ' ')}
                    </span>
                    <div className="flex items-center">
                      <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${(item.count / status.total_varieties) * 100}%`
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {item.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Varieties Database Tab */}
      {activeTab === 'varieties' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Search
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search varieties..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Crop Filter
                </label>
                <select
                  value={cropFilter}
                  onChange={(e) => setCropFilter(e.target.value)}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">All Crops</option>
                  {getCropOptions().map((crop) => (
                    <option key={crop} value={crop}>
                      {crop.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => {
                    setCurrentPage(1);
                    loadVarieties();
                  }}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Search
                </button>
              </div>
            </div>
          </div>

          {/* Varieties Table */}
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
            {loading ? (
              <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-500">Loading varieties...</p>
              </div>
            ) : (
              <>
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
                    Varieties Database ({pagination.total_count} total)
                  </h3>
                </div>
                <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                  {varieties.map((variety) => (
                    <li key={variety.id} className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-3">
                            <p className="text-sm font-medium text-blue-600 truncate">
                              {variety.variety_name}
                            </p>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                              {variety.crop_name.replace('_', ' ').toUpperCase()}
                            </span>
                            {variety.variety_type && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                                {variety.variety_type}
                              </span>
                            )}
                          </div>
                          <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                            {variety.maturity_days && (
                              <span>{variety.maturity_days} days</span>
                            )}
                            {variety.yield_potential && (
                              <span>Yield: {variety.yield_potential}</span>
                            )}
                            <span>Source: {variety.source_document}</span>
                            <span>{formatDate(variety.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>

                {/* Pagination */}
                {pagination.total_pages > 1 && (
                  <div className="bg-white dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 sm:px-6">
                    <div className="flex-1 flex justify-between sm:hidden">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(Math.min(pagination.total_pages, currentPage + 1))}
                        disabled={currentPage === pagination.total_pages}
                        className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                      >
                        Next
                      </button>
                    </div>
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          Showing page <span className="font-medium">{currentPage}</span> of{' '}
                          <span className="font-medium">{pagination.total_pages}</span>
                        </p>
                      </div>
                      <div>
                        <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                          <button
                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                            className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                          >
                            Previous
                          </button>
                          <button
                            onClick={() => setCurrentPage(Math.min(pagination.total_pages, currentPage + 1))}
                            disabled={currentPage === pagination.total_pages}
                            className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                          >
                            Next
                          </button>
                        </nav>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Organized View Tab */}
      {activeTab === 'organized' && (
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Varieties by Series and Type
              </h3>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                {status?.total_varieties || varieties.length} total varieties
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Click on any crop to expand and see varieties organized by their series and type.
            </p>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-500">Loading varieties...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {status?.crop_counts.map((cropData) => {
                  const cropVarieties = varieties.filter(v => v.crop_name === cropData.crop);
                  const groupedVarieties = groupVarietiesBySeries(cropVarieties);
                  const isExpanded = expandedCrops.has(cropData.crop);
                  
                  return (
                    <div key={cropData.crop} className="border border-gray-200 dark:border-gray-700 rounded-lg">
                      <button
                        onClick={() => toggleCropExpansion(cropData.crop)}
                        className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                            <span className="text-white font-bold text-sm">
                              {cropData.crop.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 capitalize">
                              {cropData.crop.replace('_', ' ')}
                            </h4>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {cropData.count} varieties
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {Object.keys(groupedVarieties[cropData.crop] || {}).length} series
                          </span>
                          <svg
                            className={`w-5 h-5 text-gray-400 transition-transform ${
                              isExpanded ? 'rotate-180' : ''
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
                          <div className="pt-4 space-y-4">
                            {Object.entries(groupedVarieties[cropData.crop] || {}).map(([series, seriesVarieties]) => (
                              <div key={series} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-3">
                                  <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {series}
                                  </h5>
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeriesColor(series)}`}>
                                    {seriesVarieties.length} varieties
                                  </span>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                                  {seriesVarieties.map((variety) => (
                                    <div
                                      key={variety.id}
                                      className="bg-white dark:bg-gray-800 rounded-md p-3 border border-gray-200 dark:border-gray-600"
                                    >
                                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                        {variety.variety_name}
                                      </div>
                                      {variety.variety_type && variety.variety_type !== 'Not specified' && (
                                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                          {variety.variety_type}
                                        </div>
                                      )}
                                      {variety.yield_potential && variety.yield_potential !== 'Not specified' && (
                                        <div className="text-xs text-green-600 dark:text-green-400 mt-1">
                                          {variety.yield_potential}
                                        </div>
                                      )}
                                      {variety.growing_areas && variety.growing_areas !== 'Not specified' && (
                                        <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                                          {variety.growing_areas}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Extract Varieties Tab */}
      {activeTab === 'extract' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Extract Varieties from Documents
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Use the existing varieties extraction pipeline to process documents and extract variety information.
              This will analyze all documents in the knowledge base and extract structured variety data.
            </p>

            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handleExtractVarieties(false)}
                  disabled={extracting}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {extracting ? 'Extracting...' : 'Extract Varieties (Append)'}
                </button>
                <button
                  onClick={() => handleExtractVarieties(true)}
                  disabled={extracting}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {extracting ? 'Extracting...' : 'Extract Varieties (Replace)'}
                </button>
                <button
                  onClick={handleClearVarieties}
                  disabled={extracting}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Clear All Varieties
                </button>
              </div>

              {extractionStats && (
                <div className="bg-green-50 border border-green-200 rounded-md p-4">
                  <h4 className="text-sm font-medium text-green-800 mb-2">Extraction Results</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Documents Processed:</span>
                      <span className="ml-1">{extractionStats.documents_processed}</span>
                    </div>
                    <div>
                      <span className="font-medium">Varieties Extracted:</span>
                      <span className="ml-1">{extractionStats.varieties_extracted}</span>
                    </div>
                    <div>
                      <span className="font-medium">Crops Processed:</span>
                      <span className="ml-1">{extractionStats.crops_processed.length}</span>
                    </div>
                    <div>
                      <span className="font-medium">Crops:</span>
                      <span className="ml-1">{extractionStats.crops_processed.join(', ')}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <VarietyValidationModal
        isOpen={validationModalOpen}
        sessionId={extractionPreview?.session_id || null}
        varieties={extractionPreview?.varieties || []}
        onClose={() => setValidationModalOpen(false)}
        onSubmit={handleValidateVarieties}
        isSubmitting={validating}
      />
    </div>
  );
};

export default VarietiesManager;
