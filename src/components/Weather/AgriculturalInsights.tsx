import React from 'react'
import {
  CardContent,
  Typography,
  Box,
  Grid,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  CheckCircle as GoodIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Agriculture as CropIcon,
  WaterDrop as WaterIcon,
  Thermostat as TempIcon,
} from '@mui/icons-material'

interface WeatherData {
  temperature: number
  humidity: number
  rainfall: number
  weather: string
}

interface ForecastDay {
  date: string
  temperature: { min: number; max: number }
  rainfall: number
  weather: string
}

interface HistoricalData {
  climateTrend: string
  variability: number
  droughtYears: number[]
  floodYears: number[]
}

interface AgriculturalInsightsProps {
  weather: WeatherData | null
  forecast: ForecastDay[] | null
  historical: HistoricalData | null
}

const AgriculturalInsights: React.FC<AgriculturalInsightsProps> = ({
  weather,
  forecast,
  historical,
}) => {
  if (!weather) {
    return (
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Agricultural insights unavailable
        </Typography>
      </CardContent>
    )
  }

  const generateInsights = () => {
    const insights = []
    const warnings = []
    const recommendations = []

    // Temperature analysis
    if (weather.temperature > 35) {
      warnings.push({
        icon: ErrorIcon,
        text: 'Very high temperatures may stress crops',
        action: 'Ensure adequate irrigation and consider shade for sensitive crops',
      })
    } else if (weather.temperature > 30) {
      warnings.push({
        icon: WarningIcon,
        text: 'High temperatures detected',
        action: 'Monitor crops for heat stress and increase watering',
      })
    } else if (weather.temperature >= 20 && weather.temperature <= 30) {
      insights.push({
        icon: GoodIcon,
        text: 'Optimal temperature range for most crops',
        action: 'Good conditions for planting and growth',
      })
    }

    // Rainfall analysis
    const weeklyRainfall = forecast ? forecast.reduce((sum, day) => sum + day.rainfall, 0) : 0
    
    if (weeklyRainfall > 50) {
      insights.push({
        icon: GoodIcon,
        text: 'Excellent rainfall expected this week',
        action: 'Perfect conditions for planting and crop establishment',
      })
    } else if (weeklyRainfall > 20) {
      insights.push({
        icon: GoodIcon,
        text: 'Good rainfall expected',
        action: 'Suitable for most agricultural activities',
      })
    } else if (weeklyRainfall < 5) {
      warnings.push({
        icon: WarningIcon,
        text: 'Low rainfall expected',
        action: 'Consider irrigation or drought-tolerant varieties',
      })
    }

    // Humidity analysis
    if (weather.humidity > 80) {
      warnings.push({
        icon: WarningIcon,
        text: 'Very high humidity',
        action: 'Monitor for fungal diseases and ensure good air circulation',
      })
    } else if (weather.humidity < 40) {
      warnings.push({
        icon: WarningIcon,
        text: 'Low humidity conditions',
        action: 'Plants may need additional watering',
      })
    }

    // Historical context
    if (historical) {
      if (historical.climateTrend === 'decreasing') {
        recommendations.push({
          icon: WarningIcon,
          text: 'Long-term rainfall is decreasing',
          action: 'Consider drought-resistant varieties and water conservation',
        })
      }
      
      if (historical.variability > 40) {
        recommendations.push({
          icon: WarningIcon,
          text: 'High rainfall variability in this area',
          action: 'Diversify crops to reduce weather-related risks',
        })
      }
    }

    return { insights, warnings, recommendations }
  }

  const { insights, warnings, recommendations } = generateInsights()

  const renderInsightsList = (items: any[], title: string, severity: 'success' | 'warning' | 'info') => {
    if (items.length === 0) return null

    return (
      <Box mb={3}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          {title}
        </Typography>
        <List dense>
          {items.map((item, index) => (
            <ListItem key={index} sx={{ px: 0 }}>
              <ListItemIcon>
                <item.icon color={severity} />
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                secondary={item.action}
                primaryTypographyProps={{ fontWeight: 'medium' }}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    )
  }

  return (
    <CardContent sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        Agricultural Weather Insights
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Analysis of current and forecast conditions for agricultural decision-making
      </Typography>

      {/* Current Conditions Summary */}
      <Box mb={3} p={2} bgcolor="grey.50" borderRadius={2}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Current Conditions Assessment
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Box display="flex" alignItems="center" gap={1}>
              <TempIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Temperature Status
                </Typography>
                <Chip
                  label={weather.temperature > 30 ? 'Hot' : weather.temperature > 20 ? 'Optimal' : 'Cool'}
                  color={weather.temperature > 30 ? 'error' : weather.temperature > 20 ? 'success' : 'info'}
                  size="small"
                />
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Box display="flex" alignItems="center" gap={1}>
              <WaterIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Moisture Status
                </Typography>
                <Chip
                  label={weather.humidity > 70 ? 'High' : weather.humidity > 40 ? 'Good' : 'Low'}
                  color={weather.humidity > 80 ? 'warning' : weather.humidity > 40 ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Box display="flex" alignItems="center" gap={1}>
              <CropIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Growing Conditions
                </Typography>
                <Chip
                  label={
                    weather.temperature >= 20 && weather.temperature <= 30 && weather.humidity > 50
                      ? 'Excellent'
                      : weather.temperature >= 15 && weather.temperature <= 35
                      ? 'Good'
                      : 'Challenging'
                  }
                  color={
                    weather.temperature >= 20 && weather.temperature <= 30 && weather.humidity > 50
                      ? 'success'
                      : weather.temperature >= 15 && weather.temperature <= 35
                      ? 'primary'
                      : 'error'
                  }
                  size="small"
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Insights and Recommendations */}
      {renderInsightsList(insights, 'Favorable Conditions', 'success')}
      {renderInsightsList(warnings, 'Weather Alerts', 'warning')}
      {renderInsightsList(recommendations, 'Long-term Recommendations', 'info')}

      {/* Historical Context */}
      {historical && (
        <Box mt={3} p={2} bgcolor="info.50" borderRadius={2}>
          <Typography variant="h6" gutterBottom fontWeight="bold" color="info.main">
            Historical Context
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" paragraph>
                <strong>Climate Trend:</strong> Rainfall has been {historical.climateTrend} over the past {historical.yearsAnalyzed} years.
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" paragraph>
                <strong>Variability:</strong> {historical.variability.toFixed(1)}% rainfall variability indicates {
                  historical.variability > 30 ? 'unpredictable' : 'relatively stable'
                } weather patterns.
              </Typography>
            </Grid>
            
            {historical.droughtYears.length > 0 && (
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" paragraph>
                  <strong>Recent Droughts:</strong> {historical.droughtYears.slice(-3).join(', ')}
                </Typography>
              </Grid>
            )}
            
            {historical.floodYears.length > 0 && (
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" paragraph>
                  <strong>Recent Floods:</strong> {historical.floodYears.slice(-3).join(', ')}
                </Typography>
              </Grid>
            )}
          </Grid>
        </Box>
      )}
    </CardContent>
  )
}

export default AgriculturalInsights