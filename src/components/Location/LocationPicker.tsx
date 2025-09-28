import React, { useState } from 'react'
import {
  Box,
  TextField,
  Button,
  Grid,
  Chip,
  Typography,
  Alert,
} from '@mui/material'
import {
  MyLocation as GPSIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material'

interface LocationPickerProps {
  lat: number
  lon: number
  onChange: (lat: number, lon: number) => void
}

const LocationPicker: React.FC<LocationPickerProps> = ({ lat, lon, onChange }) => {
  const [manualLat, setManualLat] = useState(lat.toString())
  const [manualLon, setManualLon] = useState(lon.toString())
  const [gpsLoading, setGpsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const knownLocations = [
    { name: 'Lilongwe', lat: -13.9833, lon: 33.7833 },
    { name: 'Area 1', lat: -13.9700, lon: 33.7700 },
    { name: 'Area 2', lat: -13.9800, lon: 33.7800 },
    { name: 'Area 3', lat: -13.9900, lon: 33.7900 },
    { name: 'Kawale', lat: -13.9300, lon: 33.7300 },
    { name: 'Mgona', lat: -13.9500, lon: 33.8000 },
  ]

  const handleGPSLocation = () => {
    if (!navigator.geolocation) {
      setError('GPS not supported by this browser')
      return
    }

    setGpsLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLat = position.coords.latitude
        const newLon = position.coords.longitude
        setManualLat(newLat.toString())
        setManualLon(newLon.toString())
        onChange(newLat, newLon)
        setGpsLoading(false)
      },
      (error) => {
        setError('Unable to get your location. Please enter coordinates manually.')
        setGpsLoading(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // 5 minutes
      }
    )
  }

  const handleManualUpdate = () => {
    const newLat = parseFloat(manualLat)
    const newLon = parseFloat(manualLon)

    if (isNaN(newLat) || isNaN(newLon)) {
      setError('Please enter valid coordinates')
      return
    }

    if (newLat < -90 || newLat > 90 || newLon < -180 || newLon > 180) {
      setError('Coordinates out of valid range')
      return
    }

    setError(null)
    onChange(newLat, newLon)
  }

  const handleKnownLocation = (location: { lat: number; lon: number }) => {
    setManualLat(location.lat.toString())
    setManualLon(location.lon.toString())
    onChange(location.lat, location.lon)
    setError(null)
  }

  return (
    <Box>
      {/* GPS Location */}
      <Box mb={3}>
        <Button
          variant="outlined"
          startIcon={<GPSIcon />}
          onClick={handleGPSLocation}
          disabled={gpsLoading}
          fullWidth
        >
          {gpsLoading ? 'Getting your location...' : 'Use My Current Location'}
        </Button>
      </Box>

      {/* Manual Coordinates */}
      <Box mb={3}>
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Enter Coordinates
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={5}>
            <TextField
              label="Latitude"
              value={manualLat}
              onChange={(e) => setManualLat(e.target.value)}
              fullWidth
              size="small"
              placeholder="-13.9833"
            />
          </Grid>
          <Grid item xs={5}>
            <TextField
              label="Longitude"
              value={manualLon}
              onChange={(e) => setManualLon(e.target.value)}
              fullWidth
              size="small"
              placeholder="33.7833"
            />
          </Grid>
          <Grid item xs={2}>
            <Button
              variant="contained"
              onClick={handleManualUpdate}
              fullWidth
              size="small"
            >
              Set
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Known Locations */}
      <Box mb={2}>
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Quick Locations
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1}>
          {knownLocations.map((location) => (
            <Chip
              key={location.name}
              label={location.name}
              onClick={() => handleKnownLocation(location)}
              clickable
              variant="outlined"
              icon={<LocationIcon />}
              sx={{
                '&:hover': {
                  backgroundColor: 'primary.50',
                },
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Coordinate Format Help */}
      <Box mt={2} p={2} bgcolor="grey.50" borderRadius={1}>
        <Typography variant="caption" color="text.secondary">
          <strong>Supported formats:</strong> Decimal degrees (-13.9833, 33.7833), 
          Named locations (Lilongwe, Area 1), or use GPS for automatic detection.
        </Typography>
      </Box>
    </Box>
  )
}

export default LocationPicker