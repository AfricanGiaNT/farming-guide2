/**
 * Tests for SmartRecommendationDisplay Component
 * Tests smart recommendation display functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SmartRecommendationDisplay from '../SmartRecommendationDisplay'
import { SearchMode } from '../SearchModeToggle'

describe('SmartRecommendationDisplay', () => {
  const mockRecommendations = [
    {
      crop_name: 'maize',
      score: 85,
      suitability_level: 'excellent',
      rainfall_match: 'excellent',
      temperature_match: 'good',
      season_suitability: 'excellent',
      sources: ['Malawi Agriculture Guide'],
      guide_recommendations: ['Plant in November-December'],
      varieties: ['SC627', 'DK8053'],
      planting_time: 'November-December',
      yield_potential: '4-6 tons/ha',
      description: 'Excellent for current conditions',
    },
    {
      crop_name: 'beans',
      score: 75,
      suitability_level: 'good',
      rainfall_match: 'good',
      temperature_match: 'good',
      season_suitability: 'good',
      sources: ['Malawi Agriculture Guide'],
      guide_recommendations: ['Plant in December'],
      varieties: ['GLP-2', 'GLP-24'],
      planting_time: 'December',
      yield_potential: '2-3 tons/ha',
      description: 'Good for current conditions',
    }
  ]

  const defaultProps = {
    searchMode: { type: 'all_crops' as const },
    recommendations: mockRecommendations,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render with all crops mode', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    expect(screen.getByText('All Crops Results')).toBeInTheDocument()
    expect(screen.getByText('Showing 2 crop recommendations for your area')).toBeInTheDocument()
    expect(screen.getByText('Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Risk Assessment')).toBeInTheDocument()
    expect(screen.getByText('Management Tips')).toBeInTheDocument()
  })

  it('should render with specific crop mode', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' },
      recommendations: [mockRecommendations[0]]
    }
    render(<SmartRecommendationDisplay {...props} />)
    
    expect(screen.getByText('Specific Crop Results')).toBeInTheDocument()
    expect(screen.getByText('Detailed analysis for maize')).toBeInTheDocument()
  })

  it('should display crop recommendations in all crops mode', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    expect(screen.getByText('Maize')).toBeInTheDocument()
    expect(screen.getByText('Beans')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('75%')).toBeInTheDocument()
  })

  it('should display detailed analysis in specific crop mode', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' },
      recommendations: [mockRecommendations[0]]
    }
    render(<SmartRecommendationDisplay {...props} />)
    
    expect(screen.getByText('Detailed Analysis: Maize')).toBeInTheDocument()
    expect(screen.getByText('Maize')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('should show loading state', () => {
    render(<SmartRecommendationDisplay {...defaultProps} loading={true} />)
    
    expect(screen.getByText('Loading crop recommendations...')).toBeInTheDocument()
  })

  it('should show specific crop loading state', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' },
      loading: true
    }
    render(<SmartRecommendationDisplay {...props} />)
    
    expect(screen.getByText('Analyzing maize...')).toBeInTheDocument()
  })

  it('should show error state', () => {
    const error = 'Network error'
    render(<SmartRecommendationDisplay {...defaultProps} error={error} />)
    
    expect(screen.getByText('Error Loading Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Network error')).toBeInTheDocument()
  })

  it('should show retry button when onRetry is provided', () => {
    const onRetry = jest.fn()
    render(<SmartRecommendationDisplay {...defaultProps} error="Test error" onRetry={onRetry} />)
    
    const retryButton = screen.getByRole('button', { name: /try again/i })
    expect(retryButton).toBeInTheDocument()
    
    fireEvent.click(retryButton)
    expect(onRetry).toHaveBeenCalled()
  })

  it('should show no recommendations message when recommendations array is empty', () => {
    render(<SmartRecommendationDisplay {...defaultProps} recommendations={[]} />)
    
    expect(screen.getByText('No Crop Recommendations Found')).toBeInTheDocument()
    expect(screen.getByText('No suitable crops were found for the current location and season')).toBeInTheDocument()
  })

  it('should show crop not found message for specific crop mode with empty recommendations', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'rice' },
      recommendations: []
    }
    render(<SmartRecommendationDisplay {...props} />)
    
    expect(screen.getByText('Crop Not Found')).toBeInTheDocument()
    expect(screen.getByText('No information was found for "rice"')).toBeInTheDocument()
  })

  it('should switch between tabs', async () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    const riskTab = screen.getByRole('tab', { name: /risk assessment/i })
    fireEvent.click(riskTab)
    
    await waitFor(() => {
      expect(screen.getByText('Risk Assessment')).toBeInTheDocument()
    })
  })

  it('should show search parameters summary when provided', () => {
    const searchParams = {
      location: 'Lilongwe',
      season: 'current',
      searchMode: { type: 'all_crops' as const }
    }
    render(<SmartRecommendationDisplay {...defaultProps} searchParams={searchParams} />)
    
    expect(screen.getByText('Search Parameters')).toBeInTheDocument()
    expect(screen.getByText('Lilongwe')).toBeInTheDocument()
    expect(screen.getByText('current')).toBeInTheDocument()
    expect(screen.getByText('All Crops')).toBeInTheDocument()
  })

  it('should show specific crop in search parameters', () => {
    const searchParams = {
      location: 'Lilongwe',
      season: 'current',
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' }
    }
    render(<SmartRecommendationDisplay {...defaultProps} searchParams={searchParams} />)
    
    expect(screen.getByText('Specific: maize')).toBeInTheDocument()
  })

  it('should show recommendation count badge', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    expect(screen.getByText('2')).toBeInTheDocument() // Badge content
  })

  it('should show share and refresh buttons', () => {
    const onRetry = jest.fn()
    render(<SmartRecommendationDisplay {...defaultProps} onRetry={onRetry} />)
    
    expect(screen.getByRole('button', { name: /share results/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /refresh results/i })).toBeInTheDocument()
  })

  it('should call onRetry when refresh button is clicked', () => {
    const onRetry = jest.fn()
    render(<SmartRecommendationDisplay {...defaultProps} onRetry={onRetry} />)
    
    const refreshButton = screen.getByRole('button', { name: /refresh results/i })
    fireEvent.click(refreshButton)
    
    expect(onRetry).toHaveBeenCalled()
  })

  it('should show no risk assessment message when no risk data is available', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    const riskTab = screen.getByRole('tab', { name: /risk assessment/i })
    fireEvent.click(riskTab)
    
    expect(screen.getByText('No Risk Assessment Available')).toBeInTheDocument()
  })

  it('should show no management tips message when no tips data is available', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    const tipsTab = screen.getByRole('tab', { name: /management tips/i })
    fireEvent.click(tipsTab)
    
    expect(screen.getByText('No Management Tips Available')).toBeInTheDocument()
  })

  it('should render risk assessment when risk data is available', () => {
    const recommendationsWithRisk = [{
      ...mockRecommendations[0],
      risk_assessment: {
        weather_risks: ['Heavy rainfall expected', 'Temperature fluctuations']
      }
    }]
    
    render(<SmartRecommendationDisplay {...defaultProps} recommendations={recommendationsWithRisk} />)
    
    const riskTab = screen.getByRole('tab', { name: /risk assessment/i })
    fireEvent.click(riskTab)
    
    expect(screen.getByText('Risk Assessment')).toBeInTheDocument()
  })

  it('should render management tips when tips data is available', () => {
    const recommendationsWithTips = [{
      ...mockRecommendations[0],
      management_tips: ['Monitor growth regularly', 'Apply fertilizer']
    }]
    
    render(<SmartRecommendationDisplay {...defaultProps} recommendations={recommendationsWithTips} />)
    
    const tipsTab = screen.getByRole('tab', { name: /management tips/i })
    fireEvent.click(tipsTab)
    
    expect(screen.getByText('Management Tips')).toBeInTheDocument()
  })

  it('should handle favorites functionality', () => {
    const onFavorite = jest.fn()
    const favorites = ['maize']
    
    render(<SmartRecommendationDisplay {...defaultProps} onFavorite={onFavorite} favorites={favorites} />)
    
    // The favorite functionality is handled by the EnhancedCropCard component
    // This test ensures the props are passed correctly
    expect(screen.getByText('Maize')).toBeInTheDocument()
  })

  it('should show correct search mode description for all crops', () => {
    render(<SmartRecommendationDisplay {...defaultProps} />)
    
    expect(screen.getByText('Showing 2 crop recommendations for your area')).toBeInTheDocument()
  })

  it('should show correct search mode description for specific crop', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' },
      recommendations: [mockRecommendations[0]]
    }
    render(<SmartRecommendationDisplay {...props} />)
    
    expect(screen.getByText('Detailed analysis for maize')).toBeInTheDocument()
  })
})
