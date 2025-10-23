import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  IconButton,
  Paper,
  Button,
} from '@mui/material'
import {
  Schedule as ScheduleIcon,
  TrendingUp as YieldIcon,
  WaterDrop as WaterIcon,
  BugReport as BugIcon,
  Compare as CompareIcon,
  CheckCircle as CheckCircleIcon,
  Agriculture as AgricultureIcon,
} from '@mui/icons-material'
import { createSlug } from '../../utils/slugUtils'

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
  // Additional fields from our database
  type?: string
  planting_months?: string
  harvest_months?: string
  min_rainfall_mm?: number
  max_rainfall_mm?: number
  optimal_temperature_min?: number
  optimal_temperature_max?: number
  spacing_requirements?: string
  fertilizer_requirements?: string
  pest_management?: string
  disease_management?: string
  harvesting_guidelines?: string
  storage_requirements?: string
  seed_rate_per_hectare?: number
  expected_yield_per_hectare?: number
  market_preference?: string
  seed_availability?: string
  cost_per_kg?: number
}

interface CompactVarietyCardProps {
  variety: Variety
  isSelected?: boolean
  compareMode?: boolean
  onSelect?: () => void
  locationSpecific?: boolean
  cropName?: string
}

const CompactVarietyCard: React.FC<CompactVarietyCardProps> = ({
  variety,
  isSelected = false,
  compareMode = false,
  onSelect,
  locationSpecific = false,
  cropName = 'unknown',
}) => {
  const navigate = useNavigate()

  // Handle card click to navigate to detail page
  const handleCardClick = () => {
    // Create URL-safe slugs for both variety and crop names
    const varietySlug = createSlug(variety.name)
    const cropSlug = createSlug(cropName)
    const url = `/varieties/${cropSlug}/${varietySlug}`
    
    console.log('🔍 CompactVarietyCard - Navigation debug:', {
      varietyName: variety.name,
      varietySlug,
      cropName,
      cropSlug,
      url
    })
    
    navigate(url)
  }

  return (
    <Card 
      onClick={handleCardClick}
      sx={{ 
        height: '100%',
        border: isSelected ? 2 : 1,
        borderColor: isSelected ? 'primary.main' : 'divider',
        position: 'relative',
        transition: 'all 0.2s ease-in-out',
        cursor: 'pointer',
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

      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Variety Header */}
        <Box mb={1.5}>
          <Typography variant="h6" component="h3" gutterBottom sx={{ fontWeight: 'bold', fontSize: '1.1rem' }}>
            {variety.name}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {variety.type && (
              <Chip 
                label={variety.type} 
                size="small" 
                color="primary" 
                variant="outlined" 
              />
            )}
            {locationSpecific && (
              <Chip
                label="📍 Location-specific"
                size="small"
                color="info"
                variant="outlined"
              />
            )}
          </Box>
        </Box>

        {/* Compact Production Overview */}
        <Paper elevation={0} sx={{ p: 1.5, mb: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ fontSize: '0.9rem' }}>
            Production Overview
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <ScheduleIcon color="primary" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Maturity
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" sx={{ fontSize: '0.85rem' }}>
                    {variety.maturity_days} days
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <YieldIcon color="success" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Yield
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" sx={{ fontSize: '0.85rem' }}>
                    {variety.yield_potential || 'High'}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <WaterIcon color="info" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Drought
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" sx={{ fontSize: '0.85rem' }}>
                    {variety.drought_tolerance || 'Moderate'}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <BugIcon color="warning" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Disease
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" sx={{ fontSize: '0.85rem' }}>
                    {variety.disease_resistance || 'Good'}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Key Info */}
        <Box mb={1.5}>
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
            {variety.description || 'A productive variety suitable for various growing conditions.'}
          </Typography>
        </Box>

        {/* Quick Stats */}
        <Box mb={1.5}>
          <Grid container spacing={1}>
            {(variety.min_rainfall_mm || variety.max_rainfall_mm) && (
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Rainfall: {variety.min_rainfall_mm || 0}-{variety.max_rainfall_mm || 0}mm
                </Typography>
              </Grid>
            )}
            {(variety.optimal_temperature_min || variety.optimal_temperature_max) && (
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Temp: {variety.optimal_temperature_min || 0}°C-{variety.optimal_temperature_max || 0}°C
                </Typography>
              </Grid>
            )}
          </Grid>
        </Box>

        {/* View Details Button */}
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              handleCardClick()
            }}
            sx={{ minWidth: 100, fontSize: '0.8rem' }}
          >
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default CompactVarietyCard
