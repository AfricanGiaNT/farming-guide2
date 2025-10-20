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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Button,
  useMediaQuery,
  useTheme,
  Chip,
  Checkbox,
  FormGroup,
  FormControlLabel,
  Stack,
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
import MonthlyRainfallTable from '../../components/Weather/MonthlyRainfallTable'
import SimplifiedLocationInput from '../../components/Weather/SimplifiedLocationInput'
import AgriculturalInsights from '../../components/Weather/AgriculturalInsights'
import AgriculturalImplications from '../../components/Weather/AgriculturalImplications'
import { weatherAPI } from '../../services/api'

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
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [tabValue, setTabValue] = useState(0)
  const [selectedYears, setSelectedYears] = useState<number[]>([])
  const [customLocation, setCustomLocation] = useState<{lat: number, lon: number} | null>(null)
  const [shouldFetchHistorical, setShouldFetchHistorical] = useState(false)
  const [agriculturalRecommendations, setAgriculturalRecommendations] = useState<any>(null)
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)
  const { location } = useSelector((state: RootState) => state.user)
  
  const lat = customLocation?.lat || location?.lat || -13.9833
  const lon = customLocation?.lon || location?.lon || 33.7833

  const { data: currentWeather, isLoading: currentLoading, error: currentError } = useWeatherData(lat, lon)
  const { data: forecast, isLoading: forecastLoading } = useWeatherForecast(lat, lon)
  const { data: historical, isLoading: historicalLoading } = useHistoricalWeather(lat, lon, selectedYears.length ? selectedYears : 1, shouldFetchHistorical)

  // Debug logging for historical data
  console.log('🌤️ Weather page - Historical data:', historical)
  console.log('🌤️ Weather page - Historical loading:', historicalLoading)
  console.log('🌤️ Weather page - Historical data type:', typeof historical)
  console.log('🌤️ Weather page - Historical keys:', historical ? Object.keys(historical) : 'null/undefined')

  // Fetch agricultural recommendations when historical data is available
  React.useEffect(() => {
    const fetchAgriculturalRecommendations = async () => {
      if (historical && selectedYears.length > 0 && !historicalLoading) {
        setLoadingRecommendations(true)
        try {
          const years = selectedYears.length
          const response = await weatherAPI.getAgriculturalRecommendations(lat, lon, years)
          setAgriculturalRecommendations(response.agricultural_implications)
          console.log('🌾 Agricultural recommendations loaded:', response)
        } catch (error) {
          console.error('Error fetching agricultural recommendations:', error)
          setAgriculturalRecommendations(null)
        } finally {
          setLoadingRecommendations(false)
        }
      }
    }

    fetchAgriculturalRecommendations()
  }, [historical, historicalLoading, selectedYears, lat, lon])

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleYearsMultiselect = (years: number[]) => {
    setSelectedYears(years)
    setShouldFetchHistorical(false)
  }

  const handleLocationChange = (lat: number, lon: number) => {
    setCustomLocation({ lat, lon })
    setShouldFetchHistorical(false) // Reset fetch trigger when location changes
  }

  return (
    <Box>
      <Typography variant={isMobile ? "h5" : "h4"} gutterBottom fontWeight="bold" color="primary">
        Weather & Climate
      </Typography>
      
      <Typography variant={isMobile ? "body2" : "body1"} color="text.secondary" paragraph>
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
              minHeight: isMobile ? 40 : 64,
              fontSize: isMobile ? '0.7rem' : '0.875rem',
              padding: isMobile ? '6px 4px' : '12px 16px',
              minWidth: isMobile ? '60px' : 'auto',
            },
            '& .MuiTab-iconWrapper': {
              fontSize: isMobile ? '16px' : '20px',
            },
          }}
        >
          <Tab
            icon={<CurrentIcon />}
            label={isMobile ? "Current" : "Current"}
            iconPosition="top"
          />
          <Tab
            icon={<ForecastIcon />}
            label={isMobile ? "7-Day" : "7-Day Forecast"}
            iconPosition="top"
          />
          <Tab
            icon={<HistoricalIcon />}
            label={isMobile ? "Historical" : "Historical"}
            iconPosition="top"
          />
          <Tab
            icon={<AgricultureIcon />}
            label={isMobile ? "Agriculture" : "Agricultural Insights"}
            iconPosition="top"
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
          {/* Simplified Location Input */}
          <Box mb={isMobile ? 2 : 3}>
            <SimplifiedLocationInput
              onLocationChange={handleLocationChange}
              currentLocation={customLocation}
            />
          </Box>

          {/* Analysis Period Selection */}
          <Box mb={isMobile ? 2 : 3}>
            <Paper sx={{ p: isMobile ? 1.5 : 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold">
                  Select Years
                </Typography>
                {selectedYears.length > 0 && (
                  <Chip 
                    label={`${selectedYears.length} selected`} 
                    color="primary" 
                    size="small"
                  />
                )}
              </Box>

              {/* Quick Select Buttons */}
              <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" useFlexGap>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    const currentYear = new Date().getFullYear()
                    handleYearsMultiselect([currentYear, currentYear - 1, currentYear - 2])
                  }}
                >
                  Last 3 Years
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    const currentYear = new Date().getFullYear()
                    handleYearsMultiselect(Array.from({ length: 5 }, (_, i) => currentYear - i))
                  }}
                >
                  Last 5 Years
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleYearsMultiselect([])}
                  disabled={selectedYears.length === 0}
                >
                  Clear All
                </Button>
              </Stack>

              {/* Year Checkboxes Grid */}
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(5, 1fr)', 
                gap: 1,
                mb: 2 
              }}>
                {Array.from({ length: 10 }).map((_, idx) => {
                  const year = new Date().getFullYear() - idx
                  const isSelected = selectedYears.includes(year)
                  return (
                    <Paper
                      key={year}
                      elevation={isSelected ? 3 : 1}
                      sx={{
                        p: 1,
                        cursor: 'pointer',
                        border: '2px solid',
                        borderColor: isSelected ? 'primary.main' : 'divider',
                        bgcolor: isSelected ? 'primary.light' : 'background.paper',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          borderColor: 'primary.main',
                          transform: 'translateY(-2px)',
                        },
                      }}
                      onClick={() => {
                        if (isSelected) {
                          handleYearsMultiselect(selectedYears.filter(y => y !== year))
                        } else {
                          handleYearsMultiselect([...selectedYears, year].sort((a, b) => b - a))
                        }
                      }}
                    >
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <Checkbox
                          checked={isSelected}
                          size="small"
                          sx={{ p: 0, mr: 0.5 }}
                        />
                        <Typography 
                          variant={isMobile ? "body2" : "body1"} 
                          fontWeight={isSelected ? 'bold' : 'normal'}
                          color={isSelected ? 'primary.main' : 'text.primary'}
                        >
                          {year}
                        </Typography>
                      </Box>
                    </Paper>
                  )
                })}
              </Box>

              {/* Selected Years Display */}
              {selectedYears.length > 0 && (
                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Selected Years:
                  </Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                    {selectedYears.sort((a, b) => b - a).map((year) => (
                      <Chip
                        key={year}
                        label={year}
                        size="small"
                        onDelete={() => handleYearsMultiselect(selectedYears.filter(y => y !== year))}
                        color="primary"
                      />
                    ))}
                  </Box>
                </Box>
              )}
              
              {/* Get Rainfall Data Button */}
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => setShouldFetchHistorical(true)}
                disabled={historicalLoading || selectedYears.length === 0}
                sx={{ 
                  minHeight: isMobile ? 40 : 48,
                  fontSize: isMobile ? '0.875rem' : '1rem'
                }}
              >
                {historicalLoading 
                  ? 'Getting Rainfall Data...' 
                  : selectedYears.length === 0 
                    ? 'Select Years to Continue' 
                    : `Get Rainfall Data (${selectedYears.length} Year${selectedYears.length > 1 ? 's' : ''})`}
              </Button>
            </Paper>
          </Box>

          {/* Historical Weather Data Display */}
          {historicalLoading ? (
            <Box p={3}>
              <Skeleton variant="rectangular" height={300} />
            </Box>
          ) : (
            <Box>
              {/* Monthly Rainfall Table - Primary Display */}
              <MonthlyRainfallTable 
                historical={historical} 
                loading={historicalLoading}
              />
              
              {/* Historical Chart - Secondary Display */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Visual Trends
                </Typography>
                <HistoricalWeatherChart historical={historical} />
              </Box>

              {/* Agricultural Implications - New Section */}
              {loadingRecommendations ? (
                <Box sx={{ mt: 3 }}>
                  <Skeleton variant="rectangular" height={400} />
                </Box>
              ) : agriculturalRecommendations ? (
                <Box sx={{ mt: 3 }}>
                  <AgriculturalImplications data={agriculturalRecommendations} />
                </Box>
              ) : null}
            </Box>
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