/**
 * Tests for Phase 4 API functionality
 * Tests specific crop recommendations API
 */

import { cropAPI } from '../api'

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }))
}))

describe('Phase 4 API Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('getSpecificCropRecommendations', () => {
    it('should call the correct API endpoint for specific crop recommendations', async () => {
      const mockAxios = require('axios')
      const mockResponse = {
        data: {
          crop_name: 'maize',
          recommendations: [{
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }],
          search_mode: 'specific_crop'
        }
      }
      
      mockAxios.create().get.mockResolvedValue(mockResponse)

      const result = await cropAPI.getSpecificCropRecommendations('maize', -13.9833, 33.7833, 'current')

      expect(mockAxios.create().get).toHaveBeenCalledWith('/crops/specific?crop=maize&location=-13.9833,33.7833&season=current')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle API errors gracefully', async () => {
      const mockAxios = require('axios')
      const mockError = new Error('API Error')
      
      mockAxios.create().get.mockRejectedValue(mockError)

      await expect(
        cropAPI.getSpecificCropRecommendations('maize', -13.9833, 33.7833, 'current')
      ).rejects.toThrow('API Error')
    })

    it('should use default season when not provided', async () => {
      const mockAxios = require('axios')
      const mockResponse = { data: {} }
      
      mockAxios.create().get.mockResolvedValue(mockResponse)

      await cropAPI.getSpecificCropRecommendations('maize', -13.9833, 33.7833)

      expect(mockAxios.create().get).toHaveBeenCalledWith('/crops/specific?crop=maize&location=-13.9833,33.7833&season=current')
    })

    it('should handle different seasons correctly', async () => {
      const mockAxios = require('axios')
      const mockResponse = { data: {} }
      
      mockAxios.create().get.mockResolvedValue(mockResponse)

      await cropAPI.getSpecificCropRecommendations('maize', -13.9833, 33.7833, 'rainy')

      expect(mockAxios.create().get).toHaveBeenCalledWith('/crops/specific?crop=maize&location=-13.9833,33.7833&season=rainy')
    })

    it('should handle unsuitable crops', async () => {
      const mockAxios = require('axios')
      const mockResponse = {
        data: {
          crop_name: 'rice',
          recommendations: [{
            crop_name: 'rice',
            score: 25,
            suitability_level: 'poor'
          }],
          search_mode: 'specific_crop',
          unsuitable: true
        }
      }
      
      mockAxios.create().get.mockResolvedValue(mockResponse)

      const result = await cropAPI.getSpecificCropRecommendations('rice', -13.9833, 33.7833, 'dry')

      expect(result.unsuitable).toBe(true)
      expect(result.recommendations[0].suitability_level).toBe('poor')
    })
  })

  describe('API Integration', () => {
    it('should maintain consistency with existing getCropRecommendations', async () => {
      const mockAxios = require('axios')
      const mockResponse = { data: {} }
      
      mockAxios.create().get.mockResolvedValue(mockResponse)

      // Test both endpoints use similar patterns
      await cropAPI.getCropRecommendations(-13.9833, 33.7833, 'current')
      await cropAPI.getSpecificCropRecommendations('maize', -13.9833, 33.7833, 'current')

      expect(mockAxios.create().get).toHaveBeenCalledWith('/crops?location=-13.9833,33.7833&season=current')
      expect(mockAxios.create().get).toHaveBeenCalledWith('/crops/specific?crop=maize&location=-13.9833,33.7833&season=current')
    })
  })
})
