import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Schedule as ScheduleIcon,
  TrendingUp as YieldIcon,
  WaterDrop as WaterIcon,
  BugReport as BugIcon,
  Landscape as SoilIcon,
  LocationOn as LocationIcon,
  Compare as CompareIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'

interface Variety {
  name: string
  maturity_days: number
  yield_potential: string
  drought_tolerance: string
  disease_resistance: string
  planting_time: string
  description: string
  weather_requirements?: string
  soil_requirements?: string
  growing_areas?: string
}

interface VarietyDetailCardProps {
  variety: Variety
  isSelected?: boolean
  compareMode?: boolean
  onSelect?: () => void
  locationSpecific?: boolean
}

const VarietyDetailCard: React.FC<VarietyDetailCardProps> = ({
  variety,
  isSelected = false,
  compareMode = false,
  onSelect,
  locationSpecific = false,
}) => {
  const isSpecified = (value: string) => value && value !== 'Not specified'

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: isSelected ? 2 : 1,
        borderColor: isSelected ? 'primary.main' : 'divider',
        position: 'relative',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: 4,
          transform: 'translateY(-2px)',
        }
      }}
    >
      {compareMode && (
        <IconButton
          onClick={onSelect}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            bgcolor: isSelected ? 'primary.main' : 'background.paper',
            color: isSelected ? 'white' : 'text.secondary',
            '&:hover': {
              bgcolor: isSelected ? 'primary.dark' : 'action.hover',
            }
          }}
        >
          {isSelected ? <CheckCircleIcon /> : <CompareIcon />}
        </IconButton>
      )}

      <CardContent>
        {/* Variety Name and Basic Info */}
        <Box mb={2}>
          <Typography variant="h6" component="h3" gutterBottom>
            🌱 {variety.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {variety.description}
          </Typography>
          {locationSpecific && (
            <Chip
              label="📍 Location-specific"
              size="small"
              color="info"
              variant="outlined"
              sx={{ mb: 1 }}
            />
          )}
        </Box>

        {/* Key Metrics */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <ScheduleIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Maturity
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {variety.maturity_days} days
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <YieldIcon color="action" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Yield Potential
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {isSpecified(variety.yield_potential) ? variety.yield_potential : 'Variable'}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Characteristics */}
        <Box mb={2}>
          <Typography variant="subtitle2" gutterBottom>
            Key Characteristics
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <WaterIcon color="primary" fontSize="small" />
                <Typography variant="body2">
                  <strong>Drought Tolerance:</strong> {isSpecified(variety.drought_tolerance) ? variety.drought_tolerance : 'Standard'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <BugIcon color="secondary" fontSize="small" />
                <Typography variant="body2">
                  <strong>Disease Resistance:</strong> {isSpecified(variety.disease_resistance) ? variety.disease_resistance : 'Standard'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1}>
                <ScheduleIcon color="success" fontSize="small" />
                <Typography variant="body2">
                  <strong>Planting Time:</strong> {variety.planting_time}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* Additional Requirements (if specified) */}
        {(isSpecified(variety.weather_requirements) || 
          isSpecified(variety.soil_requirements) || 
          isSpecified(variety.growing_areas)) && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Growing Requirements
              </Typography>
              {isSpecified(variety.weather_requirements) && (
                <Box display="flex" alignItems="flex-start" gap={1} mb={1}>
                  <WaterIcon color="info" fontSize="small" sx={{ mt: 0.2 }} />
                  <Typography variant="body2">
                    <strong>Weather:</strong> {variety.weather_requirements}
                  </Typography>
                </Box>
              )}
              {isSpecified(variety.soil_requirements) && (
                <Box display="flex" alignItems="flex-start" gap={1} mb={1}>
                  <SoilIcon color="warning" fontSize="small" sx={{ mt: 0.2 }} />
                  <Typography variant="body2">
                    <strong>Soil:</strong> {variety.soil_requirements}
                  </Typography>
                </Box>
              )}
              {isSpecified(variety.growing_areas) && (
                <Box display="flex" alignItems="flex-start" gap={1}>
                  <LocationIcon color="success" fontSize="small" sx={{ mt: 0.2 }} />
                  <Typography variant="body2">
                    <strong>Best Areas:</strong> {variety.growing_areas}
                  </Typography>
                </Box>
              )}
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  )
}

export default VarietyDetailCard
