import React, { useState } from 'react'
import { useSelector } from 'react-redux'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  Alert,
  Skeleton,
} from '@mui/material'
import {
  WbSunny as CurrentIcon,
  Schedule as ForecastIcon,
  History as HistoricalIcon,
  Agriculture as AgricultureIcon,
} from '@mui/icons-material'
import { RootState } from '../../store/store'
import { useWeatherData, useWeatherForecast, useHistoricalWeather } from '../../hooks/useWeatherData'
import CurrentWeatherCard from '../../components/Weather/CurrentWeatherCard'
import WeatherForecastCard from '../../components/Weather/WeatherForecastCard'
import HistoricalWeatherChart from '../../components/Weather/HistoricalWeatherChart'
import AgriculturalInsights from '../../components/Weather/AgriculturalInsights'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index} style={{ width: '100%' }}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

const Weather: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const { location } = useSelector((state: RootState) => state.user)
  
  const lat = location?.lat || -13.9833
  const lon = location?.lon || 33.7833

  const { data: currentWeather, isLoading: currentLoading, error: currentError } = useWeatherData(lat, lon)
  const { data: forecast, isLoading: forecastLoading } = useWeatherForecast(lat, lon)
  const { data: historical, isLoading: historicalLoading } = useHistoricalWeather(lat, lon, 5)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
        Weather & Climate
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Comprehensive weather information for agricultural decision-making
      </Typography>

      {currentError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Unable to fetch weather data. Please check your internet connection and try again.
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 64,
            },
          }}
        >
          <Tab
            icon={<CurrentIcon />}
            label="Current"
            iconPosition="start"
          />
          <Tab
            icon={<ForecastIcon />}
            label="7-Day Forecast"
            iconPosition="start"
          />
          <Tab
            icon={<HistoricalIcon />}
            label="Historical"
            iconPosition="start"
          />
          <Tab
            icon={<AgricultureIcon />}
            label="Agricultural Insights"
            iconPosition="start"
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {currentLoading ? (
            <Box p={3}>
              <Skeleton variant="rectangular" height={200} />
            </Box>
          ) : (
            <CurrentWeatherCard weather={currentWeather} />
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {forecastLoading ? (
            <Box p={3}>
              <Grid container spacing={2}>
                {[...Array(7)].map((_, index) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                    <Skeleton variant="rectangular" height={150} />
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : (
            <WeatherForecastCard forecast={forecast} />
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {historicalLoading ? (
            <Box p={3}>
              <Skeleton variant="rectangular" height={300} />
            </Box>
          ) : (
            <HistoricalWeatherChart historical={historical} />
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <AgriculturalInsights 
            weather={currentWeather}
            forecast={forecast}
            historical={historical}
          />
        </TabPanel>
      </Card>
    </Box>
  )
}

export default Weather