import React from 'react'
import {
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
} from '@mui/material'
import {
  Thermostat as TempIcon,
  Water as HumidityIcon,
  Air as WindIcon,
  Grain as RainIcon,
  Compress as PressureIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material'

interface WeatherData {
  temperature: number
  feelsLike: number
  humidity: number
  pressure: number
  weather: string
  windSpeed: number
  windDirection: number
  rainfall: number
  visibility: number
  location: string
  country: string
  timestamp: string
}

interface CurrentWeatherCardProps {
  weather: WeatherData | null
}

const CurrentWeatherCard: React.FC<CurrentWeatherCardProps> = ({ weather }) => {
  if (!weather) {
    return (
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Weather data unavailable
        </Typography>
      </CardContent>
    )
  }

  const getTemperatureStatus = (temp: number) => {
    if (temp > 35) return { label: 'Very Hot', color: 'error' }
    if (temp > 30) return { label: 'Hot', color: 'warning' }
    if (temp > 25) return { label: 'Warm', color: 'success' }
    if (temp > 20) return { label: 'Mild', color: 'info' }
    if (temp > 15) return { label: 'Cool', color: 'primary' }
    return { label: 'Cold', color: 'secondary' }
  }

  const getHumidityStatus = (humidity: number) => {
    if (humidity > 80) return { label: 'Very Humid', color: 'info' }
    if (humidity > 60) return { label: 'Humid', color: 'primary' }
    if (humidity > 40) return { label: 'Moderate', color: 'success' }
    return { label: 'Dry', color: 'warning' }
  }

  const getRainfallStatus = (rainfall: number) => {
    if (rainfall > 10) return { label: 'Heavy Rain', color: 'info' }
    if (rainfall > 2) return { label: 'Light Rain', color: 'primary' }
    if (rainfall > 0) return { label: 'Drizzle', color: 'success' }
    return { label: 'No Rain', color: 'default' }
  }

  const tempStatus = getTemperatureStatus(weather.temperature)
  const humidityStatus = getHumidityStatus(weather.humidity)
  const rainfallStatus = getRainfallStatus(weather.rainfall)

  return (
    <CardContent sx={{ p: 3 }}>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          {weather.location}, {weather.country}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Last updated: {new Date(weather.timestamp).toLocaleString()}
        </Typography>
      </Box>

      {/* Main Weather Display */}
      <Box textAlign="center" mb={3}>
        <Typography variant="h2" fontWeight="bold" color="primary.main">
          {weather.temperature}°C
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Feels like {weather.feelsLike}°C
        </Typography>
        <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
          {weather.weather}
        </Typography>
        
        <Box display="flex" justifyContent="center" gap={1} mt={2}>
          <Chip label={tempStatus.label} color={tempStatus.color as any} size="small" />
          <Chip label={humidityStatus.label} color={humidityStatus.color as any} size="small" />
          <Chip label={rainfallStatus.label} color={rainfallStatus.color as any} size="small" />
        </Box>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Detailed Metrics */}
      <Grid container spacing={3}>
        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <HumidityIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Humidity
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {weather.humidity}%
              </Typography>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <WindIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Wind Speed
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {weather.windSpeed} m/s
              </Typography>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <RainIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Rainfall
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {weather.rainfall} mm
              </Typography>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <PressureIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Pressure
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {weather.pressure} hPa
              </Typography>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <VisibilityIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Visibility
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {(weather.visibility / 1000).toFixed(1)} km
              </Typography>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sm={4}>
          <Box display="flex" alignItems="center" gap={1}>
            <TempIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Wind Direction
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {weather.windDirection}°
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </CardContent>
  )
}

export default CurrentWeatherCard