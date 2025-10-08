import { DocumentSummary, KnowledgeBaseStatus, SearchResult } from '../types';

class KnowledgeBaseService {
  private baseUrl = 'http://localhost:8001/api/admin/knowledge-base';

  async getStatus(): Promise<KnowledgeBaseStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to get knowledge base status');
      }
      
      return data.data;
    } catch (error) {
      console.error('Error getting knowledge base status:', error);
      throw error;
    }
  }

  async getDocuments(): Promise<DocumentSummary[]> {
    try {
      const response = await fetch(`${this.baseUrl}/documents`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to get documents');
      }
      
      return data.data.documents;
    } catch (error) {
      console.error('Error getting documents:', error);
      throw error;
    }
  }

  async uploadDocument(file: File): Promise<{ message: string; data: any }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to upload document');
      }
      
      return data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }

  async searchKnowledgeBase(query: string, topK: number = 5, threshold: number = 0.7): Promise<SearchResult[]> {
    try {
      const response = await fetch(`${this.baseUrl}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          top_k: topK,
          threshold,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to search knowledge base');
      }
      
      return data.data.results;
    } catch (error) {
      console.error('Error searching knowledge base:', error);
      throw error;
    }
  }

  async rebuildKnowledgeBase(): Promise<{ message: string; data: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/rebuild`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to rebuild knowledge base');
      }
      
      return data;
    } catch (error) {
      console.error('Error rebuilding knowledge base:', error);
      throw error;
    }
  }

  async clearKnowledgeBase(): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/clear`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to clear knowledge base');
      }
      
      return data;
    } catch (error) {
      console.error('Error clearing knowledge base:', error);
      throw error;
    }
  }
}

export const knowledgeBaseService = new KnowledgeBaseService();
