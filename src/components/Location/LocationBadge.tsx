import React from 'react'
import {
  Box,
  Chip,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  MyLocation as GPSIcon,
  Edit as EditIcon,
} from '@mui/icons-material'

interface LocationBadgeProps {
  lat: number
  lon: number
  onEdit: () => void
  disabled?: boolean
}

const LocationBadge: React.FC<LocationBadgeProps> = ({
  lat,
  lon,
  onEdit,
  disabled = false
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const formatCoordinates = (lat: number, lon: number) => {
    if (isMobile) {
      return `${lat.toFixed(2)}, ${lon.toFixed(2)}`
    }
    return `${lat.toFixed(4)}, ${lon.toFixed(4)}`
  }

  return (
    <Box display="flex" alignItems="center" gap={1} mb={2}>
      <Chip
        icon={<GPSIcon />}
        label={formatCoordinates(lat, lon)}
        color="primary"
        variant="outlined"
        size={isMobile ? "small" : "medium"}
        sx={{
          fontSize: isMobile ? '0.75rem' : '0.875rem',
          fontWeight: 'bold',
        }}
      />
      
      <IconButton
        size="small"
        onClick={onEdit}
        disabled={disabled}
        sx={{
          color: 'primary.main',
          '&:hover': {
            backgroundColor: 'primary.50',
          },
        }}
      >
        <EditIcon fontSize="small" />
      </IconButton>
      
      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
        Tap to change location
      </Typography>
    </Box>
  )
}

export default LocationBadge
