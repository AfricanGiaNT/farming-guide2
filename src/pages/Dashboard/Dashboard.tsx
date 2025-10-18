import React, { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  WbSunny as WeatherIcon,
  Agriculture as CropIcon,
  Agriculture as VarietyIcon,
  TrendingUp as TrendIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { RootState } from '../../store/store'
import { useWeatherData } from '../../hooks/useWeatherData'
import { useCropRecommendations } from '../../hooks/useCropRecommendations'
import WeatherWidget from '../../components/Weather/WeatherWidget'
import CropRecommendationCard from '../../components/Crops/CropRecommendationCard'
import QuickActionCard from '../../components/Dashboard/QuickActionCard'
import FarmingTipCard from '../../components/Dashboard/FarmingTipCard'

const Dashboard: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const dispatch = useDispatch()
  
  const { location } = useSelector((state: RootState) => state.user)
  const { current: currentWeather } = useSelector((state: RootState) => state.weather)
  const { recommendations } = useSelector((state: RootState) => state.crop)

  // Fetch weather data for user's location
  const { data: weatherData, isLoading: weatherLoading } = useWeatherData(
    location?.lat || -13.9833,
    location?.lon || 33.7833
  )

  // Fetch crop recommendations
  const { data: cropData, isLoading: cropLoading } = useCropRecommendations(
    location?.lat || -13.9833,
    location?.lon || 33.7833,
    'current'
  )

  const quickActions = [
    {
      title: 'Get Crop Recommendations',
      description: 'Find the best crops for your location',
      icon: CropIcon,
      color: 'primary',
      path: '/crops',
    },
    {
      title: 'Check Weather',
      description: 'Current conditions and 7-day forecast',
      icon: WeatherIcon,
      color: 'secondary',
      path: '/weather',
    },
    {
      title: 'Search Varieties',
      description: 'Find specific crop varieties',
      icon: VarietyIcon,
      color: 'success',
      path: '/varieties',
    },
    {
      title: 'View Planting Calendar',
      description: 'Optimal planting times',
      icon: TrendIcon,
      color: 'warning',
      path: '/farm',
    },
  ]

  const farmingTips = [
    {
      title: 'Rainy Season Preparation',
      content: 'November is the optimal time to prepare your fields for the main planting season.',
      category: 'Seasonal',
    },
    {
      title: 'Soil Testing',
      content: 'Test your soil pH before planting. Most crops prefer pH 6.0-7.0.',
      category: 'Soil Health',
    },
    {
      title: 'Seed Storage',
      content: 'Store seeds in cool, dry places to maintain viability.',
      category: 'Post-Harvest',
    },
  ]

  return (
    <Box>
      {/* Welcome Section */}
      <Box mb={3}>
        <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
          Welcome to Mlangizi wa Ulimi
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Your intelligent agricultural advisor for better farming decisions
        </Typography>
        
        {location && (
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <LocationIcon color="action" fontSize="small" />
            <Typography variant="body2" color="text.secondary">
              {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
              {location.accuracy && ` (±${Math.round(location.accuracy)}m)`}
            </Typography>
          </Box>
        )}
      </Box>

      <Grid container spacing={3}>
        {/* Weather Widget */}
        <Grid item xs={12} md={8}>
          <WeatherWidget 
            weather={currentWeather}
            loading={weatherLoading}
            onViewDetails={() => navigate('/weather')}
          />
        </Grid>

        {/* Current Season Indicator */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Season
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Chip 
                  label="Rainy Season" 
                  color="primary" 
                  variant="filled"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                November - April: Main planting and growing season
              </Typography>
              <Button 
                variant="outlined" 
                size="small" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/crops')}
              >
                View Seasonal Crops
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom fontWeight="bold">
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <QuickActionCard
                  title={action.title}
                  description={action.description}
                  icon={action.icon}
                  color={action.color}
                  onClick={() => navigate(action.path)}
                />
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Recent Recommendations */}
        <Grid item xs={12} md={8}>
          <Typography variant="h5" gutterBottom fontWeight="bold">
            Recent Recommendations
          </Typography>
          {cropLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <Typography>Loading recommendations...</Typography>
            </Box>
          ) : recommendations.length > 0 ? (
            <Grid container spacing={2}>
              {recommendations.slice(0, 3).map((crop, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <CropRecommendationCard
                    crop={crop}
                    onClick={() => navigate(`/varieties?crop=${crop.cropName}`)}
                  />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <CropIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No recommendations yet
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Get personalized crop recommendations based on your location and current weather conditions.
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => navigate('/crops')}
                >
                  Get Recommendations
                </Button>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Farming Tips */}
        <Grid item xs={12} md={4}>
          <Typography variant="h5" gutterBottom fontWeight="bold">
            Farming Tips
          </Typography>
          <Box display="flex" flexDirection="column" gap={2}>
            {farmingTips.map((tip, index) => (
              <FarmingTipCard
                key={index}
                title={tip.title}
                content={tip.content}
                category={tip.category}
              />
            ))}
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard