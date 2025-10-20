import React, { useState } from 'react'
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Grid,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  MyLocation as GPSIcon,
  Link as LinkIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { GoogleMapsUrlParser } from '../../utils/googleMapsUrlParser'

interface SimplifiedLocationInputProps {
  onLocationChange: (lat: number, lon: number) => void
  currentLocation?: { lat: number; lon: number }
  disabled?: boolean
}

const SimplifiedLocationInput: React.FC<SimplifiedLocationInputProps> = ({
  onLocationChange,
  currentLocation,
  disabled = false
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [googleMapsUrl, setGoogleMapsUrl] = useState('')
  const [gpsLoading, setGpsLoading] = useState(false)
  const [urlLoading, setUrlLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [activeMethod, setActiveMethod] = useState<'current' | 'google' | null>(null)

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('GPS not supported by this browser')
      return
    }

    setGpsLoading(true)
    setError(null)
    setSuccess(null)
    setActiveMethod('current')

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude
        onLocationChange(lat, lon)
        setSuccess(`Location set: ${lat.toFixed(4)}, ${lon.toFixed(4)}`)
        setGpsLoading(false)
      },
      (error) => {
        let errorMessage = 'Unable to get your location. '
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += 'Please allow location access and try again.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage += 'Location information is unavailable.'
            break
          case error.TIMEOUT:
            errorMessage += 'Location request timed out.'
            break
          default:
            errorMessage += 'Please try again or use Google Maps link instead.'
            break
        }
        setError(errorMessage)
        setGpsLoading(false)
        setActiveMethod(null)
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 300000, // 5 minutes
      }
    )
  }

  const handleGoogleMapsUrl = async () => {
    if (!googleMapsUrl.trim()) {
      setError('Please enter a Google Maps URL')
      return
    }

    setUrlLoading(true)
    setError(null)
    setSuccess(null)
    setActiveMethod('google')

    try {
      const result = GoogleMapsUrlParser.parseUrlSync(googleMapsUrl.trim())
      
      if (result.success && result.coordinates) {
        const { lat, lon } = result.coordinates
        onLocationChange(lat, lon)
        setSuccess(`Location set: ${lat.toFixed(4)}, ${lon.toFixed(4)}`)
        setGoogleMapsUrl('') // Clear the input after successful parsing
      } else {
        setError(result.error || 'Failed to parse Google Maps URL')
        setActiveMethod(null)
      }
    } catch (error) {
      setError(`Error parsing URL: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setActiveMethod(null)
    } finally {
      setUrlLoading(false)
    }
  }

  const handleUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setGoogleMapsUrl(event.target.value)
    setError(null)
    setSuccess(null)
    if (activeMethod === 'google') {
      setActiveMethod(null)
    }
  }

  const resetState = () => {
    setError(null)
    setSuccess(null)
    setActiveMethod(null)
    setGoogleMapsUrl('')
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant={isMobile ? "subtitle1" : "h6"} gutterBottom fontWeight="bold">
        Location Settings
      </Typography>
      
      <Typography variant={isMobile ? "caption" : "body2"} color="text.secondary" paragraph>
        Choose how to set your location for historical weather data:
      </Typography>

      {/* Current Location Button */}
      <Paper sx={{ p: isMobile ? 1.5 : 2, mb: 2 }}>
        <Box display="flex" alignItems="center" gap={isMobile ? 1 : 2}>
          <Button
            variant={activeMethod === 'current' ? 'contained' : 'outlined'}
            startIcon={gpsLoading ? <CircularProgress size={20} /> : <GPSIcon />}
            onClick={handleUseCurrentLocation}
            disabled={disabled || gpsLoading}
            fullWidth={isMobile}
            sx={{ 
              minHeight: isMobile ? 40 : 48,
              justifyContent: 'flex-start',
              fontSize: isMobile ? '0.75rem' : '0.875rem'
            }}
          >
            {gpsLoading ? 'Getting your location...' : 'Use My Current Location'}
          </Button>
          
          {activeMethod === 'current' && success && (
            <SuccessIcon color="success" />
          )}
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Uses your device's GPS to get precise coordinates
        </Typography>
      </Paper>

      {/* Google Maps URL Input */}
      <Paper sx={{ p: isMobile ? 1.5 : 2, mb: 2 }}>
        <Typography variant={isMobile ? "body2" : "subtitle2"} gutterBottom fontWeight="bold">
          OR Paste Google Maps Link
        </Typography>
        
        <Box display="flex" alignItems="flex-start" gap={isMobile ? 1 : 2} sx={{ mb: 1 }}>
          <TextField
            fullWidth
            placeholder={isMobile ? "https://maps.google.com/..." : "https://maps.google.com/maps/@-13.9833,33.7833,15z"}
            value={googleMapsUrl}
            onChange={handleUrlChange}
            disabled={disabled || urlLoading}
            error={!!error && activeMethod === 'google'}
            helperText={activeMethod === 'google' && error ? error : isMobile ? 'Paste Google Maps URL' : 'Paste any Google Maps URL with coordinates'}
            size="small"
          />
          
          <Button
            variant={activeMethod === 'google' ? 'contained' : 'outlined'}
            startIcon={urlLoading ? <CircularProgress size={20} /> : <LinkIcon />}
            onClick={handleGoogleMapsUrl}
            disabled={disabled || urlLoading || !googleMapsUrl.trim()}
            sx={{ 
              minWidth: isMobile ? 'auto' : 120,
              fontSize: isMobile ? '0.75rem' : '0.875rem',
              height: '40px', // Match TextField height
              alignSelf: 'flex-start',
              mt: '8px' // Align with TextField input area
            }}
          >
            {urlLoading ? 'Parsing...' : 'Set Location'}
          </Button>
          
          {activeMethod === 'google' && success && (
            <SuccessIcon color="success" />
          )}
        </Box>
        
      </Paper>

      {/* Current Location Display */}
      {currentLocation && (
        <Box sx={{ mb: 2 }}>
          <Chip
            icon={<GPSIcon />}
            label={`Current: ${currentLocation.lat.toFixed(4)}, ${currentLocation.lon.toFixed(4)}`}
            color="info"
            variant="outlined"
            size={isMobile ? "small" : "medium"}
            onDelete={resetState}
            deleteIcon={<ErrorIcon />}
          />
        </Box>
      )}

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {/* Success Display */}
      {success && (
        <Alert 
          severity="success" 
          sx={{ mb: 2 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

    </Box>
  )
}

export default SimplifiedLocationInput
