import React, { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  Skeleton,
  Chip,
  List,
  ListItem,
  ListItemText,
  Paper,
  Divider,
  LinearProgress,
  Collapse,
  IconButton,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  NavigateBefore as PrevIcon,
  NavigateNext as NextIcon,
  Clear as ClearIcon,
  Agriculture as CropIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material'
import { RootState } from '../../store/store'
import { setCropRecommendations, setSearchedCrop } from '../../store/slices/cropSlice'
import { useCropRecommendations } from '../../hooks/useCropRecommendations'
import { useSpecificCropRecommendations } from '../../hooks/useSpecificCropRecommendations'
import CropRecommendationCard from '../../components/Crops/CropRecommendationCard'
import TopCropCard from '../../components/Crops/TopCropCard'
import CropSearch from '../../components/Crops/CropSearch'
import SimplifiedLocationInput from '../../components/Location/SimplifiedLocationInput'
import { cropDataProcessor } from '../../services/cropDataProcessor'
import CropDataErrorBoundary from '../../components/ErrorBoundary/CropDataErrorBoundary'

const CropRecommendations: React.FC = () => {
  const dispatch = useDispatch()
  const { location } = useSelector((state: RootState) => state.user)
  const { recommendations, loading, error } = useSelector((state: RootState) => state.crop)
  const persistedSearchCrop = useSelector((state: RootState) => (state.crop && state.crop.searchedCrop) || '')
  
  const [currentLocation, setCurrentLocation] = useState({
    lat: location?.lat || -13.9833,
    lon: location?.lon || 33.7833,
  })
  
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 6,
    total: 0
  })

  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)
  const [searchCrop, setSearchCrop] = useState<string>(persistedSearchCrop || '')
  const [processedData, setProcessedData] = useState<any>(null)
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'enhanced' | 'fallback'>('idle')
  
  // Restore persisted crop selection on mount
  useEffect(() => {
    if (persistedSearchCrop && persistedSearchCrop !== searchCrop) {
      setSearchCrop(persistedSearchCrop)
    }
  }, [persistedSearchCrop]) // eslint-disable-line react-hooks/exhaustive-deps

  const { data: cropData, isLoading, error: apiError, refetch } = useCropRecommendations(
    currentLocation.lat,
    currentLocation.lon,
    'rainy' // Default to rainy season since we removed season selection
  )

  // Fetch specific crop recommendations when searching
  const { data: specificCropData, isLoading: specificCropLoading, error: specificCropError } = useSpecificCropRecommendations(
    searchCrop,
    currentLocation.lat,
    currentLocation.lon,
    'rainy', // Default to rainy season
    !!searchCrop // Only fetch when there's a search term
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
            'rainy_season', // Fixed: Use hardcoded season instead of undefined selectedSeason
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
  }, [cropData, dispatch, currentLocation])

  const handleLocationChange = (lat: number, lon: number) => {
    setCurrentLocation({ lat, lon })
  }

  const handleCropSearch = (cropName: string) => {
    setSearchCrop(cropName)
    dispatch(setSearchedCrop(cropName))
  }

  const handleCropSearchClear = () => {
    setSearchCrop('')
    dispatch(setSearchedCrop(''))
    // Trigger refresh of general recommendations when clearing search
    refetch()
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


  const handleResetFilters = () => {
    if (processedData?.recommendations) {
      dispatch(setCropRecommendations(processedData.recommendations))
      setPagination(prev => ({
        ...prev,
        total: processedData.recommendations.length,
        offset: 0
      }))
    }
  }

  return (
    <CropDataErrorBoundary 
      fallbackTitle="Crop Recommendations Error"
      fallbackMessage="There was an error loading crop recommendations. This might be due to server issues or malformed data."
      onRetry={() => refetch()}
    >
      <Box>
        <Typography variant="h5" gutterBottom fontWeight="bold" color="primary">
          Crop Recommendations
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
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

      {/* Crop Search - Primary Workflow Entry Point */}
      <CropSearch
        onSearch={handleCropSearch}
        onClear={handleCropSearchClear}
        onGetRecommendations={() => refetch()} // Pass the refetch function for main workflow
        isLoading={specificCropLoading}
        currentCrop={searchCrop}
        isSearchMode={!!searchCrop}
      />

      {/* Location Input - Right under search box */}
      <Box sx={{ mt: 2, mb: 2 }}>
        <SimplifiedLocationInput
          lat={currentLocation.lat}
          lon={currentLocation.lon}
          onChange={handleLocationChange}
        />
      </Box>

      {/* Action Buttons */}
      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <Button
          variant="contained"
          onClick={() => refetch()}
          startIcon={<CropIcon />}
          size="small"
          sx={{ fontWeight: 'bold' }}
        >
          Get Recommendations
        </Button>
        
        <Button
          variant="outlined"
          onClick={handleResetFilters}
          startIcon={<ClearIcon />}
          size="small"
        >
          Reset Filters
        </Button>
        
        <Button
          variant="outlined"
          onClick={() => refetch()}
          startIcon={<RefreshIcon />}
          size="small"
        >
          Refresh Data
        </Button>

        <Button
          variant="outlined"
          onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
          endIcon={showAdvancedOptions ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          size="small"
        >
          Advanced Options
        </Button>
      </Box>

      {/* Advanced Options */}
      <Collapse in={showAdvancedOptions}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Advanced Options
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Additional features and detailed information
            </Typography>
            
            {/* Risk Assessment */}
            {processedData?.risk_assessment && (
              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
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
                
                {processedData.risk_assessment.weather_risks?.length > 0 && (
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

                {processedData.risk_assessment.pest_risks?.length > 0 && (
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
              </Box>
            )}

            {/* Management Tips */}
            {processedData?.management_tips && (
              (processedData.management_tips.planting?.length > 0) || 
              (processedData.management_tips.maintenance?.length > 0) || 
              (processedData.management_tips.harvest?.length > 0) || 
              (processedData.management_tips.general?.length > 0)
            ) && (
              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Management Tips
                </Typography>
                
                {processedData.management_tips.planting?.length > 0 && (
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

                {processedData.management_tips.maintenance?.length > 0 && (
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

                {processedData.management_tips.harvest?.length > 0 && (
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

                {processedData.management_tips.general?.length > 0 && (
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
              </Box>
            )}
          </CardContent>
        </Card>
      </Collapse>

      {/* Specific Crop Search Results */}
      {searchCrop && specificCropData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h5" fontWeight="bold" color="primary.main">
                🌾 {searchCrop} Recommendations
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleCropSearchClear}
                startIcon={<ClearIcon />}
              >
                Clear Search
              </Button>
            </Box>
            
            {specificCropData.recommendations && specificCropData.recommendations.length > 0 ? (
              <Grid container spacing={2}>
                {specificCropData.recommendations.map((crop: any, index: number) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <TopCropCard
                      crop={{
                        crop_name: crop.crop_name || searchCrop,
                        score: crop.score || crop.suitability_score || 0,
                        suitability_level: crop.suitability_level || 'good',
                        top_varieties: crop.varieties?.slice(0, 3) || [],
                        planting_time: crop.planting_time,
                        yield_potential: crop.yield_potential,
                        description: crop.description
                      }}
                      rank={index + 1}
                      onClick={() => {
                        window.location.href = `/varieties?crop=${crop.crop_name || searchCrop}&lat=${currentLocation.lat}&lon=${currentLocation.lon}`
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box textAlign="center" py={4}>
                <Typography variant="body1" color="text.secondary">
                  No specific recommendations found for "{searchCrop}". Try a different crop name.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}


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

      {/* Top 3 Crop Recommendations */}
      {!loading && !isLoading && recommendations.length > 0 && (
        <>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                🌟 Top Crop Recommendations
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
                Best crops for your location and season
              </Typography>
            </Box>
            <Chip
              label={`${recommendations.length} total`}
              color="primary"
              variant="outlined"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
          
          {/* Top 3 Crops - Prominent Display */}
          <Grid container spacing={3} mb={4}>
            {recommendations.slice(0, 3).map((crop, index) => (
              <Grid item xs={12} sm={6} md={4} key={crop.crop_name || index}>
                <TopCropCard
                  crop={{
                    crop_name: crop.crop_name,
                    score: crop.score || crop.suitability_score || 0,
                    suitability_level: crop.suitability_level || 'good',
                    top_varieties: crop.varieties?.slice(0, 3) || [],
                    planting_time: crop.planting_time,
                    yield_potential: crop.yield_potential,
                    description: crop.description
                  }}
                  rank={index + 1}
                  onClick={() => {
                    window.location.href = `/varieties?crop=${crop.crop_name}&lat=${currentLocation.lat}&lon=${currentLocation.lon}`
                  }}
                />
              </Grid>
            ))}
          </Grid>

          {/* View All Recommendations Button */}
          {recommendations.length > 3 && (
            <Box display="flex" justifyContent="center" mb={3}>
              <Button
                variant="outlined"
                size="large"
                onClick={() => {
                  // Scroll to all recommendations section
                  const element = document.getElementById('all-recommendations')
                  element?.scrollIntoView({ behavior: 'smooth' })
                }}
                sx={{ minWidth: 200 }}
              >
                View All {recommendations.length} Recommendations
              </Button>
            </Box>
          )}
        </>
      )}

      {/* All Recommendations Section */}
      {!loading && !isLoading && recommendations.length > 0 && (
        <Box id="all-recommendations">
          <Typography variant="h6" fontWeight="bold" mb={2}>
            All Recommendations
          </Typography>
          
          <Grid container spacing={2}>
            {recommendations
              .slice(pagination.offset, pagination.offset + pagination.limit)
              .map((crop, index) => (
              <Grid item xs={12} sm={6} md={4} key={crop.crop_name || index}>
                <CropRecommendationCard
                  crop={crop}
                  onClick={() => {
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
        </Box>
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