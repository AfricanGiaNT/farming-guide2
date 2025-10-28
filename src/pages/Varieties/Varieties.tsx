import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Autocomplete,
  Alert,
  Skeleton,
  Chip,
  Button,
} from '@mui/material'
import {
  Search as SearchIcon,
  Agriculture as VarietyIcon,
  LocationOn as LocationIcon,
  Compare as CompareIcon,
} from '@mui/icons-material'
import { useVarietyInformation } from '../../hooks/useCropRecommendations'
import EnhancedVarietyDetailCard from '../../components/Varieties/CompactVarietyCard'
import VarietyComparison from '../../components/Varieties/VarietyComparison'
import { setSelectedCrop } from '../../store/slices/cropSlice'
import { setSelectedVarieties, addSelectedVariety, removeSelectedVariety } from '../../store/slices/knowledgeSlice'
import { RootState } from '../../store/store'

const Varieties: React.FC = () => {
  const dispatch = useDispatch()
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Get persisted state from Redux with safe defaults
  const persistedCrop = useSelector((state: RootState) => (state.crop && state.crop.selectedCrop) || null)
  const persistedVarieties = useSelector((state: RootState) => (state.knowledge && state.knowledge.selectedVarieties && Array.isArray(state.knowledge.selectedVarieties)) ? state.knowledge.selectedVarieties : [])
  
  // Initialize from URL params first, then Redux persisted state
  const urlCrop = searchParams.get('crop') || ''
  const [selectedCrop, setSelectedCropLocal] = useState(urlCrop || persistedCrop || '')
  const [locationInput, setLocationInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [compareMode, setCompareMode] = useState(false)
  const [selectedVarieties, setSelectedVarietiesLocal] = useState<string[]>(persistedVarieties || [])
  
  // Sync with Redux persisted state on mount and when it changes
  useEffect(() => {
    // If URL has a crop, use it and update Redux
    if (urlCrop && urlCrop !== selectedCrop) {
      setSelectedCropLocal(urlCrop)
      dispatch(setSelectedCrop(urlCrop))
    }
    // If no URL crop but we have persisted crop, use it
    else if (!urlCrop && persistedCrop && persistedCrop !== selectedCrop) {
      setSelectedCropLocal(persistedCrop)
    }
    
    // Sync varieties (safe check for undefined)
    if (persistedVarieties && Array.isArray(persistedVarieties) && persistedVarieties.length > 0) {
      const currentStr = JSON.stringify(selectedVarieties || [])
      const persistedStr = JSON.stringify(persistedVarieties)
      if (persistedStr !== currentStr) {
        setSelectedVarietiesLocal(persistedVarieties)
      }
    }
  }, [urlCrop, persistedCrop, persistedVarieties, dispatch]) // eslint-disable-line react-hooks/exhaustive-deps

  // Parse coordinates from URL params or location input
  const lat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : undefined
  const lon = searchParams.get('lon') ? parseFloat(searchParams.get('lon')!) : undefined

  const { data: varietyData, isLoading, error } = useVarietyInformation(selectedCrop, lat, lon)

  const cropOptions = [
    'maize', 'phaseolus beans', 'groundnut', 'sorghum', 'cassava', 'sweet potato',
    'soyabean', 'pigeonpea', 'cowpea', 'rice', 'pearl millet', 'finger millet', 'wheat',
    'tomatoes', 'onions', 'cabbage', 'leafy vegetables', 'okra', 'carrot',
    'chillies', 'tumeric', 'ginger', 'cardamom', 'pepper', 'coriander',
    'citrus', 'bananas', 'pineapples', 'mangoes', 'avocado', 'pawpaw',
    'tobacco', 'cotton', 'sunflower', 'sesame', 'castor seed'
  ]

  // Function to parse coordinates from location input
  const parseCoordinates = (input: string): { lat: number; lon: number } | null => {
    if (!input.trim()) return null
    
    // Try to match coordinate patterns like "-13.9833, 33.7833"
    const coordPattern = /(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)/
    const match = input.match(coordPattern)
    
    if (match) {
      const lat = parseFloat(match[1])
      const lon = parseFloat(match[2])
      if (!isNaN(lat) && !isNaN(lon)) {
        return { lat, lon }
      }
    }
    
    return null
  }

  useEffect(() => {
    if (selectedCrop) {
      setSearchParams(prev => {
        const newParams = new URLSearchParams(prev)
        newParams.set('crop', selectedCrop)
        return newParams
      })
      // Update Redux when crop changes
      dispatch(setSelectedCrop(selectedCrop))
    }
  }, [selectedCrop, setSearchParams, dispatch])

  const handleCropSelect = (crop: string | null) => {
    const cropValue = crop || ''
    setSelectedCropLocal(cropValue)
    setCompareMode(false)
    setSelectedVarietiesLocal([])
    dispatch(setSelectedCrop(cropValue))
    dispatch(setSelectedVarieties([]))
  }

  const handleVarietySelect = (varietyName: string) => {
    if (compareMode) {
      setSelectedVarietiesLocal(prev => {
        if (prev.includes(varietyName)) {
          const newList = prev.filter(v => v !== varietyName)
          dispatch(setSelectedVarieties(newList))
          dispatch(removeSelectedVariety(varietyName))
          return newList
        } else if (prev.length < 3) {
          const newList = [...prev, varietyName]
          dispatch(setSelectedVarieties(newList))
          dispatch(addSelectedVariety(varietyName))
          return newList
        }
        return prev
      })
    }
  }

  const filteredVarieties = varietyData?.varieties?.filter((variety: any) =>
    variety.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    variety.type?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
        Crop Varieties
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Explore detailed information about crop varieties and their characteristics
      </Typography>

      {/* Search and Filter Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <Autocomplete
                value={selectedCrop}
                onChange={(_event, newValue) => handleCropSelect(newValue)}
                options={cropOptions}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Crop"
                    placeholder="e.g., maize, groundnut, beans"
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: (
                        <InputAdornment position="start">
                          <VarietyIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                label="Location (Optional)"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                placeholder="e.g., -13.9833, 33.7833 or Lilongwe"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LocationIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                fullWidth
                helperText="Add coordinates or location name for better recommendations"
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => {
                  if (selectedCrop) {
                    // Parse location input and update URL params
                    const coords = parseCoordinates(locationInput)
                    setSearchParams(prev => {
                      const newParams = new URLSearchParams(prev)
                      newParams.set('crop', selectedCrop)
                      if (coords) {
                        newParams.set('lat', coords.lat.toString())
                        newParams.set('lon', coords.lon.toString())
                      } else {
                        newParams.delete('lat')
                        newParams.delete('lon')
                      }
                      return newParams
                    })
                  }
                }}
                fullWidth
                disabled={!selectedCrop}
                size="large"
              >
                Search Varieties
              </Button>
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                variant={compareMode ? "contained" : "outlined"}
                startIcon={<CompareIcon />}
                onClick={() => setCompareMode(!compareMode)}
                fullWidth
              >
                Compare
              </Button>
            </Grid>
          </Grid>

          {/* Location Context */}
          {lat && lon && (
            <Box mt={2}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  📍 Showing location-specific recommendations for coordinates: {lat.toFixed(4)}, {lon.toFixed(4)}
                  <br />
                  🌦️ Weather analysis and local growing conditions included in recommendations
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Search Instructions */}
          {!selectedCrop && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                💡 <strong>How to use:</strong>
                <br />
                1. Select a crop from the dropdown (e.g., Maize, Groundnuts, Beans)
                <br />
                2. Optionally add your location for better recommendations
                <br />
                3. Click "Search Varieties" to get detailed variety information
                <br />
                <br />
                <strong>Location formats:</strong> -13.9833, 33.7833 or Lilongwe, Area 1
              </Typography>
              
              {/* Quick Example Buttons */}
              <Box display="flex" gap={1} flexWrap="wrap">
                <Typography variant="caption" sx={{ mr: 1, alignSelf: 'center' }}>
                  Quick examples:
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    handleCropSelect('maize')
                    setLocationInput('-13.9833, 33.7833')
                  }}
                >
                  Maize + Location
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    handleCropSelect('groundnut')
                    setLocationInput('')
                  }}
                >
                  Groundnuts
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    handleCropSelect('phaseolus beans')
                    setLocationInput('-13.9833, 33.7833')
                  }}
                >
                  Beans + Location
                </Button>
              </Box>
            </Alert>
          )}

          {/* Compare Mode Instructions */}
          {compareMode && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Compare mode active. Select up to 3 varieties to compare side-by-side.
                {selectedVarieties.length > 0 && ` Selected: ${selectedVarieties.length}/3`}
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Error Handling */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Unable to fetch variety information. Please try again later.
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && selectedCrop && (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Skeleton variant="rectangular" height={300} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Variety Comparison */}
      {compareMode && selectedVarieties.length > 1 && (
        <Box mb={3}>
          <VarietyComparison
            varieties={selectedVarieties.map(name => 
              filteredVarieties.find((v: any) => v.name === name)
            ).filter(Boolean)}
            onClose={() => {
              setCompareMode(false)
              setSelectedVarieties([])
            }}
          />
        </Box>
      )}

      {/* Varieties Display */}
      {!isLoading && selectedCrop && filteredVarieties.length > 0 && (
        <>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" fontWeight="bold">
              {selectedCrop} Varieties
            </Typography>
            <Chip
              label={`${filteredVarieties.length} varieties found`}
              color="primary"
              variant="outlined"
            />
          </Box>
          
          <Grid container spacing={2}>
            {filteredVarieties.map((variety: any, index: number) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={variety.name || index}>
                <EnhancedVarietyDetailCard
                  variety={variety}
                  isSelected={selectedVarieties.includes(variety.name)}
                  compareMode={compareMode}
                  onSelect={() => handleVarietySelect(variety.name)}
                  locationSpecific={!!(lat && lon)}
                  cropName={selectedCrop}
                />
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* Empty States */}
      {!selectedCrop && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <VarietyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Select a crop to explore varieties
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Choose from over 20 crop types to see detailed variety information,
              planting requirements, and performance characteristics.
            </Typography>
          </CardContent>
        </Card>
      )}

      {selectedCrop && !isLoading && filteredVarieties.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              No varieties found
            </Typography>
            <Typography variant="body1" color="text.secondary">
              No varieties found for "{selectedCrop}" matching your search criteria.
              Try adjusting your search or selecting a different crop.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default Varieties