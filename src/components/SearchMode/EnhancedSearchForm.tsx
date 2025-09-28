/**
 * EnhancedSearchForm Component
 * Provides enhanced search form with integrated search mode toggle and crop selection
 * Implements Phase 4: Specific Crop Search Integration
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material'
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Agriculture as AgricultureIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import SearchModeToggle, { SearchMode } from './SearchModeToggle'

export interface EnhancedSearchFormProps {
  onSearch: (searchParams: SearchParams) => void
  loading?: boolean
  currentLocation?: { lat: number; lon: number; name: string }
  availableSeasons?: string[]
  availableCrops?: string[]
  lastSearchParams?: SearchParams
}

export interface SearchParams {
  location: string
  season: string
  searchMode: SearchMode
  coordinates?: { lat: number; lon: number }
}

const EnhancedSearchForm: React.FC<EnhancedSearchFormProps> = ({
  onSearch,
  loading = false,
  currentLocation,
  availableSeasons = ['current', 'rainy_season', 'dry_season'],
  availableCrops = ['maize', 'beans', 'groundnuts', 'rice', 'sorghum', 'millet', 'cassava', 'sweet potato'],
  lastSearchParams
}) => {
  const [location, setLocation] = useState(currentLocation?.name || 'Lilongwe')
  const [season, setSeason] = useState('current')
  const [searchMode, setSearchMode] = useState<SearchMode>({ type: 'all_crops' })
  const [customLocation, setCustomLocation] = useState('')
  const [useCustomLocation, setUseCustomLocation] = useState(false)

  // Initialize with last search params if available
  useEffect(() => {
    if (lastSearchParams) {
      setLocation(lastSearchParams.location)
      setSeason(lastSearchParams.season)
      setSearchMode(lastSearchParams.searchMode)
      if (lastSearchParams.coordinates) {
        setUseCustomLocation(true)
        setCustomLocation(`${lastSearchParams.coordinates.lat}, ${lastSearchParams.coordinates.lon}`)
      }
    }
  }, [lastSearchParams])

  const handleSearch = () => {
    const searchParams: SearchParams = {
      location: useCustomLocation ? customLocation : location,
      season,
      searchMode,
      coordinates: useCustomLocation ? parseCoordinates(customLocation) : undefined
    }
    
    onSearch(searchParams)
  }

  const parseCoordinates = (coordString: string): { lat: number; lon: number } | undefined => {
    try {
      const [lat, lon] = coordString.split(',').map(coord => parseFloat(coord.trim()))
      if (!isNaN(lat) && !isNaN(lon)) {
        return { lat, lon }
      }
    } catch (error) {
      console.error('Error parsing coordinates:', error)
    }
    return undefined
  }

  const handleLocationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    setLocation(value)
    setUseCustomLocation(false)
  }

  const handleCustomLocationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    setCustomLocation(value)
    setUseCustomLocation(true)
  }

  const handleSeasonChange = (event: any) => {
    setSeason(event.target.value)
  }

  const handleSearchModeChange = (newSearchMode: SearchMode) => {
    setSearchMode(newSearchMode)
  }

  const getSeasonLabel = (seasonValue: string) => {
    switch (seasonValue) {
      case 'current':
        return 'Current Season'
      case 'rainy_season':
        return 'Rainy Season'
      case 'dry_season':
        return 'Dry Season'
      default:
        return seasonValue
    }
  }

  const getSeasonDescription = (seasonValue: string) => {
    switch (seasonValue) {
      case 'current':
        return 'Recommendations based on current weather conditions'
      case 'rainy_season':
        return 'Recommendations for the rainy season (November-April)'
      case 'dry_season':
        return 'Recommendations for the dry season (May-October)'
      default:
        return ''
    }
  }

  const isSearchDisabled = () => {
    if (loading) return true
    if (searchMode.type === 'specific_crop' && !searchMode.cropName) return true
    if (useCustomLocation && !parseCoordinates(customLocation)) return true
    return false
  }

  const getSearchButtonText = () => {
    if (loading) return 'Searching...'
    if (searchMode.type === 'specific_crop') {
      return `Search ${searchMode.cropName || 'Crop'}`
    }
    return 'Get Crop Recommendations'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <AgricultureIcon color="primary" />
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              Crop Recommendations
            </Typography>
          </Box>

          {/* Search Mode Toggle */}
          <SearchModeToggle
            searchMode={searchMode}
            onSearchModeChange={handleSearchModeChange}
            availableCrops={availableCrops}
            disabled={loading}
          />

          <Divider sx={{ my: 3 }} />

          {/* Location Selection */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Location
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Select Location</InputLabel>
                  <Select
                    value={useCustomLocation ? 'custom' : location}
                    label="Select Location"
                    onChange={(e) => {
                      if (e.target.value === 'custom') {
                        setUseCustomLocation(true)
                      } else {
                        setLocation(e.target.value)
                        setUseCustomLocation(false)
                      }
                    }}
                    disabled={loading}
                  >
                    <MenuItem value="Lilongwe">Lilongwe</MenuItem>
                    <MenuItem value="Blantyre">Blantyre</MenuItem>
                    <MenuItem value="Mzuzu">Mzuzu</MenuItem>
                    <MenuItem value="Zomba">Zomba</MenuItem>
                    <MenuItem value="custom">Custom Coordinates</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                {useCustomLocation ? (
                  <TextField
                    fullWidth
                    label="Coordinates (lat, lon)"
                    placeholder="e.g., -13.9833, 33.7833"
                    value={customLocation}
                    onChange={handleCustomLocationChange}
                    disabled={loading}
                    error={customLocation && !parseCoordinates(customLocation)}
                    helperText={customLocation && !parseCoordinates(customLocation) ? 'Invalid coordinates format' : 'Enter latitude and longitude separated by comma'}
                  />
                ) : (
                  <TextField
                    fullWidth
                    label="Custom Location"
                    placeholder="Enter location name"
                    value={location}
                    onChange={handleLocationChange}
                    disabled={loading}
                  />
                )}
              </Grid>
            </Grid>

            {/* Current Location Display */}
            {currentLocation && !useCustomLocation && (
              <Box sx={{ mt: 2 }}>
                <Chip
                  icon={<LocationIcon />}
                  label={`Current: ${currentLocation.name} (${currentLocation.lat.toFixed(4)}, ${currentLocation.lon.toFixed(4)})`}
                  color="info"
                  variant="outlined"
                  size="small"
                />
              </Box>
            )}
          </Box>

          {/* Season Selection */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Season
            </Typography>
            
            <FormControl fullWidth>
              <InputLabel>Select Season</InputLabel>
              <Select
                value={season}
                label="Select Season"
                onChange={handleSeasonChange}
                disabled={loading}
              >
                {availableSeasons.map((seasonValue) => (
                  <MenuItem key={seasonValue} value={seasonValue}>
                    <Box>
                      <Typography variant="body1">
                        {getSeasonLabel(seasonValue)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {getSeasonDescription(seasonValue)}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Search Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
              onClick={handleSearch}
              disabled={isSearchDisabled()}
              sx={{
                minWidth: 200,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
              }}
            >
              {getSearchButtonText()}
            </Button>
          </Box>

          {/* Search Summary */}
          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Search Summary
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                icon={<LocationIcon />}
                label={useCustomLocation ? `Custom: ${customLocation}` : location}
                color="primary"
                variant="outlined"
                size="small"
              />
              <Chip
                icon={<CalendarIcon />}
                label={getSeasonLabel(season)}
                color="secondary"
                variant="outlined"
                size="small"
              />
              <Chip
                icon={<AgricultureIcon />}
                label={searchMode.type === 'all_crops' ? 'All Crops' : `Specific: ${searchMode.cropName || 'Crop'}`}
                color="success"
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>

          {/* Validation Messages */}
          {searchMode.type === 'specific_crop' && !searchMode.cropName && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Please select a specific crop to get detailed recommendations.
              </Typography>
            </Alert>
          )}

          {useCustomLocation && !parseCoordinates(customLocation) && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Please enter valid coordinates in the format: latitude, longitude
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default EnhancedSearchForm
