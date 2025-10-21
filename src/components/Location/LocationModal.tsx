import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Close as CloseIcon,
} from '@mui/icons-material'
import SimplifiedLocationInput from './SimplifiedLocationInput'

interface LocationModalProps {
  open: boolean
  onClose: () => void
  onLocationChange: (lat: number, lon: number) => void
  currentLocation?: { lat: number; lon: number }
}

const LocationModal: React.FC<LocationModalProps> = ({
  open,
  onClose,
  onLocationChange,
  currentLocation
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const handleLocationChange = (lat: number, lon: number) => {
    onLocationChange(lat, lon)
    onClose() // Close modal after location is set
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: isMobile ? 0 : 2,
        },
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1,
      }}>
        <Box>
          <Typography variant={isMobile ? "h6" : "h5"} fontWeight="bold">
            Change Location
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Set your location for crop recommendations
          </Typography>
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ ml: 2 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ px: isMobile ? 2 : 3 }}>
        <SimplifiedLocationInput
          onLocationChange={handleLocationChange}
          currentLocation={currentLocation}
        />
      </DialogContent>
      
      <DialogActions sx={{ px: isMobile ? 2 : 3, pb: 2 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          fullWidth={isMobile}
        >
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default LocationModal
