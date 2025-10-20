import React from 'react'
import { render, screen } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import MonthlyRainfallTable from '../MonthlyRainfallTable'

const theme = createTheme()

const baseHistorical: any = {
  monthly_averages: {
    January: { average_rainfall: 200, min_rainfall: 150, max_rainfall: 250, average_temperature: 25, years_analyzed: 2 },
    February: { average_rainfall: 180, min_rainfall: 120, max_rainfall: 240, average_temperature: 26, years_analyzed: 2 },
    March: { average_rainfall: 160, min_rainfall: 100, max_rainfall: 220, average_temperature: 27, years_analyzed: 2 },
    April: { average_rainfall: 80, min_rainfall: 40, max_rainfall: 120, average_temperature: 28, years_analyzed: 2 },
    May: { average_rainfall: 20, min_rainfall: 0, max_rainfall: 40, average_temperature: 29, years_analyzed: 2 },
    June: { average_rainfall: 5, min_rainfall: 0, max_rainfall: 10, average_temperature: 30, years_analyzed: 2 },
    July: { average_rainfall: 3, min_rainfall: 0, max_rainfall: 8, average_temperature: 31, years_analyzed: 2 },
    August: { average_rainfall: 2, min_rainfall: 0, max_rainfall: 5, average_temperature: 32, years_analyzed: 2 },
    September: { average_rainfall: 8, min_rainfall: 0, max_rainfall: 15, average_temperature: 31, years_analyzed: 2 },
    October: { average_rainfall: 40, min_rainfall: 20, max_rainfall: 60, average_temperature: 30, years_analyzed: 2 },
    November: { average_rainfall: 120, min_rainfall: 80, max_rainfall: 160, average_temperature: 29, years_analyzed: 2 },
    December: { average_rainfall: 180, min_rainfall: 140, max_rainfall: 220, average_temperature: 28, years_analyzed: 2 },
  },
  climate_summary: {
    total_annual_rainfall: 900,
    wettest_month: 'January',
    driest_month: 'August',
    climate_trend: 'stable',
    drought_risk: 'low',
    analysis_period: 'October 2023 to October 2025'
  },
  years_analyzed: 2,
  location: 'Lilongwe',
  timestamp: '2025-10-20T00:00:00Z',
}

const renderWithTheme = (ui: React.ReactElement) => render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>)

describe('Year Accordions', () => {
  test('shows multi-year annual average and year accordions', () => {
    const data: any = {
      ...baseHistorical,
      per_year: [
        { year: 2025, annual_rainfall: 608, monthly: { January: 517.3 }, months_covered: 12, coverage: 'full' },
        { year: 2024, annual_rainfall: 606, monthly: { January: 277.8 }, months_covered: 10, coverage: 'partial' },
      ],
      multi_year: {
        annual_average: (608 + 606) / 2,
        monthly_average: { January: (517.3 + 277.8) / 2 },
      },
    }

    renderWithTheme(<MonthlyRainfallTable historical={data} />)

    // Annual average displayed (rounded in UI heading)
    expect(screen.getByText(`${Math.round(((608 + 606) / 2))} mm`)).toBeInTheDocument()

    // Accordions show both years
    expect(screen.getByText('2025')).toBeInTheDocument()
    expect(screen.getByText('2024')).toBeInTheDocument()
    // Partial badge present for partial year
    expect(screen.getByText(/Partial \(10\/12\)/)).toBeInTheDocument()
  })
})
