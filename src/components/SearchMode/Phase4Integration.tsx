/**
 * Phase4Integration Component
 * Integrates all Phase 4 functionality into a single component
 * Implements Phase 4: Specific Crop Search Integration
 */

import React, { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Box, Alert, CircularProgress } from '@mui/material'
import { RootState } from '../../store/store'
import { setCropRecommendations } from '../../store/slices/cropSlice'
import { useCropRecommendations } from '../../hooks/useCropRecommendations'
import { useSpecificCropRecommendations } from '../../hooks/useSpecificCropRecommendations'
import { cropDataProcessor } from '../../services/cropDataProcessor'
import EnhancedSearchForm, { SearchParams } from './EnhancedSearchForm'
import SmartRecommendationDisplay from './SmartRecommendationDisplay'
import { SearchMode } from './SearchModeToggle'

const Phase4Integration: React.FC = () => {
  const dispatch = useDispatch()
  const { location } = useSelector((state: RootState) => state.user)
  const { selectedSeason, recommendations, loading, error } = useSelector((state: RootState) => state.crop)
  
  const [currentLocation, setCurrentLocation] = useState({
    lat: location?.lat || -13.9833,
    lon: location?.lon || 33.7833,
    name: location?.name || 'Lilongwe'
  })
  
  const [searchParams, setSearchParams] = useState<SearchParams>({
    location: currentLocation.name,
    season: selectedSeason,
    searchMode: { type: 'all_crops' }
  })
  
  const [processedData, setProcessedData] = useState<any>(null)
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'enhanced' | 'fallback'>('idle')
  const [favorites, setFavorites] = useState<string[]>([])

  // Use appropriate hook based on search mode
  const allCropsQuery = useCropRecommendations(
    currentLocation.lat,
    currentLocation.lon,
    searchParams.season,
    searchParams.searchMode.type === 'all_crops'
  )

  const specificCropQuery = useSpecificCropRecommendations({
    cropName: searchParams.searchMode.cropName || '',
    lat: currentLocation.lat,
    lon: currentLocation.lon,
    season: searchParams.season,
    enabled: searchParams.searchMode.type === 'specific_crop' && !!searchParams.searchMode.cropName
  })

  // Determine which query to use
  const activeQuery = searchParams.searchMode.type === 'all_crops' ? allCropsQuery : specificCropQuery
  const cropData = activeQuery.data
  const isLoading = activeQuery.isLoading
  const apiError = activeQuery.error

  // Process data when it changes
  useEffect(() => {
    if (cropData?.recommendations) {
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
            searchParams.season,
            weatherData
          )

          setProcessedData(processed)
          dispatch(setCropRecommendations(processed.recommendations))

          if (processed.processing_metadata?.ai_enhanced) {
            setProcessingStatus('enhanced')
          } else {
            setProcessingStatus('fallback')
          }

          if (processed.processing_metadata) {
            console.log('Data processing completed:', processed.processing_metadata)
          }
        } catch (error) {
          console.error('Data processing failed:', error)
          setProcessingStatus('fallback')
          setProcessedData(cropData)
          dispatch(setCropRecommendations(cropData.recommendations))
        }
      }
      processData()
    }
  }, [cropData, dispatch, currentLocation, searchParams.season])

  const handleSearch = (params: SearchParams) => {
    setSearchParams(params)
    
    // Update location if coordinates are provided
    if (params.coordinates) {
      setCurrentLocation({
        lat: params.coordinates.lat,
        lon: params.coordinates.lon,
        name: params.location
      })
    } else {
      setCurrentLocation(prev => ({
        ...prev,
        name: params.location
      }))
    }
  }

  const handleRetry = () => {
    activeQuery.refetch()
  }

  const handleFavorite = (cropName: string) => {
    setFavorites(prev => {
      if (prev.includes(cropName)) {
        return prev.filter(name => name !== cropName)
      } else {
        return [...prev, cropName]
      }
    })
  }

  const availableCrops = [
    'maize', 'beans', 'groundnuts', 'rice', 'sorghum', 'millet', 
    'cassava', 'sweet potato', 'tomato', 'onion', 'cabbage', 'carrot'
  ]

  const availableSeasons = ['current', 'rainy_season', 'dry_season']

  return (
    <Box>
      {/* Enhanced Search Form */}
      <EnhancedSearchForm
        onSearch={handleSearch}
        loading={isLoading}
        currentLocation={currentLocation}
        availableSeasons={availableSeasons}
        availableCrops={availableCrops}
        lastSearchParams={searchParams}
      />

      {/* Processing Status Indicator */}
      {processingStatus !== 'idle' && (
        <Box sx={{ mb: 2 }}>
          {processingStatus === 'processing' && (
            <Alert severity="info" sx={{ display: 'flex', alignItems: 'center' }}>
              <CircularProgress size={20} sx={{ mr: 1 }} />
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

      {/* Smart Recommendation Display */}
      <SmartRecommendationDisplay
        searchMode={searchParams.searchMode}
        recommendations={processedData?.recommendations || cropData?.recommendations || []}
        loading={isLoading}
        error={apiError?.message}
        onRetry={handleRetry}
        onFavorite={handleFavorite}
        favorites={favorites}
        searchParams={searchParams}
      />
    </Box>
  )
}

export default Phase4Integration
