import React, { useState, useEffect } from 'react'
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
  Tabs,
  Tab,
} from '@mui/material'
import {
  Search as SearchIcon,
  Agriculture as VarietyIcon,
  LocationOn as LocationIcon,
  Compare as CompareIcon,
  List as ListIcon,
  GridView as GridIcon,
} from '@mui/icons-material'
import { useVarietyInformation } from '../../hooks/useCropRecommendations'
import EnhancedVarietyDetailCard from '../../components/Varieties/EnhancedVarietyDetailCard'
import VarietyComparison from '../../components/Varieties/VarietyComparison'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`variety-tabpanel-${index}`}
      aria-labelledby={`variety-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const Varieties: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedCrop, setSelectedCrop] = useState(searchParams.get('crop') || '')
  const [locationInput, setLocationInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [compareMode, setCompareMode] = useState(false)
  const [selectedVarieties, setSelectedVarieties] = useState<string[]>([])
  const [viewMode, setViewMode] = useState(0) // 0 = grid, 1 = list

  // Parse coordinates from URL params or location input
  const lat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : undefined
  const lon = searchParams.get('lon') ? parseFloat(searchParams.get('lon')!) : undefined

  const { data: varietyData, isLoading, error } = useVarietyInformation(selectedCrop, lat, lon)

  // Enhanced crop options based on our database
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
    // Only update URL if selectedCrop differs from URL param to avoid infinite loop
    const currentUrlCrop = searchParams.get('crop')
    if (selectedCrop && selectedCrop !== currentUrlCrop) {
      setSearchParams(prev => {
        const newParams = new URLSearchParams(prev)
        newParams.set('crop', selectedCrop)
        return newParams
      }, { replace: true }) // Use replace to avoid adding to history stack
    }
  }, [selectedCrop]) // Removed setSearchParams from deps to prevent loops

  const handleCropSelect = (crop: string | null) => {
    setSelectedCrop(crop || '')
    setCompareMode(false)
    setSelectedVarieties([])
  }

  const handleVarietySelect = (varietyName: string) => {
    if (compareMode) {
      setSelectedVarieties(prev => {
        if (prev.includes(varietyName)) {
          return prev.filter(v => v !== varietyName)
        } else if (prev.length < 3) {
          return [...prev, varietyName]
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
        🌱 Crop Varieties Database
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Explore comprehensive farming information for crop varieties with detailed production guides, 
        input requirements, and growing timelines extracted from the Malawi Agriculture Guide.
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
                    placeholder="e.g., maize, groundnut, phaseolus beans"
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

            <Grid item xs={12} md={3}>
              <TextField
                label="Search Varieties"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by variety name..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={3}>
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
                helperText="Add coordinates for location-specific info"
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
                    }, { replace: true }) // Use replace to avoid history stack issues
                  }
                }}
                fullWidth
                disabled={!selectedCrop}
                size="large"
              >
                Search Varieties
              </Button>
            </Grid>
          </Grid>

          {/* Action Buttons */}
          <Box display="flex" gap={2} mt={2} alignItems="center">
            <Button
              variant={compareMode ? "contained" : "outlined"}
              startIcon={<CompareIcon />}
              onClick={() => setCompareMode(!compareMode)}
            >
              Compare Varieties
            </Button>
            
            <Box display="flex" border={1} borderColor="divider" borderRadius={1}>
              <Button
                variant={viewMode === 0 ? "contained" : "text"}
                size="small"
                onClick={() => setViewMode(0)}
                startIcon={<GridIcon />}
              >
                Grid
              </Button>
              <Button
                variant={viewMode === 1 ? "contained" : "text"}
                size="small"
                onClick={() => setViewMode(1)}
                startIcon={<ListIcon />}
              >
                List
              </Button>
            </Box>
          </Box>

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
                1. Select a crop from the dropdown (e.g., Maize, Groundnuts, Phaseolus Beans)
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
                    setSelectedCrop('maize')
                    setLocationInput('-13.9833, 33.7833')
                  }}
                >
                  Maize + Location
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setSelectedCrop('groundnut')
                    setLocationInput('')
                  }}
                >
                  Groundnut
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setSelectedCrop('phaseolus beans')
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
              <Skeleton variant="rectangular" height={400} />
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
              {selectedCrop.charAt(0).toUpperCase() + selectedCrop.slice(1)} Varieties
            </Typography>
            <Chip
              label={`${filteredVarieties.length} varieties found`}
              color="primary"
              variant="outlined"
            />
          </Box>
          
          <Grid container spacing={3}>
            {filteredVarieties.map((variety: any, index: number) => (
              <Grid item xs={12} sm={6} md={4} key={variety.name || index}>
                <EnhancedVarietyDetailCard
                  variety={variety}
                  isSelected={selectedVarieties.includes(variety.name)}
                  compareMode={compareMode}
                  onSelect={() => handleVarietySelect(variety.name)}
                  locationSpecific={!!(lat && lon)}
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
              Choose from over 50 crop types to see detailed variety information,
              production timelines, input requirements, and farming processes.
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
