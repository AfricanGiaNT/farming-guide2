import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Button,
  Skeleton,
} from '@mui/material'
import {
  WbSunny as SunnyIcon,
  Cloud as CloudyIcon,
  Grain as RainIcon,
  Thermostat as TempIcon,
  Water as HumidityIcon,
  Air as WindIcon,
} from '@mui/icons-material'

interface WeatherData {
  temperature: number
  humidity: number
  weather: string
  windSpeed: number
  rainfall: number
  location: string
}

interface WeatherWidgetProps {
  weather: WeatherData | null
  loading: boolean
  onViewDetails: () => void
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({
  weather,
  loading,
  onViewDetails,
}) => {
  const getWeatherIcon = (weatherDesc: string) => {
    const desc = weatherDesc?.toLowerCase() || ''
    if (desc.includes('rain')) return RainIcon
    if (desc.includes('cloud')) return CloudyIcon
    return SunnyIcon
  }

  const getTemperatureColor = (temp: number) => {
    if (temp > 30) return 'error.main'
    if (temp > 25) return 'warning.main'
    if (temp > 20) return 'success.main'
    return 'info.main'
  }

  const getAgriculturalContext = (weather: WeatherData) => {
    const { temperature, humidity, rainfall } = weather
    
    if (rainfall > 10) {
      return { text: 'Excellent for crop growth', color: 'success' }
    } else if (temperature > 30 && humidity < 40) {
      return { text: 'Monitor for drought stress', color: 'warning' }
    } else if (humidity > 80) {
      return { text: 'Watch for fungal diseases', color: 'warning' }
    } else {
      return { text: 'Good growing conditions', color: 'success' }
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="60%" height={32} />
          <Skeleton variant="rectangular" width="100%" height={120} sx={{ my: 2 }} />
          <Skeleton variant="text" width="40%" height={24} />
        </CardContent>
      </Card>
    )
  }

  if (!weather) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CloudyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Weather data unavailable
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Unable to fetch weather information at the moment
          </Typography>
        </CardContent>
      </Card>
    )
  }

  const WeatherIconComponent = getWeatherIcon(weather.weather)
  const agriculturalContext = getAgriculturalContext(weather)

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h5" gutterBottom fontWeight="bold">
              Current Weather
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {weather.location}
            </Typography>
          </Box>
          <WeatherIconComponent 
            sx={{ 
              fontSize: 40, 
              color: getTemperatureColor(weather.temperature) 
            }} 
          />
        </Box>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6} sm={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <TempIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {weather.temperature}°C
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Temperature
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <HumidityIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {weather.humidity}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Humidity
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <WindIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {weather.windSpeed} m/s
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Wind Speed
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <RainIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {weather.rainfall} mm
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Rainfall
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Chip
            label={agriculturalContext.text}
            color={agriculturalContext.color as any}
            variant="outlined"
            size="small"
          />
          <Button variant="outlined" size="small" onClick={onViewDetails}>
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default WeatherWidget