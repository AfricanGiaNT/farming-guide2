import React, { useState } from 'react'
import {
  Box,
  TextField,
  Button,
  Typography,
  Chip,
  useTheme,
  InputAdornment,
  IconButton,
} from '@mui/material'
import {
  MyLocation as GPSIcon,
  LocationOn as LocationIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'

interface SimplifiedLocationInputProps {
  lat: number
  lon: number
  onChange: (lat: number, lon: number) => void
}

const SimplifiedLocationInput: React.FC<SimplifiedLocationInputProps> = ({ 
  lat, 
  lon, 
  onChange 
}) => {
  const theme = useTheme()
  const [gpsLoading, setGpsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const knownLocations = [
    { name: 'Lilongwe', lat: -13.9833, lon: 33.7833 },
    { name: 'Area 1', lat: -13.9700, lon: 33.7700 },
    { name: 'Area 2', lat: -13.9800, lon: 33.7800 },
    { name: 'Kawale', lat: -13.9300, lon: 33.7300 },
    { name: 'Mgona', lat: -13.9500, lon: 33.8000 },
  ]

  const handleGPSLocation = () => {
    if (!navigator.geolocation) {
      setError('GPS not supported')
      return
    }

    setGpsLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLat = position.coords.latitude
        const newLon = position.coords.longitude
        onChange(newLat, newLon)
        setGpsLoading(false)
      },
      (error) => {
        setError('Unable to get location')
        setGpsLoading(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000,
      }
    )
  }

  const handleKnownLocation = (location: { lat: number; lon: number }) => {
    onChange(location.lat, location.lon)
    setError(null)
  }

  return (
    <Box>
      {/* Location Display */}
      <Box 
        display="flex" 
        alignItems="center" 
        gap={1}
        sx={{
          backgroundColor: 'grey.50',
          borderRadius: 1,
          p: 1,
          border: '1px solid',
          borderColor: 'grey.200',
        }}
      >
        <LocationIcon fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
          Location: {lat.toFixed(4)}, {lon.toFixed(4)}
        </Typography>
        <Button
          size="small"
          variant="outlined"
          startIcon={<GPSIcon />}
          onClick={handleGPSLocation}
          disabled={gpsLoading}
          sx={{ minWidth: 'auto', px: 1 }}
        >
          {gpsLoading ? '...' : 'GPS'}
        </Button>
      </Box>

      {/* Quick Location Chips */}
      <Box mt={1}>
        <Box display="flex" gap={0.5} flexWrap="wrap">
          {knownLocations.map((location) => (
            <Chip
              key={location.name}
              label={location.name}
              onClick={() => handleKnownLocation(location)}
              variant="outlined"
              size="small"
              sx={{
                cursor: 'pointer',
                fontSize: '0.7rem',
                height: 24,
                '&:hover': {
                  backgroundColor: theme.palette.primary.light,
                  color: 'white',
                },
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
          {error}
        </Typography>
      )}
    </Box>
  )
}

export default SimplifiedLocationInput