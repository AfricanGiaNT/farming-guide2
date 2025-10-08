import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Search, 
  Database, 
  FileText, 
  Trash2, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Download,
  Eye,
  BarChart3
} from 'lucide-react';
import { knowledgeBaseService } from '../../services/knowledgeBaseService';
import { 
  KnowledgeBaseStatus, 
  DocumentSummary, 
  SearchResult, 
  UploadProgress 
} from '../../types';

interface KnowledgeBaseManagerProps {
  className?: string;
}

const KnowledgeBaseManager: React.FC<KnowledgeBaseManagerProps> = ({ className = '' }) => {
  const [status, setStatus] = useState<KnowledgeBaseStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'search'>('overview');
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadKnowledgeBaseData();
  }, []);

  const loadKnowledgeBaseData = async () => {
    setIsLoading(true);
    try {
      const [statusData, documentsData] = await Promise.all([
        knowledgeBaseService.getStatus(),
        knowledgeBaseService.getDocuments()
      ]);
      setStatus(statusData);
      setDocuments(documentsData);
    } catch (error) {
      showMessage('error', 'Failed to load knowledge base data');
    } finally {
      setIsLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error' | 'info', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const uploadItem: UploadProgress = {
      file,
      progress: 0,
      status: 'uploading',
      message: 'Uploading file...'
    };

    setUploadProgress(prev => [...prev, uploadItem]);

    try {
      const result = await knowledgeBaseService.uploadDocument(file);
      
      setUploadProgress(prev => 
        prev.map(item => 
          item.file === file 
            ? { ...item, progress: 100, status: 'completed', message: 'Upload successful!' }
            : item
        )
      );

      showMessage('success', result.message);
      await loadKnowledgeBaseData();
      
      // Remove completed upload after 3 seconds
      setTimeout(() => {
        setUploadProgress(prev => prev.filter(item => item.file !== file));
      }, 3000);

    } catch (error) {
      setUploadProgress(prev => 
        prev.map(item => 
          item.file === file 
            ? { ...item, status: 'error', message: 'Upload failed' }
            : item
        )
      );
      showMessage('error', 'Failed to upload document');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const results = await knowledgeBaseService.searchKnowledgeBase(searchQuery);
      setSearchResults(results);
      setActiveTab('search');
    } catch (error) {
      showMessage('error', 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRebuild = async () => {
    if (!confirm('Are you sure you want to rebuild the knowledge base? This will process all documents again.')) {
      return;
    }

    setIsLoading(true);
    try {
      const result = await knowledgeBaseService.rebuildKnowledgeBase();
      showMessage('success', result.message);
      await loadKnowledgeBaseData();
    } catch (error) {
      showMessage('error', 'Failed to rebuild knowledge base');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear the knowledge base? This action cannot be undone.')) {
      return;
    }

    setIsLoading(true);
    try {
      await knowledgeBaseService.clearKnowledgeBase();
      showMessage('success', 'Knowledge base cleared successfully');
      await loadKnowledgeBaseData();
    } catch (error) {
      showMessage('error', 'Failed to clear knowledge base');
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Knowledge Base Management</h2>
          <p className="text-gray-600">Upload, process, and manage agricultural documents</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Document</span>
          </button>
          <button
            onClick={handleRebuild}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Rebuild</span>
          </button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800' :
          message.type === 'error' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Upload Progress */}
      {uploadProgress.length > 0 && (
        <div className="space-y-2">
          {uploadProgress.map((item, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{item.file.name}</span>
                <span className={`text-sm ${
                  item.status === 'completed' ? 'text-green-600' :
                  item.status === 'error' ? 'text-red-600' :
                  'text-blue-600'
                }`}>
                  {item.message}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    item.status === 'completed' ? 'bg-green-500' :
                    item.status === 'error' ? 'bg-red-500' :
                    'bg-blue-500'
                  }`}
                  style={{ width: `${item.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'documents', label: 'Documents', icon: FileText },
            { id: 'search', label: 'Search', icon: Search }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Vectors</p>
                <p className="text-2xl font-bold text-gray-900">{status?.total_vectors || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Documents</p>
                <p className="text-2xl font-bold text-gray-900">{documents.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <RefreshCw className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Chunk Size</p>
                <p className="text-2xl font-bold text-gray-900">{status?.chunk_size || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Model</p>
                <p className="text-sm font-bold text-gray-900 truncate">{status?.embedding_model || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Documents in Knowledge Base</h3>
            <button
              onClick={handleClear}
              className="flex items-center space-x-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          </div>
          
          <div className="grid gap-4">
            {documents.map((doc, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{doc.document_name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{doc.sample_text}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>{doc.chunk_count} chunks</span>
                      <span>{doc.total_tokens} tokens</span>
                      <span>{doc.document_type}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {documents.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No documents in knowledge base</p>
                <p className="text-sm">Upload a document to get started</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'search' && (
        <div className="space-y-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge base..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={isLoading || !searchQuery.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div className="space-y-4">
            {searchResults.map((result, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{result.metadata.source_document}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    result.relevance === 'high' ? 'bg-green-100 text-green-800' :
                    result.relevance === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {result.relevance} ({Math.round(result.score * 100)}%)
                  </span>
                </div>
                <p className="text-sm text-gray-600">{result.text_preview}</p>
                <div className="mt-2 text-xs text-gray-500">
                  {result.metadata.document_type}
                </div>
              </div>
            ))}
            
            {searchResults.length === 0 && searchQuery && (
              <div className="text-center py-8 text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No results found for "{searchQuery}"</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.docx"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
};

export default KnowledgeBaseManager;
