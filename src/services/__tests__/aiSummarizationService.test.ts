/**
 * Tests for AI Summarization Service
 * Tests AI-powered data summarization and enhancement functionality
 */

import { AISummarizationService, aiSummarizationService } from '../aiSummarizationService'

// Mock fetch for OpenAI API calls
global.fetch = jest.fn()

describe('AISummarizationService', () => {
  let service: AISummarizationService

  beforeEach(() => {
    service = new AISummarizationService({
      enableAI: false, // Start with AI disabled for fallback testing
      cacheEnabled: true,
    })
    jest.clearAllMocks()
  })

  describe('Weather Risk Summarization', () => {
    it('should summarize weather risks with fallback when AI is disabled', async () => {
      const risks = [
        'Heavy rainfall expected in the next 7 days',
        'Potential drought conditions due to low precipitation',
        'High temperature stress may affect crop growth'
      ]

      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {
        temperature: 25,
        rainfall: 50
      })

      expect(result).toHaveLength(3)
      expect(result[0]).toHaveProperty('id')
      expect(result[0]).toHaveProperty('summary')
      expect(result[0]).toHaveProperty('category')
      expect(result[0]).toHaveProperty('severity')
      expect(result[0]).toHaveProperty('priority')
      expect(result[0]).toHaveProperty('actionableAdvice')
      expect(result[0]).toHaveProperty('confidence')
    })

    it('should categorize risks correctly', async () => {
      const risks = [
        'Heavy rainfall expected',
        'Pest infestation detected',
        'Fungal disease spreading'
      ]

      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      expect(result[0].category).toBe('weather')
      expect(result[1].category).toBe('pest')
      expect(result[2].category).toBe('disease')
    })

    it('should prioritize risks correctly', async () => {
      const risks = [
        'Severe drought conditions',
        'Moderate rainfall expected',
        'Possible pest issues'
      ]

      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      // Severe risks should have higher priority
      const severeRisk = result.find(r => r.text.includes('Severe'))
      expect(severeRisk?.priority).toBeGreaterThan(5)
    })

    it('should handle empty risks array', async () => {
      const result = await service.summarizeWeatherRisks([], 'Lilongwe', 'current', {})
      expect(result).toEqual([])
    })

    it('should handle invalid risks data', async () => {
      const result = await service.summarizeWeatherRisks(null as any, 'Lilongwe', 'current', {})
      expect(result).toEqual([])
    })
  })

  describe('Management Tips Summarization', () => {
    it('should categorize management tips by farming phase', async () => {
      const tips = [
        'Plant seeds in well-prepared soil',
        'Monitor soil moisture regularly',
        'Harvest when crops are mature',
        'Apply fertilizer as needed'
      ]

      const result = await service.summarizeManagementTips(tips, 'Lilongwe', 'current')

      expect(result.planting).toHaveLength(1)
      expect(result.maintenance).toHaveLength(2)
      expect(result.harvest).toHaveLength(1)
      expect(result.general).toHaveLength(0)
    })

    it('should identify actionable tips', async () => {
      const tips = [
        'Apply fertilizer at recommended rates',
        'Monitor crop development',
        'Use proper irrigation techniques'
      ]

      const result = await service.summarizeManagementTips(tips, 'Lilongwe', 'current')

      expect(result.planting[0].actionable).toBe(true)
      expect(result.maintenance[0].actionable).toBe(true)
    })

    it('should handle empty tips array', async () => {
      const result = await service.summarizeManagementTips([], 'Lilongwe', 'current')
      
      expect(result.planting).toEqual([])
      expect(result.maintenance).toEqual([])
      expect(result.harvest).toEqual([])
      expect(result.general).toEqual([])
    })
  })

  describe('Crop Recommendation Enhancement', () => {
    it('should enhance crop recommendations with fallback data', async () => {
      const recommendations = [
        {
          crop_name: 'maize',
          score: 85,
          suitability_level: 'excellent',
          rainfall_match: 'excellent',
          temperature_match: 'good',
          season_suitability: 'excellent'
        }
      ]

      const result = await service.enhanceCropRecommendations(
        recommendations,
        'Lilongwe',
        'current',
        { temperature: 25, rainfall: 50 }
      )

      expect(result).toHaveLength(1)
      expect(result[0]).toHaveProperty('ai_summary')
      expect(result[0]).toHaveProperty('key_benefits')
      expect(result[0]).toHaveProperty('potential_challenges')
      expect(result[0]).toHaveProperty('actionable_steps')
      expect(result[0]).toHaveProperty('seasonal_advice')
      expect(result[0]).toHaveProperty('confidence_score')
    })

    it('should preserve original recommendation data', async () => {
      const recommendations = [
        {
          crop_name: 'maize',
          score: 85,
          suitability_level: 'excellent'
        }
      ]

      const result = await service.enhanceCropRecommendations(
        recommendations,
        'Lilongwe',
        'current',
        {}
      )

      expect(result[0].crop_name).toBe('maize')
      expect(result[0].score).toBe(85)
      expect(result[0].suitability_level).toBe('excellent')
    })

    it('should handle empty recommendations array', async () => {
      const result = await service.enhanceCropRecommendations([], 'Lilongwe', 'current', {})
      expect(result).toEqual([])
    })
  })

  describe('AI Integration (when enabled)', () => {
    beforeEach(() => {
      service = new AISummarizationService({
        enableAI: true,
        cacheEnabled: true,
      })
    })

    it('should call OpenAI API when AI is enabled', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          choices: [{ message: { content: JSON.stringify([{
            summary: 'Test summary',
            category: 'weather',
            severity: 'medium',
            priority: 7,
            actionableAdvice: 'Test advice',
            confidence: 0.8
          }]) } }]
        })
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const risks = ['Test risk']
      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.openai.com/v1/chat/completions',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': expect.stringContaining('Bearer')
          })
        })
      )

      expect(result).toHaveLength(1)
      expect(result[0].summary).toBe('Test summary')
    })

    it('should handle OpenAI API errors gracefully', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const risks = ['Test risk']
      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      // Should fallback to non-AI processing
      expect(result).toHaveLength(1)
      expect(result[0].summary).toContain('Test risk')
    })

    it('should handle malformed AI responses', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          choices: [{ message: { content: 'invalid json' } }]
        })
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const risks = ['Test risk']
      const result = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      // Should fallback to non-AI processing
      expect(result).toHaveLength(1)
      expect(result[0].summary).toContain('Test risk')
    })
  })

  describe('Caching', () => {
    it('should cache results when caching is enabled', async () => {
      service = new AISummarizationService({
        enableAI: false,
        cacheEnabled: true,
      })

      const risks = ['Test risk']
      
      // First call
      const result1 = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})
      
      // Second call should use cache
      const result2 = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      expect(result1).toEqual(result2)
    })

    it('should not cache when caching is disabled', async () => {
      service = new AISummarizationService({
        enableAI: false,
        cacheEnabled: false,
      })

      const risks = ['Test risk']
      
      // Both calls should process independently
      const result1 = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})
      const result2 = await service.summarizeWeatherRisks(risks, 'Lilongwe', 'current', {})

      // Results should be similar but not identical (different IDs)
      expect(result1).toHaveLength(result2.length)
      expect(result1[0].summary).toBe(result2[0].summary)
      expect(result1[0].id).not.toBe(result2[0].id)
    })
  })

  describe('Helper Methods', () => {
    it('should categorize risks correctly', () => {
      const service = new AISummarizationService()
      
      // Access private method through any type
      const categorizeRisk = (service as any).categorizeRisk.bind(service)
      
      expect(categorizeRisk('Heavy rainfall')).toBe('weather')
      expect(categorizeRisk('Pest infestation')).toBe('pest')
      expect(categorizeRisk('Fungal disease')).toBe('disease')
      expect(categorizeRisk('Unknown issue')).toBe('other')
    })

    it('should assess severity correctly', () => {
      const service = new AISummarizationService()
      
      const assessSeverity = (service as any).assessSeverity.bind(service)
      
      expect(assessSeverity('Severe drought')).toBe('high')
      expect(assessSeverity('Moderate rainfall')).toBe('medium')
      expect(assessSeverity('Light rain')).toBe('low')
    })

    it('should calculate priority correctly', () => {
      const service = new AISummarizationService()
      
      const calculatePriority = (service as any).calculatePriority.bind(service)
      
      const highPriorityRisk = calculatePriority('Severe weather conditions')
      const lowPriorityRisk = calculatePriority('Minor issue')
      
      expect(highPriorityRisk).toBeGreaterThan(lowPriorityRisk)
    })
  })
})

describe('Singleton Instance', () => {
  it('should export singleton instance', () => {
    expect(aiSummarizationService).toBeInstanceOf(AISummarizationService)
  })

  it('should have default configuration', () => {
    expect(aiSummarizationService).toBeDefined()
  })
})
