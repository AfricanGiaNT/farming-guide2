/**
 * API Service for Mlangizi wa Ulimi Frontend
 * Connects to the Flask backend running on port 8000
 */

// API configuration - Use Replit domain if available, otherwise localhost for development
const getApiBaseUrl = () => {
  // Try to detect Replit environment
  if (typeof window !== 'undefined' && window.location.hostname.includes('replit.dev')) {
    // In Replit, use the same domain with port 8000
    return `https://${window.location.hostname}:8000/api`;
  }
  // Default to localhost for local development
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

// Types for API responses
export interface WeatherData {
  location: string;
  current: {
    temperature: number;
    humidity: number;
    rainfall: number;
    description: string;
    wind_speed: number;
    pressure: number;
  };
  forecast: Array<{
    date: string;
    temp_high: number;
    temp_low: number;
    rain_chance: number;
    description: string;
  }>;
  timestamp: string;
  mock_data?: boolean;
}

export interface CropRecommendation {
  crop_data?: {
    name: string;
    category: string;
    description: string;
    temperature_requirements?: {
      minimum_temp: number;
      maximum_temp: number;
      optimal_temp: number;
    };
    water_requirements?: {
      minimum_rainfall: number;
      maximum_rainfall: number;
      optimal_rainfall: number;
    };
  };
  score: number;
  total_score?: number;
  suitability_level: string;
  suitability_score: number;
  sources: string[];
  guide_recommendations: string[];
  reasons: string[];
  score_components: {
    content_quality: number;
    guide_relevance: number;
    seasonal_match: number;
  };
  source: string;
  // Legacy properties for backward compatibility
  crop?: string;
  varieties?: string[];
  planting_time?: string;
  yield_potential?: string;
  description?: string;
}

export interface CropResponse {
  location: string;
  season: string;
  recommendations: CropRecommendation[];
  timestamp: string;
  mock_data?: boolean;
}

export interface VarietyInfo {
  name: string;
  maturity_days: number;
  yield_potential: string;
  drought_tolerance: string;
  disease_resistance: string;
  planting_time: string;
  description: string;
}

export interface VarietiesResponse {
  crop: string;
  location: string;
  varieties: VarietyInfo[];
  timestamp: string;
  mock_data?: boolean;
}

export interface SearchResult {
  title: string;
  content: string;
  source: string;
  category: string;
  relevance_score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
  timestamp: string;
  mock_data?: boolean;
}

export interface Category {
  id: string;
  name: string;
  count: number;
}

export interface CategoriesResponse {
  categories: Category[];
}

export interface HistoricalWeatherData {
  location: string;
  years_analyzed: number;
  period_start?: string;
  period_end?: string;
  monthly_averages: {
    [month: string]: {
      average_rainfall: number;
      min_rainfall: number;
      max_rainfall: number;
      average_temperature: number;
      years_analyzed: number;
    };
  };
  key_monthly_averages?: {
    [month: string]: {
      average_rainfall: number;
      min_rainfall: number;
      max_rainfall: number;
      average_temperature: number;
      years_analyzed: number;
    };
  };
  yearly_breakdown?: Array<{
    year: number;
    annual_rainfall: number;
    avg_temperature: number;
    wettest_month: string;
    driest_month: string;
    monthly_summary: {
      wet_season_total: number;
      dry_season_total: number;
    };
  }>;
  climate_summary: {
    total_annual_rainfall: number;
    wettest_month: string;
    driest_month: string;
    climate_trend: string;
    drought_risk: string;
    analysis_period?: string;
  };
  agricultural_implications: {
    wet_season: string;
    dry_season: string;
    planting_window: string;
    harvest_period: string;
    data_note?: string;
  };
  timestamp: string;
  mock_data?: boolean;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data: T;
  timestamp: string;
}

export interface ExtractedVariety {
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
  extraction_session_id: string;
  context?: string;
}

export interface VarietyExtractionStats {
  documents_processed: number;
  varieties_extracted: number;
  crops_processed: string[];
}

export interface VarietyExtractionResult {
  session_id: string | null;
  varieties: ExtractedVariety[];
  stats: VarietyExtractionStats;
}

export interface VarietyExtractionParams {
  crops?: string[];
  documents?: string[];
  clear_existing?: boolean;
}

export interface VarietyValidationPayload {
  session_id: string;
  selected_varieties: ExtractedVariety[];
  clear_existing?: boolean;
}

export interface VarietyValidationResult {
  session_id: string;
  varieties_saved: number;
}

// API Service Class
class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async getHealth() {
    return this.request('/health');
  }

  // Weather API
  async getWeather(location: string): Promise<WeatherData> {
    return this.request(`/weather/${encodeURIComponent(location)}`);
  }

  // Historical Weather API
  async getHistoricalWeather(location: string, years: number = 5): Promise<HistoricalWeatherData> {
    return this.request(`/weather/${encodeURIComponent(location)}/historical?years=${years}`);
  }

  // Crops API
  async getCrops(location: string = 'Lilongwe', season: string = 'current'): Promise<CropResponse> {
    const params = new URLSearchParams({
      location,
      season,
    });
    return this.request(`/crops?${params}`);
  }

  // Varieties API
  async getVarieties(crop: string, location?: string): Promise<VarietiesResponse> {
    const params = new URLSearchParams({ crop });
    if (location) {
      params.append('location', location);
    }
    return this.request(`/varieties?${params}`);
  }

  // Search API
  async searchKnowledge(query: string, limit: number = 10): Promise<SearchResponse> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return this.request(`/search?${params}`);
  }

  async extractVarietiesForValidation(params: VarietyExtractionParams = {}): Promise<ApiResponse<VarietyExtractionResult>> {
    return this.request('/admin/varieties/extract', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async validateSelectedVarieties(payload: VarietyValidationPayload): Promise<ApiResponse<VarietyValidationResult>> {
    return this.request('/admin/varieties/validate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Categories API
  async getCategories(): Promise<CategoriesResponse> {
    return this.request('/categories');
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
