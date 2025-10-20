import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { configureStore } from '@reduxjs/toolkit'
import Weather from '../Weather'

// Mock theme for testing
const theme = createTheme()

// Mock store
const mockStore = configureStore({
  reducer: {
    user: () => ({
      location: { lat: -13.9833, lon: 33.7833, name: 'Lilongwe' }
    })
  }
})

// Mock weather hooks
jest.mock('../../../hooks/useWeatherData', () => ({
  useWeatherData: () => ({
    data: { temperature: 25, humidity: 60 },
    isLoading: false,
    error: null
  }),
  useWeatherForecast: () => ({
    data: { forecast: [] },
    isLoading: false
  }),
  useHistoricalWeather: () => ({
    data: {
      monthly_averages: {
        January: { average_rainfall: 200, min_rainfall: 150, max_rainfall: 250, average_temperature: 25, years_analyzed: 5 },
        February: { average_rainfall: 180, min_rainfall: 120, max_rainfall: 240, average_temperature: 26, years_analyzed: 5 },
        March: { average_rainfall: 160, min_rainfall: 100, max_rainfall: 220, average_temperature: 27, years_analyzed: 5 },
        April: { average_rainfall: 80, min_rainfall: 40, max_rainfall: 120, average_temperature: 28, years_analyzed: 5 },
        May: { average_rainfall: 20, min_rainfall: 0, max_rainfall: 40, average_temperature: 29, years_analyzed: 5 },
        June: { average_rainfall: 5, min_rainfall: 0, max_rainfall: 10, average_temperature: 30, years_analyzed: 5 },
        July: { average_rainfall: 3, min_rainfall: 0, max_rainfall: 8, average_temperature: 31, years_analyzed: 5 },
        August: { average_rainfall: 2, min_rainfall: 0, max_rainfall: 5, average_temperature: 32, years_analyzed: 5 },
        September: { average_rainfall: 8, min_rainfall: 0, max_rainfall: 15, average_temperature: 31, years_analyzed: 5 },
        October: { average_rainfall: 40, min_rainfall: 20, max_rainfall: 60, average_temperature: 30, years_analyzed: 5 },
        November: { average_rainfall: 120, min_rainfall: 80, max_rainfall: 160, average_temperature: 29, years_analyzed: 5 },
        December: { average_rainfall: 180, min_rainfall: 140, max_rainfall: 220, average_temperature: 28, years_analyzed: 5 },
      },
      climate_summary: {
        total_annual_rainfall: 1008,
        wettest_month: 'January',
        driest_month: 'August',
        climate_trend: 'stable',
        drought_risk: 'low',
        analysis_period: 'January 2020 to December 2024'
      },
      years_analyzed: 5,
      location: 'Lilongwe',
      timestamp: '2024-01-01T00:00:00Z'
    },
    isLoading: false
  })
})

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <Provider store={mockStore}>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </Provider>
  )
}

describe('Weather Page Integration', () => {
  describe('Rendering', () => {
    test('renders weather page with all tabs', () => {
      renderWithProviders(<Weather />)
      
      expect(screen.getByText('Weather & Climate')).toBeInTheDocument()
      expect(screen.getByText('Current')).toBeInTheDocument()
      expect(screen.getByText('7-Day Forecast')).toBeInTheDocument()
      expect(screen.getByText('Historical')).toBeInTheDocument()
      expect(screen.getByText('Agricultural Insights')).toBeInTheDocument()
    })

    test('renders historical tab content', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for new components
      expect(screen.getByText('Location Settings')).toBeInTheDocument()
      expect(screen.getByText('Analysis Period')).toBeInTheDocument()
      expect(screen.getByText('Use My Current Location')).toBeInTheDocument()
      expect(screen.getByText('OR Paste Google Maps Link')).toBeInTheDocument()
    })
  })

  describe('Historical Tab Functionality', () => {
    test('displays monthly rainfall table as primary content', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for monthly rainfall table
      expect(screen.getByText('1008 mm')).toBeInTheDocument() // Annual rainfall
      expect(screen.getByText('Annual Rainfall (5 years average)')).toBeInTheDocument()
      expect(screen.getByText('Monthly Rainfall Breakdown')).toBeInTheDocument()
    })

    test('displays visual trends as secondary content', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for visual trends section
      expect(screen.getByText('Visual Trends')).toBeInTheDocument()
    })

    test('allows changing analysis period', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Find and click the analysis period dropdown
      const analysisPeriodSelect = screen.getByLabelText('Years to Analyze')
      fireEvent.mouseDown(analysisPeriodSelect)
      
      // Check for available options
      expect(screen.getByText('1 Year')).toBeInTheDocument()
      expect(screen.getByText('2 Years')).toBeInTheDocument()
      expect(screen.getByText('3 Years')).toBeInTheDocument()
      expect(screen.getByText('5 Years')).toBeInTheDocument()
      expect(screen.getByText('10 Years')).toBeInTheDocument()
    })
  })

  describe('Location Input Integration', () => {
    test('simplified location input is displayed', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for simplified location input
      expect(screen.getByText('Location Settings')).toBeInTheDocument()
      expect(screen.getByText('Use My Current Location')).toBeInTheDocument()
      expect(screen.getByText('OR Paste Google Maps Link')).toBeInTheDocument()
    })

    test('Google Maps URL input is available', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for Google Maps URL input
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      expect(urlInput).toBeInTheDocument()
    })
  })

  describe('Mobile Responsiveness', () => {
    test('components are mobile-friendly', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check that components render without errors on mobile
      expect(screen.getByText('Location Settings')).toBeInTheDocument()
      expect(screen.getByText('Monthly Rainfall Breakdown')).toBeInTheDocument()
    })
  })

  describe('Data Flow', () => {
    test('historical data flows to monthly rainfall table', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check that data is displayed correctly
      expect(screen.getByText('200.0')).toBeInTheDocument() // January rainfall
      expect(screen.getByText('180.0')).toBeInTheDocument() // February rainfall
      expect(screen.getByText('Jan')).toBeInTheDocument()
      expect(screen.getByText('Feb')).toBeInTheDocument()
    })

    test('annual rainfall is prominently displayed', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for prominent annual rainfall display
      expect(screen.getByText('1008 mm')).toBeInTheDocument()
      expect(screen.getByText('Annual Rainfall (5 years average)')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    test('handles missing historical data gracefully', () => {
      // Mock empty historical data
      jest.doMock('../../../hooks/useWeatherData', () => ({
        useWeatherData: () => ({
          data: { temperature: 25, humidity: 60 },
          isLoading: false,
          error: null
        }),
        useWeatherForecast: () => ({
          data: { forecast: [] },
          isLoading: false
        }),
        useHistoricalWeather: () => ({
          data: null,
          isLoading: false
        })
      }))

      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Should show appropriate message
      expect(screen.getByText('Historical data unavailable')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    test('has proper tab navigation', () => {
      renderWithProviders(<Weather />)
      
      const tabs = screen.getAllByRole('tab')
      expect(tabs).toHaveLength(4)
      
      // Check tab labels
      expect(screen.getByRole('tab', { name: 'Current' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: '7-Day Forecast' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Historical' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Agricultural Insights' })).toBeInTheDocument()
    })

    test('has proper form labels', () => {
      renderWithProviders(<Weather />)
      
      // Click on Historical tab
      const historicalTab = screen.getByText('Historical')
      fireEvent.click(historicalTab)
      
      // Check for proper form labels
      expect(screen.getByLabelText('Years to Analyze')).toBeInTheDocument()
    })
  })
})
