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
  List,
  ListItem,
  ListItemText,
  TextField,
  Paper,
  Divider,
} from '@mui/material'
import {
  WbSunny as CurrentIcon,
  Grain as RainyIcon,
  WbSunnyOutlined as DryIcon,
  CompareArrows as CompareIcon,
  LocationOn as LocationIcon,
  Refresh as RefreshIcon,
  NavigateBefore as PrevIcon,
  NavigateNext as NextIcon,
  Search as SearchIcon,
  MyLocation as MyLocationIcon,
  Clear as ClearIcon,
  Agriculture as CropIcon,
} from '@mui/icons-material'
import { RootState } from '../../store/store'
import { setSelectedSeason, setCropRecommendations } from '../../store/slices/cropSlice'
import { useCropRecommendations } from '../../hooks/useCropRecommendations'
import CropRecommendationCard from '../../components/Crops/CropRecommendationCard'
import LocationPicker from '../../components/Location/LocationPicker'
import SeasonalComparison from '../../components/Crops/SeasonalComparison'
import { cropDataProcessor } from '../../services/cropDataProcessor'
import CropDataErrorBoundary from '../../components/ErrorBoundary/CropDataErrorBoundary'
import SectionErrorBoundary from '../../components/ErrorBoundary/SectionErrorBoundary'

const CropRecommendations: React.FC = () => {
  const dispatch = useDispatch()
  const { location } = useSelector((state: RootState) => state.user)
  const { selectedSeason, recommendations, loading, error } = useSelector((state: RootState) => state.crop)
  
  const [currentLocation, setCurrentLocation] = useState({
    lat: location?.lat || -13.9833,
    lon: location?.lon || 33.7833,
  })
  
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 6,
    total: 0
  })

  const [inputCoordinates, setInputCoordinates] = useState('')
  const [inputCropName, setInputCropName] = useState('')
  const [showInputForm, setShowInputForm] = useState(false)
  const [processedData, setProcessedData] = useState<any>(null)
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'enhanced' | 'fallback'>('idle')

  const { data: cropData, isLoading, error: apiError, refetch } = useCropRecommendations(
    currentLocation.lat,
    currentLocation.lon,
    selectedSeason
  )

  useEffect(() => {
    if (cropData?.recommendations) {
      // Use comprehensive data processing pipeline (Phase 2)
      const processData = async () => {
        setProcessingStatus('processing')
        try {
          const location = `${currentLocation.lat},${currentLocation.lon}`
          const weatherData = {
            temperature: cropData.environmental_summary?.current_temperature || 25,
            rainfall: cropData.environmental_summary?.total_7day_rainfall || 0,
            humidity: cropData.environmental_summary?.humidity || 50
          }

          const processed = await cropDataProcessor.processComprehensiveData(
            cropData,
            location,
            selectedSeason,
            weatherData
          )

          setProcessedData(processed)
          dispatch(setCropRecommendations(processed.recommendations))
          setPagination(prev => ({
            ...prev,
            total: processed.recommendations.length,
            offset: 0 // Reset to first page when data changes
          }))

          // Set processing status based on metadata
          if (processed.processing_metadata?.ai_enhanced) {
            setProcessingStatus('enhanced')
          } else {
            setProcessingStatus('fallback')
          }

          // Log processing metadata for monitoring
          if (processed.processing_metadata) {
            console.log('Data processing completed:', processed.processing_metadata)
          }
        } catch (error) {
          console.error('Data processing failed:', error)
          setProcessingStatus('fallback')
          // Fallback to original data
          setProcessedData(cropData)
          dispatch(setCropRecommendations(cropData.recommendations))
          setPagination(prev => ({
            ...prev,
            total: cropData.recommendations.length,
            offset: 0
          }))
        }
      }

      processData()
    }
  }, [cropData, dispatch, currentLocation, selectedSeason])

  const handleSeasonChange = (_event: React.SyntheticEvent, newValue: number) => {
    const seasons = ['current', 'rainy', 'dry', 'all'] as const
    dispatch(setSelectedSeason(seasons[newValue]))
  }

  const handleLocationChange = (lat: number, lon: number) => {
    setCurrentLocation({ lat, lon })
  }

  const handlePageChange = (newOffset: number) => {
    setPagination(prev => ({
      ...prev,
      offset: newOffset
    }))
  }

  const handleNextPage = () => {
    const nextOffset = pagination.offset + pagination.limit
    if (nextOffset < pagination.total) {
      handlePageChange(nextOffset)
    }
  }

  const handlePrevPage = () => {
    const prevOffset = Math.max(0, pagination.offset - pagination.limit)
    handlePageChange(prevOffset)
  }

  const handleCoordinateSubmit = () => {
    if (inputCoordinates.trim()) {
      // Parse coordinates (format: "lat, lon" or "lat,lon")
      const coords = inputCoordinates.split(',').map(c => c.trim())
      if (coords.length === 2) {
        const lat = parseFloat(coords[0])
        const lon = parseFloat(coords[1])
        if (!isNaN(lat) && !isNaN(lon)) {
          setCurrentLocation({ lat, lon })
          setInputCoordinates('')
          setShowInputForm(false)
        } else {
          alert('Please enter valid coordinates (e.g., -13.9833, 33.7833)')
        }
      } else {
        alert('Please enter coordinates in the format: latitude, longitude')
      }
    }
  }

  const handleCropSearch = () => {
    if (inputCropName.trim()) {
      // Filter recommendations by crop name
      const filteredCrops = recommendations.filter(crop => 
        crop.crop_name.toLowerCase().includes(inputCropName.toLowerCase())
      )
      if (filteredCrops.length > 0) {
        dispatch(setCropRecommendations(filteredCrops))
        setPagination(prev => ({
          ...prev,
          total: filteredCrops.length,
          offset: 0
        }))
      } else {
        alert(`No crops found matching "${inputCropName}". Try a different search term.`)
      }
      setInputCropName('')
    }
  }

  const handleResetFilters = () => {
    if (processedData?.recommendations) {
      dispatch(setCropRecommendations(processedData.recommendations))
      setPagination(prev => ({
        ...prev,
        total: processedData.recommendations.length,
        offset: 0
      }))
    }
    setInputCropName('')
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
    <CropDataErrorBoundary 
      fallbackTitle="Crop Recommendations Error"
      fallbackMessage="There was an error loading crop recommendations. This might be due to server issues or malformed data."
      onRetry={() => refetch()}
    >
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
          Crop Recommendations
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          Get personalized crop recommendations based on your location and seasonal conditions
        </Typography>
        
        {/* Processing Status Indicator */}
        {processingStatus !== 'idle' && (
          <Box sx={{ mb: 2 }}>
            {processingStatus === 'processing' && (
              <Alert severity="info" sx={{ display: 'flex', alignItems: 'center' }}>
                <LinearProgress sx={{ width: 20, mr: 1 }} />
                Processing data with AI enhancement...
              </Alert>
            )}
            {processingStatus === 'enhanced' && (
              <Alert severity="success" sx={{ display: 'flex', alignItems: 'center' }}>
                ✨ Data enhanced with AI summarization
              </Alert>
            )}
            {processingStatus === 'fallback' && (
              <Alert severity="warning" sx={{ display: 'flex', alignItems: 'center' }}>
                ⚠️ Using fallback processing (AI enhancement unavailable)
              </Alert>
            )}
          </Box>
        )}

      {/* Input Form for Coordinates and Crop Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom color="error">
            🔍 Search & Input Options
          </Typography>
          
          <Grid container spacing={3}>
            {/* Coordinate Input */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                📍 Enter Coordinates
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Enter latitude and longitude coordinates (e.g., -13.9833, 33.7833)
              </Typography>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  placeholder="e.g., -13.9833, 33.7833"
                  value={inputCoordinates}
                  onChange={(e) => setInputCoordinates(e.target.value)}
                  size="small"
                  variant="outlined"
                />
                <Button
                  variant="contained"
                  onClick={handleCoordinateSubmit}
                  disabled={!inputCoordinates.trim()}
                  startIcon={<MyLocationIcon />}
                >
                  Set Location
                </Button>
              </Box>
            </Grid>

            {/* Crop Search */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                🌱 Search Crops
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Search for specific crops in the current recommendations
              </Typography>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  placeholder="e.g., maize, groundnut, beans"
                  value={inputCropName}
                  onChange={(e) => setInputCropName(e.target.value)}
                  size="small"
                  variant="outlined"
                />
                <Button
                  variant="outlined"
                  onClick={handleCropSearch}
                  disabled={!inputCropName.trim()}
                  startIcon={<SearchIcon />}
                >
                  Search
                </Button>
              </Box>
            </Grid>
          </Grid>

          {/* Action Buttons */}
          <Box display="flex" gap={2} mt={2} flexWrap="wrap">
            <Button
              variant="outlined"
              onClick={() => setShowInputForm(!showInputForm)}
              startIcon={<LocationIcon />}
            >
              {showInputForm ? 'Hide' : 'Show'} Location Picker
            </Button>
            
            <Button
              variant="outlined"
              onClick={handleResetFilters}
              startIcon={<ClearIcon />}
            >
              Reset Filters
            </Button>
            
            <Button
              variant="contained"
              onClick={() => refetch()}
              startIcon={<RefreshIcon />}
            >
              Refresh Data
            </Button>
          </Box>

          {/* Collapsible Location Picker */}
          {showInputForm && (
            <Box mt={3}>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Interactive Location Picker
              </Typography>
              <LocationPicker
                lat={currentLocation.lat}
                lon={currentLocation.lon}
                onChange={handleLocationChange}
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Risk Assessment - Positioned immediately after search form */}
      {processedData?.risk_assessment && (
        <SectionErrorBoundary sectionName="Risk Assessment">
          <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Risk Assessment
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Typography variant="body2" fontWeight="bold">
                Overall Risk Level:
              </Typography>
              <Chip
                label={processedData.risk_assessment.overall_risk_level}
                color={
                  processedData.risk_assessment.overall_risk_level === 'low' ? 'success' :
                  processedData.risk_assessment.overall_risk_level === 'moderate' ? 'warning' : 'error'
                }
                size="small"
              />
            </Box>
            
            {processedData.risk_assessment.weather_risks && processedData.risk_assessment.weather_risks.length > 0 && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Weather Risks ({processedData.risk_assessment.weather_risks.length}):
                </Typography>
                <List dense>
                  {processedData.risk_assessment.weather_risks.map((risk: any, index: number) => (
                    <ListItem key={risk.id || index} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${risk.text}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondary={risk.category ? `Category: ${risk.category}` : undefined}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {processedData.risk_assessment.pest_risks && processedData.risk_assessment.pest_risks.length > 0 && (
              <Box>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Pest Risks:
                </Typography>
                <List dense>
                  {processedData.risk_assessment.pest_risks.map((risk, index) => (
                    <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${risk}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
          </Card>
        </SectionErrorBoundary>
      )}

      {/* Current Location Display */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <LocationIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Current Location
            </Typography>
          </Box>
          
          <Typography variant="body1" fontWeight="bold" color="primary.main">
            {currentLocation.lat.toFixed(4)}, {currentLocation.lon.toFixed(4)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Use the input form above to change location or search for specific crops
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

      {/* Environmental Summary */}
      {processedData?.environmental_summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Environmental Conditions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {processedData.environmental_summary.total_7day_rainfall}mm
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    7-Day Rainfall
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {processedData.environmental_summary.current_temperature}°C
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Temperature
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {processedData.environmental_summary.humidity}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Humidity
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {processedData.historical_data || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Years Analyzed
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Planting Advice */}
      {processedData?.planting_advice && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Planting Advice
            </Typography>
            <Grid container spacing={2}>
              {processedData.planting_advice.optimal_planting_window && (
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    Optimal Planting Window:
                  </Typography>
                  <Typography variant="body2">
                    {processedData.planting_advice.optimal_planting_window}
                  </Typography>
                </Grid>
              )}
              {processedData.planting_advice.soil_preparation && (
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    Soil Preparation:
                  </Typography>
                  <Typography variant="body2">
                    {processedData.planting_advice.soil_preparation}
                  </Typography>
                </Grid>
              )}
              {processedData.planting_advice.seed_requirements && (
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    Seed Requirements:
                  </Typography>
                  <Typography variant="body2">
                    {processedData.planting_advice.seed_requirements}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Management Tips */}
      {processedData?.management_tips && (
        processedData.management_tips.planting.length > 0 || 
        processedData.management_tips.maintenance.length > 0 || 
        processedData.management_tips.harvest.length > 0 || 
        processedData.management_tips.general.length > 0
      ) && (
        <SectionErrorBoundary sectionName="Management Tips">
          <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Management Tips
            </Typography>
            
            {processedData.management_tips.planting.length > 0 && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  🌱 Planting Phase:
                </Typography>
                <List dense>
                  {processedData.management_tips.planting.map((tip, index) => (
                    <ListItem key={`planting_${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${tip}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {processedData.management_tips.maintenance.length > 0 && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  🔧 Maintenance Phase:
                </Typography>
                <List dense>
                  {processedData.management_tips.maintenance.map((tip, index) => (
                    <ListItem key={`maintenance_${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${tip}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {processedData.management_tips.harvest.length > 0 && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  🌾 Harvest Phase:
                </Typography>
                <List dense>
                  {processedData.management_tips.harvest.map((tip, index) => (
                    <ListItem key={`harvest_${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${tip}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {processedData.management_tips.general.length > 0 && (
              <Box>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  📋 General Tips:
                </Typography>
                <List dense>
                  {processedData.management_tips.general.map((tip, index) => (
                    <ListItem key={`general_${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={`• ${tip}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
          </Card>
        </SectionErrorBoundary>
      )}


      {/* AI-Enhanced Insights */}
      {processedData?.seasonal_advice && (
        <SectionErrorBoundary sectionName="AI-Enhanced Insights">
          <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              🌟 AI-Enhanced Insights
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Advanced analysis combining weather data, historical patterns, and agricultural expertise
            </Typography>
            
            {processedData.seasonal_advice.general_advice && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  General Advice:
                </Typography>
                <Typography variant="body2">
                  {processedData.seasonal_advice.general_advice}
                </Typography>
              </Box>
            )}

            {processedData.seasonal_advice.timing_recommendations && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Timing Recommendations:
                </Typography>
                <Typography variant="body2">
                  {processedData.seasonal_advice.timing_recommendations}
                </Typography>
              </Box>
            )}

            {processedData.seasonal_advice.weather_considerations && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Weather Considerations:
                </Typography>
                <Typography variant="body2">
                  {processedData.seasonal_advice.weather_considerations}
                </Typography>
              </Box>
            )}

            {processedData.seasonal_advice.risk_mitigation && (
              <Box>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Risk Mitigation:
                </Typography>
                <Typography variant="body2">
                  {processedData.seasonal_advice.risk_mitigation}
                </Typography>
              </Box>
            )}
          </CardContent>
          </Card>
        </SectionErrorBoundary>
      )}

      {/* Data Sources and Analysis Summary */}
      {processedData?.sources && processedData.sources.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              📚 Analysis Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Data Sources:
                </Typography>
                <Typography variant="body2">
                  {processedData.sources.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Historical Analysis:
                </Typography>
                <Typography variant="body2">
                  {processedData.historical_data || 0} years of historical data analyzed
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                  Analysis Timestamp:
                </Typography>
                <Typography variant="body2">
                  {processedData.timestamp ? new Date(processedData.timestamp).toLocaleString() : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Recommendations Display */}
      {!loading && !isLoading && recommendations.length > 0 && (
        <>
          {selectedSeason === 'all' ? (
            <SeasonalComparison data={processedData} />
          ) : (
            <>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" fontWeight="bold">
                  Recommended Crops
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <Chip
                    label={`${pagination.total} recommendations`}
                    color="primary"
                    variant="outlined"
                  />
                  {pagination.total > pagination.limit && (
                    <Typography variant="body2" color="text.secondary">
                      Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total}
                    </Typography>
                  )}
                </Box>
              </Box>
              
              <Grid container spacing={3}>
                {recommendations
                  .slice(pagination.offset, pagination.offset + pagination.limit)
                  .map((crop, index) => (
                  <Grid item xs={12} sm={6} md={4} key={crop.crop_name || index}>
                    <CropRecommendationCard
                      crop={crop}
                      onClick={() => {
                        // Navigate to variety details
                        window.location.href = `/varieties?crop=${crop.crop_name}&lat=${currentLocation.lat}&lon=${currentLocation.lon}`
                      }}
                    />
                  </Grid>
                ))}
              </Grid>

              {/* Pagination Controls */}
              {pagination.total > pagination.limit && (
                <Box display="flex" justifyContent="center" alignItems="center" gap={2} mt={4}>
                  <Button
                    variant="outlined"
                    startIcon={<PrevIcon />}
                    onClick={handlePrevPage}
                    disabled={pagination.offset === 0}
                  >
                    Previous
                  </Button>
                  
                  <Box display="flex" gap={1}>
                    {Array.from({ length: Math.ceil(pagination.total / pagination.limit) }, (_, i) => {
                      const pageOffset = i * pagination.limit
                      const isCurrentPage = pageOffset === pagination.offset
                      return (
                        <Button
                          key={i}
                          variant={isCurrentPage ? "contained" : "outlined"}
                          size="small"
                          onClick={() => handlePageChange(pageOffset)}
                          sx={{ minWidth: 40 }}
                        >
                          {i + 1}
                        </Button>
                      )
                    })}
                  </Box>
                  
                  <Button
                    variant="outlined"
                    endIcon={<NextIcon />}
                    onClick={handleNextPage}
                    disabled={pagination.offset + pagination.limit >= pagination.total}
                  >
                    Next
                  </Button>
                </Box>
              )}
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
    </CropDataErrorBoundary>
  )
}

export default CropRecommendations