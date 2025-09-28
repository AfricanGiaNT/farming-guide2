import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import '@testing-library/jest-dom'
import CropRecommendations from '../CropRecommendations'
import { cropSlice } from '../../../store/slices/cropSlice'
import { userSlice } from '../../../store/slices/userSlice'

// Mock the hooks
jest.mock('../../../hooks/useCropRecommendations', () => ({
  useCropRecommendations: jest.fn()
}))

// Mock the components
jest.mock('../../../components/Crops/CropRecommendationCard', () => {
  return function MockCropRecommendationCard({ crop }: { crop: any }) {
    return <div data-testid="crop-card">{crop.crop_name}</div>
  }
})

jest.mock('../../../components/Location/LocationPicker', () => {
  return function MockLocationPicker() {
    return <div data-testid="location-picker">Location Picker</div>
  }
})

jest.mock('../../../components/Crops/SeasonalComparison', () => {
  return function MockSeasonalComparison() {
    return <div data-testid="seasonal-comparison">Seasonal Comparison</div>
  }
})

// Mock the data processor
jest.mock('../../../services/cropDataProcessor', () => ({
  cropDataProcessor: {
    validateApiResponse: jest.fn(() => ({ isValid: true, errors: [] })),
    processRiskAssessment: jest.fn((risks) => risks.slice(0, 5)),
    summarizeManagementTips: jest.fn((tips) => ({
      planting: tips.filter((t: string) => t.includes('plant')),
      maintenance: tips.filter((t: string) => t.includes('fertilizer')),
      harvest: tips.filter((t: string) => t.includes('harvest')),
      general: tips.filter((t: string) => !t.includes('plant') && !t.includes('fertilizer') && !t.includes('harvest'))
    })),
    prioritizeRecommendations: jest.fn((recs) => recs)
  }
}))

const createMockStore = (initialState = {}) => {
  return configureStore({
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
        ...initialState.crop
      },
      user: {
        location: { lat: -13.9833, lon: 33.7833 },
        ...initialState.user
      }
    }
  })
}

const mockCropData = {
  recommendations: [
    {
      crop_name: 'maize',
      score: 85,
      suitability_level: 'excellent',
      rainfall_match: 'excellent',
      temperature_match: 'excellent',
      season_suitability: 'excellent',
      sources: ['Malawi Agriculture Guide'],
      guide_recommendations: ['Plant in November', 'Use certified seeds'],
      varieties: ['SC627', 'DK8053'],
      planting_time: 'November-December',
      yield_potential: '4-6 tons/ha'
    }
  ],
  risk_assessment: {
    overall_risk_level: 'moderate',
    weather_risks: [
      'Heavy rainfall expected in the next 2 weeks',
      'Drought conditions may affect crop growth',
      'High temperature stress during flowering period',
      'Pest infestation risk due to wet conditions',
      'Disease outbreak potential in humid weather',
      'Soil erosion from excessive rainfall',
      'Flooding risk in low-lying areas',
      'Wind damage to young plants',
      'Frost damage during cold spells',
      'Hail damage to crops',
      'Lightning strikes affecting irrigation',
      'Heat wave conditions',
      'Low humidity affecting pollination',
      'Excessive cloud cover reducing photosynthesis'
    ],
    pest_risks: ['Stem borer attack', 'Leaf spot disease']
  },
  management_tips: [
    'Plant seeds at proper depth',
    'Apply fertilizer every 6 weeks',
    'Harvest when crops are mature',
    'Monitor soil moisture regularly'
  ],
  planting_advice: {
    optimal_planting_window: 'November-December',
    soil_preparation: 'Prepare land 2-3 weeks before planting',
    seed_requirements: 'Use certified seeds for best results'
  },
  environmental_summary: {
    total_7day_rainfall: 50,
    current_temperature: 25,
    humidity: 65
  },
  seasonal_advice: {
    general_advice: 'Current conditions are favorable for planting',
    timing_recommendations: 'Plant within the next 2 weeks',
    weather_considerations: 'Monitor rainfall patterns',
    risk_mitigation: 'Prepare for potential weather risks'
  },
  sources: ['Malawi Agriculture Guide'],
  historical_data: 5,
  timestamp: '2025-01-01T00:00:00Z'
}

describe('CropRecommendations', () => {
  const mockUseCropRecommendations = require('../../../hooks/useCropRecommendations').useCropRecommendations

  beforeEach(() => {
    mockUseCropRecommendations.mockReturnValue({
      data: mockCropData,
      isLoading: false,
      error: null,
      refetch: jest.fn()
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should render crop recommendations page', () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    expect(screen.getByText('Crop Recommendations')).toBeInTheDocument()
    expect(screen.getByText(/Get personalized crop recommendations/)).toBeInTheDocument()
  })

  it('should display Risk Assessment immediately after search form', async () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    await waitFor(() => {
      expect(screen.getByText('Risk Assessment')).toBeInTheDocument()
    })

    // Check that Risk Assessment appears before other sections
    const riskAssessment = screen.getByText('Risk Assessment')
    const environmentalConditions = screen.getByText('Environmental Conditions')
    
    expect(riskAssessment.compareDocumentPosition(environmentalConditions)).toBe(Node.DOCUMENT_POSITION_FOLLOWING)
  })

  it('should limit weather risks to maximum 5 items', async () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    await waitFor(() => {
      expect(screen.getByText(/Weather Risks \(5\):/)).toBeInTheDocument()
    })

    // Should show only 5 risks even though mock data has 14
    const riskItems = screen.getAllByText(/•/)
    const weatherRisks = riskItems.filter(item => 
      item.textContent?.includes('rainfall') || 
      item.textContent?.includes('Drought') ||
      item.textContent?.includes('temperature') ||
      item.textContent?.includes('Pest') ||
      item.textContent?.includes('Disease')
    )
    
    expect(weatherRisks).toHaveLength(5)
  })

  it('should categorize management tips by farming phase', async () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    await waitFor(() => {
      expect(screen.getByText('Management Tips')).toBeInTheDocument()
    })

    expect(screen.getByText('🌱 Planting Phase:')).toBeInTheDocument()
    expect(screen.getByText('🔧 Maintenance Phase:')).toBeInTheDocument()
    expect(screen.getByText('🌾 Harvest Phase:')).toBeInTheDocument()
  })

  it('should handle malformed API responses gracefully', async () => {
    const malformedData = {
      recommendations: 'not an array',
      risk_assessment: null,
      management_tips: undefined
    }

    mockUseCropRecommendations.mockReturnValue({
      data: malformedData,
      isLoading: false,
      error: null,
      refetch: jest.fn()
    })

    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    // Should not crash and should show basic structure
    expect(screen.getByText('Crop Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Search & Input Options')).toBeInTheDocument()
  })

  it('should display crop recommendations when available', async () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    await waitFor(() => {
      expect(screen.getByText('Recommended Crops')).toBeInTheDocument()
    })

    expect(screen.getByTestId('crop-card')).toBeInTheDocument()
    expect(screen.getByText('maize')).toBeInTheDocument()
  })

  it('should handle season changes', async () => {
    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    const rainySeasonTab = screen.getByText('Rainy Season')
    fireEvent.click(rainySeasonTab)

    await waitFor(() => {
      expect(screen.getByText(/November - April: Main growing season/)).toBeInTheDocument()
    })
  })

  it('should show loading state', () => {
    mockUseCropRecommendations.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: jest.fn()
    })

    const store = createMockStore({ crop: { loading: true } })
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    // Should show skeleton loading
    expect(screen.getAllByTestId(/skeleton/i)).toHaveLength(6)
  })

  it('should show error state', () => {
    mockUseCropRecommendations.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('API Error'),
      refetch: jest.fn()
    })

    const store = createMockStore({ crop: { error: 'API Error' } })
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    expect(screen.getByText(/Unable to fetch crop recommendations/)).toBeInTheDocument()
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('should handle empty recommendations', async () => {
    const emptyData = {
      ...mockCropData,
      recommendations: []
    }

    mockUseCropRecommendations.mockReturnValue({
      data: emptyData,
      isLoading: false,
      error: null,
      refetch: jest.fn()
    })

    const store = createMockStore()
    
    render(
      <Provider store={store}>
        <CropRecommendations />
      </Provider>
    )

    await waitFor(() => {
      expect(screen.getByText('No recommendations available')).toBeInTheDocument()
    })
  })
})
