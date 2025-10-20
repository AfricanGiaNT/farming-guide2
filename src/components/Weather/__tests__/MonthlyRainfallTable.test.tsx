import React from 'react'
import { render, screen } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import MonthlyRainfallTable from '../MonthlyRainfallTable'

// Mock theme for testing
const theme = createTheme()

const mockHistoricalData = {
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
}

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  )
}

describe('MonthlyRainfallTable', () => {
  describe('Loading State', () => {
    test('shows loading message when loading is true', () => {
      renderWithTheme(<MonthlyRainfallTable historical={null} loading={true} />)
      
      expect(screen.getByText('Loading monthly rainfall data...')).toBeInTheDocument()
    })
  })

  describe('No Data States', () => {
    test('shows unavailable message when historical data is null', () => {
      renderWithTheme(<MonthlyRainfallTable historical={null} loading={false} />)
      
      expect(screen.getByText('Historical data unavailable')).toBeInTheDocument()
      expect(screen.getByText('Please check your location settings and try again.')).toBeInTheDocument()
    })

    test('shows unavailable message when monthly_averages is missing', () => {
      const dataWithoutMonthly = {
        ...mockHistoricalData,
        monthly_averages: undefined
      }
      
      renderWithTheme(<MonthlyRainfallTable historical={dataWithoutMonthly} loading={false} />)
      
      expect(screen.getByText('Monthly averages data unavailable')).toBeInTheDocument()
    })
  })

  describe('Data Display', () => {
    test('displays annual rainfall prominently', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('1008 mm')).toBeInTheDocument()
      expect(screen.getByText('Annual Rainfall (5 years average)')).toBeInTheDocument()
    })

    test('displays all 12 months in table', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      // Check for abbreviated month names
      expect(screen.getByText('Jan')).toBeInTheDocument()
      expect(screen.getByText('Feb')).toBeInTheDocument()
      expect(screen.getByText('Mar')).toBeInTheDocument()
      expect(screen.getByText('Apr')).toBeInTheDocument()
      expect(screen.getByText('May')).toBeInTheDocument()
      expect(screen.getByText('Jun')).toBeInTheDocument()
      expect(screen.getByText('Jul')).toBeInTheDocument()
      expect(screen.getByText('Aug')).toBeInTheDocument()
      expect(screen.getByText('Sep')).toBeInTheDocument()
      expect(screen.getByText('Oct')).toBeInTheDocument()
      expect(screen.getByText('Nov')).toBeInTheDocument()
      expect(screen.getByText('Dec')).toBeInTheDocument()
    })

    test('displays rainfall values for each month', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('200.0')).toBeInTheDocument() // January
      expect(screen.getByText('180.0')).toBeInTheDocument() // February
      expect(screen.getByText('160.0')).toBeInTheDocument() // March
    })

    test('displays rainfall ranges', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('150-250')).toBeInTheDocument() // January range
      expect(screen.getByText('120-240')).toBeInTheDocument() // February range
    })

    test('displays rainfall level chips', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getAllByText('High')).toHaveLength(3) // Jan, Feb, Dec
      expect(screen.getAllByText('Moderate')).toHaveLength(2) // Mar, Nov
      expect(screen.getAllByText('Low')).toHaveLength(1) // Apr
      expect(screen.getAllByText('Very Low')).toHaveLength(6) // May, Jun, Jul, Aug, Sep, Oct
    })
  })

  describe('Special Month Indicators', () => {
    test('highlights wettest month', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('Wettest')).toBeInTheDocument()
    })

    test('highlights driest month', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('Driest')).toBeInTheDocument()
    })
  })

  describe('Agricultural Insights', () => {
    test('displays wet season months', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText(/Wet Season:/)).toBeInTheDocument()
    })

    test('displays dry season months', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText(/Dry Season:/)).toBeInTheDocument()
    })

    test('shows climate variability warning', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText(/High rainfall variability/)).toBeInTheDocument()
    })
  })

  describe('Climate Trend Warnings', () => {
    test('shows drought warning for decreasing trend', () => {
      const dataWithDecreasingTrend = {
        ...mockHistoricalData,
        climate_summary: {
          ...mockHistoricalData.climate_summary,
          climate_trend: 'decreasing'
        }
      }
      
      renderWithTheme(<MonthlyRainfallTable historical={dataWithDecreasingTrend} loading={false} />)
      
      expect(screen.getByText(/Decreasing rainfall trend detected/)).toBeInTheDocument()
    })

    test('does not show drought warning for stable trend', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.queryByText(/Decreasing rainfall trend detected/)).not.toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    test('handles missing month data gracefully', () => {
      const dataWithMissingMonth = {
        ...mockHistoricalData,
        monthly_averages: {
          ...mockHistoricalData.monthly_averages,
          January: undefined
        }
      }
      
      renderWithTheme(<MonthlyRainfallTable historical={dataWithMissingMonth} loading={false} />)
      
      // Should still render the table
      expect(screen.getByText('Monthly Rainfall Breakdown')).toBeInTheDocument()
    })

    test('handles zero rainfall values', () => {
      const dataWithZeroRainfall = {
        ...mockHistoricalData,
        monthly_averages: {
          ...mockHistoricalData.monthly_averages,
          January: { average_rainfall: 0, min_rainfall: 0, max_rainfall: 0, average_temperature: 25, years_analyzed: 5 }
        }
      }
      
      renderWithTheme(<MonthlyRainfallTable historical={dataWithZeroRainfall} loading={false} />)
      
      expect(screen.getByText('0.0')).toBeInTheDocument()
      expect(screen.getByText('Very Low')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    test('has proper table structure', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
      
      const headers = screen.getAllByRole('columnheader')
      expect(headers).toHaveLength(4) // Month, Rainfall, Range, Level
    })

    test('has descriptive text for screen readers', () => {
      renderWithTheme(<MonthlyRainfallTable historical={mockHistoricalData} loading={false} />)
      
      expect(screen.getByText('Monthly Rainfall Breakdown')).toBeInTheDocument()
      expect(screen.getByText('Agricultural Insights')).toBeInTheDocument()
    })
  })
})
