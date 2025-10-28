import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Paper,
  Button,
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
  ExpandMore as ExpandMoreIcon,
  Agriculture as AgricultureIcon,
  Inventory as InventoryIcon,
  Build as BuildIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  CheckCircleOutline as CheckIcon,
  Info as InfoIcon,
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

interface VarietyDetailCardProps {
  variety: Variety
  isSelected?: boolean
  compareMode?: boolean
  onSelect?: () => void
  locationSpecific?: boolean
  cropName?: string
}

// Helper function to safely display object values
const safeRenderValue = (value: any, fallback: string = 'Not specified'): string => {
  if (value === null || value === undefined) return fallback;
  
  // Handle object with text property
  if (typeof value === 'object' && value !== null && 'text' in value) {
    return value.text || fallback;
  }
  
  // Handle arrays by joining
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : fallback;
  }
  
  // Return the value as string
  return String(value);
};

const VarietyDetailCard: React.FC<VarietyDetailCardProps> = ({
  variety,
  isSelected = false,
  compareMode = false,
  onSelect,
  locationSpecific = false,
  cropName = 'unknown',
}) => {
  const navigate = useNavigate()
  const [expanded, setExpanded] = useState(false)
  const isSpecified = (value: string | number) => value && value !== 'Not specified' && value !== 0

  // Handle card click to navigate to detail page
  const handleCardClick = () => {
    const varietySlug = variety.name.toLowerCase().replace(/\s+/g, '-')
    const cropSlug = cropName.toLowerCase().replace(/\s+/g, '-')
    navigate(`/varieties/${cropSlug}/${varietySlug}`)
  }

  // Generate production timeline based on maturity days
  const getProductionTimeline = (maturityDays: number) => {
    const weeks = Math.ceil(maturityDays / 7)
    return {
      weeks,
      phases: [
        { week: 'Week 1-2', activity: 'Land preparation & Planting', icon: '🌱' },
        { week: `Week 3-${Math.max(4, weeks - 8)}`, activity: 'Growth & Maintenance', icon: '🌿' },
        { week: `Week ${Math.max(5, weeks - 7)}-${weeks - 2}`, activity: 'Flowering & Development', icon: '🌸' },
        { week: `Week ${weeks - 1}-${weeks}`, activity: 'Harvesting', icon: '🌾' },
      ]
    }
  }

  const timeline = getProductionTimeline(variety.maturity_days || 120)

  // Generate input requirements based on variety data
  const getInputRequirements = () => {
    const inputs = []
    
    if (variety.seed_rate_per_hectare) {
      inputs.push({
        category: 'Seeds',
        items: [
          `Certified seeds: ${variety.seed_rate_per_hectare}kg/hectare`,
          variety.seed_availability ? `Availability: ${variety.seed_availability}` : null,
          variety.cost_per_kg ? `Cost: MK${variety.cost_per_kg}/kg` : null,
        ].filter(Boolean)
      })
    }

    if (variety.fertilizer_requirements) {
      inputs.push({
        category: 'Fertilizers',
        items: [variety.fertilizer_requirements]
      })
    }

    if (variety.pest_management || variety.disease_management) {
      inputs.push({
        category: 'Protection',
        items: [
          variety.pest_management,
          variety.disease_management,
        ].filter(Boolean)
      })
    }

    return inputs
  }

  const inputRequirements = getInputRequirements()

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

      <CardContent>
        {/* Variety Header */}
        <Box mb={2}>
          <Typography variant="h6" component="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
            🌱 {variety.name}
          </Typography>
          {variety.type && (
            <Chip 
              label={variety.type} 
              size="small" 
              color="primary" 
              variant="outlined" 
              sx={{ mb: 1 }}
            />
          )}
          {locationSpecific && (
            <Chip
              label="📍 Location-specific"
              size="small"
              color="info"
              variant="outlined"
              sx={{ mb: 1, ml: 1 }}
            />
          )}
        </Box>

        {/* Production Overview */}
        <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: 'primary.50' }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            📊 Production Overview
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <ScheduleIcon color="primary" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Production Time
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {safeRenderValue(variety.maturity_days, '120')} days ({safeRenderValue(timeline.weeks, '17')} weeks)
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <YieldIcon color="success" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Yield Potential
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {safeRenderValue(variety.expected_yield_per_hectare) 
                      ? `${safeRenderValue(variety.expected_yield_per_hectare)} kg/ha`
                      : safeRenderValue(variety.yield_potential, 'Not specified')}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Key Characteristics */}
        <Box mb={2}>
          <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
            ⭐ Key Characteristics
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <WaterIcon color="info" fontSize="small" />
                <Typography variant="body2">
                  <strong>Drought Tolerance:</strong> {safeRenderValue(variety.drought_tolerance, 'Standard')}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <BugIcon color="warning" fontSize="small" />
                <Typography variant="body2">
                  <strong>Common diseases:</strong> {variety.disease_resistance ? (
                    typeof variety.disease_resistance === 'object' && 'items' in variety.disease_resistance
                      ? variety.disease_resistance.items?.join(', ') || safeRenderValue(variety.disease_resistance)
                      : safeRenderValue(variety.disease_resistance)
                  ) : 'No specific information available'}
                </Typography>
              </Box>
            </Grid>
            {(variety.min_rainfall_mm || variety.max_rainfall_mm) && (
              <Grid item xs={12}>
                <Box display="flex" alignItems="center" gap={1}>
                  <WaterIcon color="primary" fontSize="small" />
                  <Typography variant="body2">
                    <strong>Rainfall:</strong> {safeRenderValue(variety.min_rainfall_mm, '0')}-{safeRenderValue(variety.max_rainfall_mm, '0')}mm
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </Box>

        {/* Expandable Detailed Information */}
        <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle2" fontWeight="bold">
              📋 Detailed Production Guide
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {/* Production Timeline */}
            <Box mb={3}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                📅 Production Timeline
              </Typography>
              <List dense>
                {timeline.phases.map((phase, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Typography variant="h6">{phase.icon}</Typography>
                    </ListItemIcon>
                    <ListItemText
                      primary={safeRenderValue(phase.activity)}
                      secondary={safeRenderValue(phase.week)}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>

            {/* Input Requirements */}
            {inputRequirements.length > 0 && (
              <Box mb={3}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  🛒 Required Inputs
                </Typography>
                {inputRequirements.map((input, index) => (
                  <Box key={index} mb={2}>
                    <Typography variant="body2" fontWeight="medium" color="primary" gutterBottom>
                      {input.category}:
                    </Typography>
                    <List dense>
                      {input.items.map((item, itemIndex) => (
                        <ListItem key={itemIndex}>
                          <ListItemIcon>
                            <CheckIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={safeRenderValue(item)} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                ))}
              </Box>
            )}

            {/* Growing Requirements */}
            <Box mb={3}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                🌍 Growing Requirements
              </Typography>
              <Grid container spacing={2}>
                {variety.spacing_requirements && (
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Spacing:</strong> {variety.spacing_requirements}
                      </Typography>
                    </Alert>
                  </Grid>
                )}
                {variety.soil_requirements && (
                  <Grid item xs={12}>
                    <Alert severity="success" sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Soil:</strong> {variety.soil_requirements}
                      </Typography>
                    </Alert>
                  </Grid>
                )}
                {(variety.optimal_temperature_min || variety.optimal_temperature_max) && (
                  <Grid item xs={12}>
                    <Alert severity="warning" sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Temperature:</strong> {variety.optimal_temperature_min || 0}°C - {variety.optimal_temperature_max || 0}°C
                      </Typography>
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </Box>

            {/* Harvesting & Storage */}
            {(variety.harvesting_guidelines || variety.storage_requirements) && (
              <Box mb={3}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  🌾 Harvesting & Storage
                </Typography>
                {variety.harvesting_guidelines && (
                  <Alert severity="info" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>Harvesting:</strong> {variety.harvesting_guidelines}
                    </Typography>
                  </Alert>
                )}
                {variety.storage_requirements && (
                  <Alert severity="success">
                    <Typography variant="body2">
                      <strong>Storage:</strong> {variety.storage_requirements}
                    </Typography>
                  </Alert>
                )}
              </Box>
            )}

            {/* Market Information */}
            {variety.market_preference && (
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  💰 Market Information
                </Typography>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Market Preference:</strong> {variety.market_preference}
                  </Typography>
                </Alert>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Quick Action Note */}
        <Box mt={2}>
          <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
            <Typography variant="body2">
              💡 <strong>Tip:</strong> This variety is suitable for {variety.yield_potential || 'standard'} yield production. 
              {variety.maturity_days && ` Complete cycle takes ${variety.maturity_days} days.`}
            </Typography>
          </Alert>
        </Box>

        {/* View Details Button */}
        <Box mt={2} display="flex" justifyContent="center">
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              handleCardClick()
            }}
            sx={{ minWidth: 120 }}
          >
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default VarietyDetailCard
