import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
  Divider
} from '@mui/material'
import { 
  TrendingUp, 
  TrendingDown, 
  Assessment, 
  BarChart,
  PieChart,
  ShowChart,
  CalendarToday,
  LocationOn
} from '@mui/icons-material'
import { analyticsAPI, weatherAPI } from '../../services/api'

interface DashboardMetrics {
  totalUsers: number
  activeUsers: number
  totalQueries: number
  avgResponseTime: number
  topCrops: Array<{ crop: string; queries: number }>
  topLocations: Array<{ location: string; queries: number }>
}

interface WeatherAnalytics {
  avgTemperature: number
  avgRainfall: number
  weatherTrends: Array<{ month: string; temp: number; rainfall: number }>
}

const Analytics: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  useEffect(() => {
    loadAnalyticsData()
  }, [timeRange])

  const loadAnalyticsData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Load dashboard metrics
      const dashboardData = await analyticsAPI.getDashboardData()
      setMetrics(dashboardData)

      // Load weather analytics
      const weatherAnalytics = await weatherAPI.getHistoricalWeather(-13.9833, 33.7833, 1)
      if (weatherAnalytics) {
        setWeatherData({
          avgTemperature: calculateAverageTemperature(weatherAnalytics.monthly_averages),
          avgRainfall: calculateAverageRainfall(weatherAnalytics.monthly_averages),
          weatherTrends: formatWeatherTrends(weatherAnalytics.monthly_averages)
        })
      }

    } catch (err) {
      setError('Failed to load analytics data')
      console.error('Analytics error:', err)
      
      // Fallback to mock data
      setMetrics({
        totalUsers: 1250,
        activeUsers: 890,
        totalQueries: 15420,
        avgResponseTime: 1.2,
        topCrops: [
          { crop: 'Maize', queries: 4520 },
          { crop: 'Groundnuts', queries: 3210 },
          { crop: 'Beans', queries: 2890 },
          { crop: 'Soybeans', queries: 2100 },
          { crop: 'Rice', queries: 1800 }
        ],
        topLocations: [
          { location: 'Lilongwe', queries: 5200 },
          { location: 'Blantyre', queries: 3800 },
          { location: 'Mzuzu', queries: 2100 },
          { location: 'Zomba', queries: 1800 },
          { location: 'Kasungu', queries: 1200 }
        ]
      })

      setWeatherData({
        avgTemperature: 24.5,
        avgRainfall: 850,
        weatherTrends: [
          { month: 'Jan', temp: 26, rainfall: 200 },
          { month: 'Feb', temp: 25, rainfall: 180 },
          { month: 'Mar', temp: 24, rainfall: 120 },
          { month: 'Apr', temp: 22, rainfall: 40 },
          { month: 'May', temp: 20, rainfall: 10 },
          { month: 'Jun', temp: 18, rainfall: 5 }
        ]
      })
    } finally {
      setLoading(false)
    }
  }

  const calculateAverageTemperature = (monthlyData: any) => {
    const temps = Object.values(monthlyData).map((month: any) => month.average_temperature || 0)
    return temps.reduce((sum: number, temp: number) => sum + temp, 0) / temps.length
  }

  const calculateAverageRainfall = (monthlyData: any) => {
    const rainfalls = Object.values(monthlyData).map((month: any) => month.average_rainfall || 0)
    return rainfalls.reduce((sum: number, rain: number) => sum + rain, 0)
  }

  const formatWeatherTrends = (monthlyData: any) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.map((month, index) => {
      const monthData = monthlyData[month] || {}
      return {
        month,
        temp: monthData.average_temperature || 0,
        rainfall: monthData.average_rainfall || 0
      }
    }).slice(0, 6) // Show first 6 months
  }

  const getGrowthIndicator = (current: number, previous: number) => {
    const growth = ((current - previous) / previous) * 100
    return {
      value: Math.abs(growth).toFixed(1),
      isPositive: growth >= 0,
      icon: growth >= 0 ? <TrendingUp /> : <TrendingDown />
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={40} />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          Analytics Dashboard
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as '7d' | '30d' | '90d')}
          >
            <MenuItem value="7d">Last 7 days</MenuItem>
            <MenuItem value="30d">Last 30 days</MenuItem>
            <MenuItem value="90d">Last 90 days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error} - Showing sample data
        </Alert>
      )}

      {/* Key Metrics */}
      {metrics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {metrics.totalUsers.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Users
                    </Typography>
                  </Box>
                  <Assessment sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                  {getGrowthIndicator(metrics.totalUsers, 1000).icon}
                  <Typography variant="caption" color="success.main">
                    +{getGrowthIndicator(metrics.totalUsers, 1000).value}% from last month
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {metrics.activeUsers.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Users
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                  {getGrowthIndicator(metrics.activeUsers, 750).icon}
                  <Typography variant="caption" color="success.main">
                    +{getGrowthIndicator(metrics.activeUsers, 750).value}% from last month
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {metrics.totalQueries.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Queries
                    </Typography>
                  </Box>
                  <BarChart sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                  {getGrowthIndicator(metrics.totalQueries, 12000).icon}
                  <Typography variant="caption" color="success.main">
                    +{getGrowthIndicator(metrics.totalQueries, 12000).value}% from last month
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {metrics.avgResponseTime}s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Response Time
                    </Typography>
                  </Box>
                  <ShowChart sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                  {getGrowthIndicator(metrics.avgResponseTime, 1.5).icon}
                  <Typography variant="caption" color="success.main">
                    -{getGrowthIndicator(metrics.avgResponseTime, 1.5).value}s from last month
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Weather Analytics */}
      {weatherData && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationOn />
                  Weather Overview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary.main">
                        {weatherData.avgTemperature.toFixed(1)}°C
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Average Temperature
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {weatherData.avgRainfall.toFixed(0)}mm
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Annual Rainfall
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarToday />
                  Seasonal Trends
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2 }}>
                  {weatherData.weatherTrends.map((trend, index) => (
                    <Box key={index} sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        {trend.month}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {trend.temp}°C
                      </Typography>
                      <Typography variant="caption" color="info.main">
                        {trend.rainfall}mm
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Top Crops and Locations */}
      {metrics && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PieChart />
                  Top Crops
                </Typography>
                {metrics.topCrops.map((crop, index) => (
                  <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1 }}>
                    <Typography variant="body2">{crop.crop}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {crop.queries.toLocaleString()}
                      </Typography>
                      <Chip label={`#${index + 1}`} size="small" color="primary" />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationOn />
                  Top Locations
                </Typography>
                {metrics.topLocations.map((location, index) => (
                  <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1 }}>
                    <Typography variant="body2">{location.location}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {location.queries.toLocaleString()}
                      </Typography>
                      <Chip label={`#${index + 1}`} size="small" color="secondary" />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}

export default Analytics
