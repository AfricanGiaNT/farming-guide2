import {
  Variety,
  VarietiesStatus,
  ExtractionStats,
  ExtractionPreview,
  ExtractedVarietyPreview,
  VarietyValidationResult,
} from '../types';

const API_BASE_URL = 'http://localhost:8001/api/admin/varieties';

class VarietiesService {
  async getStatus(): Promise<VarietiesStatus> {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) {
      throw new Error('Failed to fetch varieties status');
    }
    const data = await response.json();
    return data.data;
  }

  async getVarieties(params: {
    page?: number;
    per_page?: number;
    crop?: string;
    search?: string;
  } = {}): Promise<{
    varieties: Variety[];
    pagination: {
      page: number;
      per_page: number;
      total_count: number;
      total_pages: number;
    };
  }> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.per_page) searchParams.append('per_page', params.per_page.toString());
    if (params.crop) searchParams.append('crop', params.crop);
    if (params.search) searchParams.append('search', params.search);

    const response = await fetch(`${API_BASE_URL}/list?${searchParams}`);
    if (!response.ok) {
      throw new Error('Failed to fetch varieties list');
    }
    const data = await response.json();
    return data.data;
  }

  async extractVarieties(params: {
    crops?: string[];
    documents?: string[];
    clear_existing?: boolean;
  } = {}): Promise<{
    message: string;
    data: ExtractionPreview;
  }> {
    const response = await fetch(`${API_BASE_URL}/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to extract varieties');
    }

    const data = await response.json();
    const preview: ExtractionPreview = data.data;
    return {
      message: data.message,
      data: preview,
    };
  }

  async validateVarieties(payload: {
    session_id: string;
    selected_varieties: ExtractedVarietyPreview[];
    clear_existing?: boolean;
  }): Promise<{
    message: string;
    data: VarietyValidationResult;
  }> {
    const response = await fetch(`${API_BASE_URL}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to validate varieties');
    }

    const data = await response.json();
    const result: VarietyValidationResult = data.data;
    return {
      message: data.message,
      data: result,
    };
  }

  async clearVarieties(): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/clear`, { method: 'POST' });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to clear varieties');
    }
    const data = await response.json();
    return data.message;
  }
}

export const varietiesService = new VarietiesService();
