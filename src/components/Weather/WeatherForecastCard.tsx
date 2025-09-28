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
  WbSunny as SunnyIcon,
  Cloud as CloudyIcon,
  Grain as RainIcon,
  Thermostat as TempIcon,
} from '@mui/icons-material'
import { format, parseISO } from 'date-fns'

interface ForecastDay {
  date: string
  temperature: {
    min: number
    max: number
  }
  rainfall: number
  weather: string
  humidity: number
}

interface WeatherForecastCardProps {
  forecast: ForecastDay[] | null
}

const WeatherForecastCard: React.FC<WeatherForecastCardProps> = ({ forecast }) => {
  if (!forecast || forecast.length === 0) {
    return (
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Forecast data unavailable
        </Typography>
      </CardContent>
    )
  }

  const getWeatherIcon = (weather: string) => {
    const desc = weather.toLowerCase()
    if (desc.includes('rain')) return RainIcon
    if (desc.includes('cloud')) return CloudyIcon
    return SunnyIcon
  }

  const getRainfallColor = (rainfall: number) => {
    if (rainfall > 10) return 'info'
    if (rainfall > 2) return 'primary'
    if (rainfall > 0) return 'success'
    return 'default'
  }

  return (
    <CardContent sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        7-Day Weather Forecast
      </Typography>
      
      <Grid container spacing={2}>
        {forecast.map((day, index) => {
          const WeatherIcon = getWeatherIcon(day.weather)
          const isToday = index === 0
          
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={day.date}>
              <Paper
                elevation={isToday ? 4 : 1}
                sx={{
                  p: 2,
                  textAlign: 'center',
                  border: isToday ? 2 : 0,
                  borderColor: isToday ? 'primary.main' : 'transparent',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    elevation: 4,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                {isToday && (
                  <Chip
                    label="Today"
                    color="primary"
                    size="small"
                    sx={{ mb: 1 }}
                  />
                )}
                
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  {format(parseISO(day.date), 'EEE, MMM d')}
                </Typography>
                
                <WeatherIcon 
                  sx={{ 
                    fontSize: 40, 
                    color: 'primary.main',
                    mb: 1,
                  }} 
                />
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {day.weather}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6" fontWeight="bold">
                    {day.temperature.max}°
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {day.temperature.min}°
                  </Typography>
                </Box>
                
                <Box display="flex" justifyContent="center" gap={1} mb={1}>
                  <Chip
                    label={`${day.rainfall}mm`}
                    color={getRainfallColor(day.rainfall) as any}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                <Typography variant="caption" color="text.secondary">
                  Humidity: {day.humidity}%
                </Typography>
              </Paper>
            </Grid>
          )
        })}
      </Grid>
      
      {/* Weekly Summary */}
      <Box mt={3} p={2} bgcolor="grey.50" borderRadius={2}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Weekly Summary
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="bold" color="primary">
                {forecast.reduce((sum, day) => sum + day.rainfall, 0).toFixed(1)}mm
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Rainfall
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {Math.max(...forecast.map(day => day.temperature.max))}°C
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Max Temperature
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="bold" color="info.main">
                {Math.min(...forecast.map(day => day.temperature.min))}°C
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Min Temperature
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="bold" color="success.main">
                {forecast.filter(day => day.rainfall > 0).length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rainy Days
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </CardContent>
  )
}

export default WeatherForecastCard