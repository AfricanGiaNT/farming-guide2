// Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'superadmin';
  lastLogin?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// Document Management Types
export interface Document {
  id: string;
  filename: string;
  originalName: string;
  filesize: number;
  mimeType: string;
  uploadDate: string;
  status: 'processing' | 'completed' | 'failed' | 'archived';
  categories: string[];
  description?: string;
  processingProgress?: number;
  metadata: DocumentMetadata;
}

export interface DocumentMetadata {
  pages?: number;
  wordCount?: number;
  language?: string;
  extractedTopics?: string[];
}

// Variety Management Types
export interface Variety {
  id: string;
  cropType: string;
  name: string;
  description: string;
  maturityDays: number;
  yieldPerHectare: number;
  season: 'rainy' | 'dry' | 'both';
  soilRequirements: string[];
  regions: string[];
  plantingTips: string;
  harvestTips: string;
  createdAt: string;
  updatedAt: string;
}

export interface CropType {
  id: string;
  name: string;
  category: string;
  varietyCount: number;
}

// Dashboard Analytics Types
export interface DashboardStats {
  totalDocuments: number;
  totalVarieties: number;
  recentUploads: number;
  processingQueue: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
  storageUsed: number;
  storageLimit: number;
}

export interface ActivityLog {
  id: string;
  action: string;
  entityType: 'document' | 'variety' | 'user' | 'system';
  entityId: string;
  userId: string;
  userEmail: string;
  timestamp: string;
  details: Record<string, any>;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string[];
    borderColor?: string;
    borderWidth?: number;
  }[];
}

// Search and Filtering Types
export interface SearchFilters {
  query?: string;
  documentType?: string;
  cropType?: string;
  dateFrom?: string;
  dateTo?: string;
  status?: string;
  category?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    current: number;
    totalPages: number;
    totalItems: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// System Management Types
export interface SystemConfig {
  apiEndpoints: {
    openweather: string;
    openai: string;
  };
  processing: {
    maxFileSize: number;
    allowedFormats: string[];
    batchSize: number;
  };
  notifications: {
    emailEnabled: boolean;
    slackWebhook?: string;
  };
}

export interface ProcessingJob {
  id: string;
  type: 'document_processing' | 'bulk_import' | 'reindexing';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
  metadata: Record<string, any>;
}

// Form Types
export interface FormFieldError {
  field: string;
  message: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: FormFieldError[];
}

// UI State Types
export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

export interface ConfirmDialogState {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

// Knowledge Base Types
export interface KnowledgeBaseStatus {
  total_vectors?: number;
  chunk_size?: number;
  overlap?: number;
  embedding_model?: string;
  embedding_cache_size?: number;
  processed_documents?: string[];
  storage_path?: string;
  dimension?: number;
}

export interface DocumentSummary {
  document_name: string;
  chunk_count: number;
  total_tokens: number;
  sample_text: string;
  file_path: string;
  document_type: string;
}

export interface SearchResult {
  text: string;
  score: number;
  metadata: {
    source_document: string;
    file_path: string;
    document_type: string;
  };
  text_preview: string;
  relevance: 'high' | 'medium' | 'low';
  query?: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

// Varieties Types
export interface Variety {
  id: number;
  crop_name: string;
  variety_name: string;
  variety_type?: string;
  yield_potential?: string;
  maturity_days?: number;
  weather_requirements?: string;
  soil_requirements?: string;
  growing_areas?: string;
  disease_resistance?: string;
  planting_time?: string;
  source_document: string;
  confidence_score?: number;
  validation_status?: string;
  extraction_session_id?: string;
  created_at: string;
}

export interface VarietiesStatus {
  total_varieties: number;
  crop_counts: Array<{
    crop: string;
    count: number;
  }>;
  recent_additions: number;
  database_path: string;
}

export interface ExtractionStats {
  documents_processed: number;
  varieties_extracted: number;
  crops_processed: string[];
}

export interface ExtractedVarietyPreview {
  crop_name: string;
  variety_name: string;
  variety_type?: string;
  yield_potential?: string;
  maturity_days?: number;
  weather_requirements?: string;
  soil_requirements?: string;
  growing_areas?: string;
  disease_resistance?: string;
  planting_time?: string;
  source_document?: string;
  confidence_score?: number;
  validation_status?: string;
  extraction_session_id?: string;
  context?: string;
}

export interface ExtractionPreview {
  session_id: string | null;
  varieties: ExtractedVarietyPreview[];
  stats: ExtractionStats;
}

export interface VarietyValidationResult {
  session_id: string;
  varieties_saved: number;
}
