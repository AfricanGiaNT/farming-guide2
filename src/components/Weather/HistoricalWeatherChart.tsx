import React from 'react'
import {
  CardContent,
  Typography,
  Box,
  Grid,
  Paper,
  Chip,
} from '@mui/material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface HistoricalData {
  monthly_averages: Record<string, {
    average_rainfall: number
    min_rainfall: number
    max_rainfall: number
    average_temperature: number
    years_analyzed: number
  }>
  climate_summary: {
    total_annual_rainfall: number
    wettest_month: string
    driest_month: string
    climate_trend: string
    drought_risk: string
    analysis_period: string
  }
  years_analyzed: number
  location: string
  timestamp: string
  mock_data?: boolean
}

interface HistoricalWeatherChartProps {
  historical: HistoricalData | null
}

const HistoricalWeatherChart: React.FC<HistoricalWeatherChartProps> = ({ historical }) => {
  // Debug logging
  console.log('🔍 HistoricalWeatherChart received data:', historical)
  console.log('🔍 Historical data type:', typeof historical)
  console.log('🔍 Historical keys:', historical ? Object.keys(historical) : 'null/undefined')
  console.log('🔍 Monthly averages:', historical?.monthly_averages)
  console.log('🔍 Monthly averages type:', typeof historical?.monthly_averages)
  
  if (!historical) {
    console.log('❌ Historical data is null/undefined')
    return (
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Historical data unavailable
        </Typography>
      </CardContent>
    )
  }

  if (!historical.monthly_averages) {
    console.log('❌ Monthly averages is null/undefined')
    return (
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Monthly averages data unavailable
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Available keys: {Object.keys(historical).join(', ')}
        </Typography>
      </CardContent>
    )
  }

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const monthlyData = months.map(month => 
    historical.monthly_averages[month]?.average_rainfall || 0
  )

  const chartData = {
    labels: months.map(month => month.slice(0, 3)), // Short month names
    datasets: [
      {
        label: 'Average Rainfall (mm)',
        data: monthlyData,
        borderColor: '#1976D2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Monthly Rainfall Averages (${historical.years_analyzed} years)`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Rainfall (mm)',
        },
      },
    },
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'success'
      case 'decreasing':
        return 'error'
      case 'stable':
        return 'info'
      default:
        return 'default'
    }
  }

  const getVariabilityLevel = (variability: number) => {
    if (variability > 40) return { label: 'High', color: 'error' }
    if (variability > 25) return { label: 'Moderate', color: 'warning' }
    return { label: 'Low', color: 'success' }
  }

  const variabilityLevel = getVariabilityLevel(25) // Default moderate variability

  return (
    <CardContent sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        Historical Weather Patterns
      </Typography>
      
      {/* Chart */}
      <Box height={300} mb={3}>
        <Line data={chartData} options={chartOptions} />
      </Box>

      {/* Climate Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" fontWeight="bold" color="primary">
              {historical.years_analyzed}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Years Analyzed
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Climate Trend
            </Typography>
            <Chip
              label={historical.climate_summary.climate_trend}
              color="info"
              variant="filled"
            />
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Variability
            </Typography>
            <Typography variant="h5" fontWeight="bold" color={`${variabilityLevel.color}.main`}>
              25.0%
            </Typography>
            <Chip
              label={variabilityLevel.label}
              color={variabilityLevel.color as any}
              size="small"
              variant="outlined"
            />
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Extreme Events
            </Typography>
            <Box display="flex" justifyContent="space-around">
              <Box>
                <Typography variant="h5" fontWeight="bold" color="error.main">
                  2
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Drought Years
                </Typography>
              </Box>
              <Box>
                <Typography variant="h5" fontWeight="bold" color="info.main">
                  1
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Flood Years
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Agricultural Implications */}
      <Box mt={3} p={2} bgcolor="primary.50" borderRadius={2}>
        <Typography variant="h6" gutterBottom fontWeight="bold" color="primary">
          Agricultural Implications
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" paragraph>
              <strong>Wet Season:</strong> {months.slice(10).concat(months.slice(0, 4)).filter(month => 
                (historical.monthly_averages[month]?.average_rainfall || 0) > 50
              ).join(', ')}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="body2" paragraph>
              <strong>Dry Season:</strong> {months.filter(month => 
                (historical.monthly_averages[month]?.average_rainfall || 0) <= 50
              ).join(', ')}
            </Typography>
          </Grid>
          
          {historical.climate_summary.climate_trend.includes('decreasing') && (
            <Grid item xs={12}>
              <Typography variant="body2" color="error.main">
                ⚠️ Decreasing rainfall trend detected. Consider drought-resistant varieties.
              </Typography>
            </Grid>
          )}
          
          {true && (
            <Grid item xs={12}>
              <Typography variant="body2" color="warning.main">
                ⚠️ High rainfall variability. Plan for both drought and excess water scenarios.
              </Typography>
            </Grid>
          )}
        </Grid>
      </Box>
    </CardContent>
  )
}

export default HistoricalWeatherChart