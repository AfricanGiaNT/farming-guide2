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