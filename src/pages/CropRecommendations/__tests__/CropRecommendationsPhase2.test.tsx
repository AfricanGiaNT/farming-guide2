/**
 * Integration Tests for CropRecommendations Component - Phase 2
 * Tests AI enhancement and comprehensive data processing integration
 */

import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import CropRecommendations from '../CropRecommendations'
import { cropSlice } from '../../../store/slices/cropSlice'
import { userSlice } from '../../../store/slices/userSlice'

// Mock the crop data processor
jest.mock('../../../services/cropDataProcessor', () => ({
  cropDataProcessor: {
    processComprehensiveData: jest.fn(),
  }
}))

// Mock the API hook
jest.mock('../../../hooks/useCropRecommendations', () => ({
  useCropRecommendations: jest.fn(),
}))

import { cropDataProcessor } from '../../../services/cropDataProcessor'
import { useCropRecommendations } from '../../../hooks/useCropRecommendations'

const mockCropDataProcessor = cropDataProcessor as jest.Mocked<typeof cropDataProcessor>
const mockUseCropRecommendations = useCropRecommendations as jest.MockedFunction<typeof useCropRecommendations>

describe('CropRecommendations Phase 2 Integration', () => {
  let store: any

  beforeEach(() => {
    store = configureStore({
      reducer: {
        crop: cropSlice.reducer,
        user: userSlice.reducer,
      },
      preloadedState: {
        crop: {
          selectedSeason: 'current',
          recommendations: [],
          loading: false,
          error: null,
        },
        user: {
          location: { lat: -13.9833, lon: 33.7833 },
          preferences: {},
        },
      },
    })

    jest.clearAllMocks()
  })

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )
  }

  describe('AI Enhancement Processing', () => {
    it('should show processing status when AI enhancement is active', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent',
            rainfall_match: 'excellent',
            temperature_match: 'good',
            season_suitability: 'excellent'
          }
        ],
        risk_assessment: {
          weather_risks: ['Heavy rainfall expected']
        },
        management_tips: ['Monitor soil moisture'],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      const mockProcessedData = {
        ...mockCropData,
        processing_metadata: {
          location: '-13.9833,33.7833',
          season: 'current',
          timestamp: '2024-01-01T00:00:00.000Z',
          ai_enhanced: true,
          processing_version: '2.0',
          validation: {
            isValid: true,
            qualityScore: 0.9,
            errorCount: 0,
            warningCount: 0,
            qualityMetrics: {
              completeness: 1.0,
              accuracy: 0.9,
              relevance: 0.8,
              clarity: 0.9,
              overall: 0.9
            }
          }
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockProcessedData)

      renderComponent()

      // Should show processing status initially
      expect(screen.getByText('Processing data with AI enhancement...')).toBeInTheDocument()

      // Wait for processing to complete
      await waitFor(() => {
        expect(screen.getByText('✨ Data enhanced with AI summarization')).toBeInTheDocument()
      })

      // Should call the comprehensive data processor
      expect(mockCropDataProcessor.processComprehensiveData).toHaveBeenCalledWith(
        mockCropData,
        '-13.9833,33.7833',
        'current',
        {
          temperature: 25,
          rainfall: 50,
          humidity: 60
        }
      )
    })

    it('should show fallback status when AI enhancement fails', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      const mockProcessedData = {
        ...mockCropData,
        processing_metadata: {
          location: '-13.9833,33.7833',
          season: 'current',
          timestamp: '2024-01-01T00:00:00.000Z',
          ai_enhanced: false,
          processing_version: '2.0-fallback',
          error: 'AI enhancement failed',
          validation: {
            isValid: true,
            qualityScore: 0.7,
            errorCount: 0,
            warningCount: 0,
            qualityMetrics: {
              completeness: 0.8,
              accuracy: 0.8,
              relevance: 0.7,
              clarity: 0.8,
              overall: 0.8
            }
          }
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockProcessedData)

      renderComponent()

      // Wait for processing to complete
      await waitFor(() => {
        expect(screen.getByText('⚠️ Using fallback processing (AI enhancement unavailable)')).toBeInTheDocument()
      })
    })

    it('should handle processing errors gracefully', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      // Simulate processing error
      mockCropDataProcessor.processComprehensiveData.mockRejectedValue(
        new Error('Processing failed')
      )

      renderComponent()

      // Should show fallback status
      await waitFor(() => {
        expect(screen.getByText('⚠️ Using fallback processing (AI enhancement unavailable)')).toBeInTheDocument()
      })

      // Should still display the original data
      expect(screen.getByText('maize')).toBeInTheDocument()
    })
  })

  describe('Data Quality Monitoring', () => {
    it('should log processing metadata for monitoring', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      const mockProcessedData = {
        ...mockCropData,
        processing_metadata: {
          location: '-13.9833,33.7833',
          season: 'current',
          timestamp: '2024-01-01T00:00:00.000Z',
          ai_enhanced: true,
          processing_version: '2.0',
          validation: {
            isValid: true,
            qualityScore: 0.9,
            errorCount: 0,
            warningCount: 1,
            qualityMetrics: {
              completeness: 1.0,
              accuracy: 0.9,
              relevance: 0.8,
              clarity: 0.9,
              overall: 0.9
            }
          }
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockProcessedData)

      renderComponent()

      // Wait for processing to complete
      await waitFor(() => {
        expect(screen.getByText('✨ Data enhanced with AI summarization')).toBeInTheDocument()
      })

      // Should log processing metadata
      expect(consoleSpy).toHaveBeenCalledWith(
        'Data processing completed:',
        mockProcessedData.processing_metadata
      )

      consoleSpy.mockRestore()
    })

    it('should handle validation warnings appropriately', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        risk_assessment: {
          weather_risks: Array(20).fill('Risk item') // Too many risks
        },
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      const mockProcessedData = {
        ...mockCropData,
        processing_metadata: {
          location: '-13.9833,33.7833',
          season: 'current',
          timestamp: '2024-01-01T00:00:00.000Z',
          ai_enhanced: true,
          processing_version: '2.0',
          validation: {
            isValid: true,
            qualityScore: 0.7,
            errorCount: 0,
            warningCount: 1,
            qualityMetrics: {
              completeness: 1.0,
              accuracy: 0.8,
              relevance: 0.7,
              clarity: 0.6,
              overall: 0.8
            }
          }
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockProcessedData)

      renderComponent()

      // Should still show enhanced status despite warnings
      await waitFor(() => {
        expect(screen.getByText('✨ Data enhanced with AI summarization')).toBeInTheDocument()
      })
    })
  })

  describe('Season and Location Context', () => {
    it('should pass correct context to data processor', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        environmental_summary: {
          current_temperature: 30,
          total_7day_rainfall: 100,
          humidity: 70
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockCropData)

      // Update store to different season
      store.dispatch(cropSlice.actions.setSelectedSeason('rainy'))

      renderComponent()

      await waitFor(() => {
        expect(mockCropDataProcessor.processComprehensiveData).toHaveBeenCalledWith(
          mockCropData,
          '-13.9833,33.7833',
          'rainy', // Should use updated season
          {
            temperature: 30,
            rainfall: 100,
            humidity: 70
          }
        )
      })
    })

    it('should handle missing environmental data gracefully', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ]
        // Missing environmental_summary
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockCropData)

      renderComponent()

      await waitFor(() => {
        expect(mockCropDataProcessor.processComprehensiveData).toHaveBeenCalledWith(
          mockCropData,
          '-13.9833,33.7833',
          'current',
          {
            temperature: 25, // Default values
            rainfall: 0,
            humidity: 50
          }
        )
      })
    })
  })

  describe('Performance and Caching', () => {
    it('should not reprocess data unnecessarily', async () => {
      const mockCropData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      mockUseCropRecommendations.mockReturnValue({
        data: mockCropData,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      })

      mockCropDataProcessor.processComprehensiveData.mockResolvedValue(mockCropData)

      const { rerender } = renderComponent()

      // Wait for initial processing
      await waitFor(() => {
        expect(mockCropDataProcessor.processComprehensiveData).toHaveBeenCalledTimes(1)
      })

      // Rerender with same data
      rerender(
        <Provider store={store}>
          <CropRecommendations />
        </Provider>
      )

      // Should not reprocess
      expect(mockCropDataProcessor.processComprehensiveData).toHaveBeenCalledTimes(1)
    })
  })
})
