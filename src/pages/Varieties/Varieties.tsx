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
} from '@mui/material'
import {
  Search as SearchIcon,
  Eco as VarietyIcon,
  LocationOn as LocationIcon,
  Compare as CompareIcon,
} from '@mui/icons-material'
import { useVarietyInformation } from '../../hooks/useCropRecommendations'
import VarietyDetailCard from '../../components/Varieties/VarietyDetailCard'
import VarietyComparison from '../../components/Varieties/VarietyComparison'

const Varieties: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedCrop, setSelectedCrop] = useState(searchParams.get('crop') || '')
  const [searchQuery, setSearchQuery] = useState('')
  const [compareMode, setCompareMode] = useState(false)
  const [selectedVarieties, setSelectedVarieties] = useState<string[]>([])

  const lat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : undefined
  const lon = searchParams.get('lon') ? parseFloat(searchParams.get('lon')!) : undefined

  const { data: varietyData, isLoading, error } = useVarietyInformation(selectedCrop, lat, lon)

  const cropOptions = [
    'Maize', 'Beans', 'Groundnuts', 'Sorghum', 'Cassava', 'Sweet Potato',
    'Soybeans', 'Pigeon Peas', 'Cowpeas', 'Rice', 'Millet', 'Wheat',
    'Tomato', 'Onion', 'Cabbage', 'Lettuce', 'Spinach', 'Carrot',
    'Pepper', 'Eggplant', 'Cucumber', 'Pumpkin', 'Watermelon',
  ]

  useEffect(() => {
    if (selectedCrop) {
      setSearchParams(prev => {
        const newParams = new URLSearchParams(prev)
        newParams.set('crop', selectedCrop)
        return newParams
      })
    }
  }, [selectedCrop, setSearchParams])

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
        Crop Varieties
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Explore detailed information about crop varieties and their characteristics
      </Typography>

      {/* Search and Filter Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <Autocomplete
                value={selectedCrop}
                onChange={(_event, newValue) => handleCropSelect(newValue)}
                options={cropOptions}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Crop"
                    placeholder="Choose a crop to explore varieties"
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
                label="Search varieties"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or type"
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
            <Box mt={2} display="flex" alignItems="center" gap={1}>
              <LocationIcon color="action" fontSize="small" />
              <Typography variant="body2" color="text.secondary">
                Location-specific recommendations for {lat.toFixed(4)}, {lon.toFixed(4)}
              </Typography>
            </Box>
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
          
          <Grid container spacing={3}>
            {filteredVarieties.map((variety: any, index: number) => (
              <Grid item xs={12} sm={6} md={4} key={variety.name || index}>
                <VarietyDetailCard
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