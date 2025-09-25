import React, { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Button,
  Alert,
  Skeleton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import {
  WbSunny as CurrentIcon,
  Grain as RainyIcon,
  WbSunnyOutlined as DryIcon,
  CompareArrows as CompareIcon,
  LocationOn as LocationIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { RootState } from '../../store/store'
import { setSelectedSeason, setCropRecommendations } from '../../store/slices/cropSlice'
import { useCropRecommendations } from '../../hooks/useCropRecommendations'
import CropRecommendationCard from '../../components/Crops/CropRecommendationCard'
import LocationPicker from '../../components/Location/LocationPicker'
import SeasonalComparison from '../../components/Crops/SeasonalComparison'

const CropRecommendations: React.FC = () => {
  const dispatch = useDispatch()
  const { location } = useSelector((state: RootState) => state.user)
  const { selectedSeason, recommendations, loading, error } = useSelector((state: RootState) => state.crop)
  
  const [currentLocation, setCurrentLocation] = useState({
    lat: location?.lat || -13.9833,
    lon: location?.lon || 33.7833,
  })

  const { data: cropData, isLoading, error: apiError, refetch } = useCropRecommendations(
    currentLocation.lat,
    currentLocation.lon,
    selectedSeason
  )

  useEffect(() => {
    if (cropData?.recommendations) {
      dispatch(setCropRecommendations(cropData.recommendations))
    }
  }, [cropData, dispatch])

  const handleSeasonChange = (_event: React.SyntheticEvent, newValue: number) => {
    const seasons = ['current', 'rainy', 'dry', 'all'] as const
    dispatch(setSelectedSeason(seasons[newValue]))
  }

  const handleLocationChange = (lat: number, lon: number) => {
    setCurrentLocation({ lat, lon })
  }

  const getSeasonDescription = (season: string) => {
    switch (season) {
      case 'rainy':
        return 'November - April: Main growing season with regular rainfall'
      case 'dry':
        return 'May - October: Dry season with minimal rainfall'
      case 'all':
        return 'Year-round comparison across all seasons'
      default:
        return 'Current conditions and immediate recommendations'
    }
  }

  const seasonTabs = [
    { value: 'current', label: 'Current', icon: CurrentIcon },
    { value: 'rainy', label: 'Rainy Season', icon: RainyIcon },
    { value: 'dry', label: 'Dry Season', icon: DryIcon },
    { value: 'all', label: 'All Seasons', icon: CompareIcon },
  ]

  const currentTabIndex = seasonTabs.findIndex(tab => tab.value === selectedSeason)

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
        Crop Recommendations
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Get personalized crop recommendations based on your location and seasonal conditions
      </Typography>

      {/* Location Picker */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <LocationIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Location
            </Typography>
          </Box>
          
          <LocationPicker
            lat={currentLocation.lat}
            lon={currentLocation.lon}
            onChange={handleLocationChange}
          />
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Current: {currentLocation.lat.toFixed(4)}, {currentLocation.lon.toFixed(4)}
          </Typography>
        </CardContent>
      </Card>

      {/* Season Selection */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={currentTabIndex}
          onChange={handleSeasonChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 72,
            },
          }}
        >
          {seasonTabs.map((tab, index) => {
            const Icon = tab.icon
            return (
              <Tab
                key={tab.value}
                icon={<Icon />}
                label={tab.label}
                iconPosition="start"
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.50',
                  },
                }}
              />
            )
          })}
        </Tabs>
        
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            {getSeasonDescription(selectedSeason)}
          </Typography>
        </CardContent>
      </Card>

      {/* Error Handling */}
      {(error || apiError) && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => refetch()}>
              <RefreshIcon fontSize="small" />
              Retry
            </Button>
          }
        >
          Unable to fetch crop recommendations. Please check your internet connection.
        </Alert>
      )}

      {/* Loading State */}
      {(loading || isLoading) && (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Recommendations Display */}
      {!loading && !isLoading && recommendations.length > 0 && (
        <>
          {selectedSeason === 'all' ? (
            <SeasonalComparison data={cropData} />
          ) : (
            <>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" fontWeight="bold">
                  Recommended Crops
                </Typography>
                <Chip
                  label={`${recommendations.length} recommendations`}
                  color="primary"
                  variant="outlined"
                />
              </Box>
              
              <Grid container spacing={3}>
                {recommendations.map((crop, index) => (
                  <Grid item xs={12} sm={6} md={4} key={crop.cropId || index}>
                    <CropRecommendationCard
                      crop={crop}
                      onClick={() => {
                        // Navigate to variety details
                        window.location.href = `/varieties?crop=${crop.cropName}&lat=${currentLocation.lat}&lon=${currentLocation.lon}`
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </>
      )}

      {/* Empty State */}
      {!loading && !isLoading && recommendations.length === 0 && !error && !apiError && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <CropIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              No recommendations available
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              We couldn't generate crop recommendations for your current location and season.
              This might be due to limited data or extreme weather conditions.
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => refetch()}
              startIcon={<RefreshIcon />}
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default CropRecommendations