import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Alert,
  Chip,
  Divider,
  Paper,
} from '@mui/material'
import {
  Opacity as DropletsIcon,
  Warning as WarningIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  CalendarMonth as CalendarIcon,
  Agriculture as SproutIcon,
} from '@mui/icons-material'

interface CropRecommendation {
  crop_name: string
  local_name: string
  water_requirement: 'low' | 'medium' | 'high'
  planting_months: string[]
  days_to_harvest: number
  min_rainfall_mm: number
  max_rainfall_mm: number
  optimal_rainfall_mm: number
  notes?: string
  match_score: number
}

interface SeasonData {
  months: string[]
  average_monthly_rainfall_mm: number
  total_season_rainfall_mm: number
  suitable_crops: CropRecommendation[]
}

interface Variability {
  percentage: number
  level: 'Low' | 'Medium' | 'High'
  interpretation: string
  coefficient_of_variation: number
}

interface ExtremeEvents {
  drought_years: number
  drought_year_list: number[]
  flood_years: number
  flood_year_list: number[]
  total_years_analyzed: number
  drought_threshold_mm: number
  flood_threshold_mm: number
}

interface AgriculturalImplicationsData {
  wet_season: SeasonData
  dry_season: SeasonData
  variability: Variability
  extreme_events: ExtremeEvents
  warnings: string[]
  advice: string[]
  years_analyzed: number
}

interface AgriculturalImplicationsProps {
  data: AgriculturalImplicationsData
}

const AgriculturalImplications: React.FC<AgriculturalImplicationsProps> = ({ data }) => {
  const { wet_season, dry_season, variability, extreme_events, warnings, advice } = data

  const getVariabilityColor = (level: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (level) {
      case 'Low':
        return 'success'
      case 'Medium':
        return 'warning'
      case 'High':
        return 'error'
      default:
        return 'default'
    }
  }

  const getWaterRequirementColor = (requirement: string): 'info' | 'primary' | 'secondary' => {
    switch (requirement) {
      case 'low':
        return 'info'
      case 'medium':
        return 'primary'
      case 'high':
        return 'secondary'
      default:
        return 'info'
    }
  }

  const CropCard = ({ crop }: { crop: CropRecommendation }) => (
    <Paper elevation={1} sx={{ p: 2, height: '100%', '&:hover': { boxShadow: 3 } }}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
        <Box>
          <Typography variant="subtitle1" fontWeight="bold">{crop.crop_name}</Typography>
          {crop.local_name && (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              ({crop.local_name})
            </Typography>
          )}
        </Box>
        <Chip
          label={crop.water_requirement}
          color={getWaterRequirementColor(crop.water_requirement)}
          size="small"
        />
      </Box>
      
      <Box sx={{ mt: 2 }}>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <CalendarIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            <strong>Plant:</strong> {crop.planting_months.slice(0, 3).join(', ')}
            {crop.planting_months.length > 3 && '...'}
          </Typography>
        </Box>
        
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <TrendingUpIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            <strong>Harvest:</strong> {crop.days_to_harvest} days
          </Typography>
        </Box>
        
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <DropletsIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            <strong>Rainfall:</strong> {crop.min_rainfall_mm}-{crop.max_rainfall_mm}mm
          </Typography>
        </Box>
        
        {crop.notes && (
          <Alert severity="warning" sx={{ mt: 1, py: 0.5, '& .MuiAlert-message': { fontSize: '0.75rem' } }}>
            {crop.notes}
          </Alert>
        )}
      </Box>
    </Paper>
  )

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <SproutIcon sx={{ fontSize: 32, color: 'success.main' }} />
          <Typography variant="h5" fontWeight="bold">
            Agricultural Implications
          </Typography>
        </Box>

        {/* Rainfall Variability */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <TrendingUpIcon sx={{ fontSize: 24 }} />
            <Typography variant="h6" fontWeight="bold">
              Climate Variability
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={2}>
            <Chip
              label={`${variability.level} Variability`}
              color={getVariabilityColor(variability.level)}
              sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
            />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                {variability.percentage}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {variability.interpretation}
              </Typography>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Extreme Events */}
        <Box mb={3}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Extreme Events
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light' }}>
                <Typography variant="h3" fontWeight="bold" color="warning.dark">
                  {extreme_events.drought_years}
                </Typography>
                <Typography variant="body2" color="warning.dark">
                  Drought Years
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'info.light' }}>
                <Typography variant="h3" fontWeight="bold" color="info.dark">
                  {extreme_events.flood_years}
                </Typography>
                <Typography variant="body2" color="info.dark">
                  Flood Years
                </Typography>
              </Paper>
            </Grid>
          </Grid>
          <Typography variant="caption" display="block" textAlign="center" mt={1} color="text.secondary">
            Based on {extreme_events.total_years_analyzed} years of data
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Wet Season Crops */}
        <Box mb={3}>
          <Typography variant="h6" fontWeight="bold" color="primary.main" mb={1}>
            🌧️ Wet Season: Suitable Crops
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            <strong>Months:</strong> {wet_season.months.join(', ')} • 
            <strong> Avg Rainfall:</strong> {Math.round(wet_season.average_monthly_rainfall_mm)}mm/month
          </Typography>
          {wet_season.suitable_crops && wet_season.suitable_crops.length > 0 ? (
            <Grid container spacing={2}>
              {wet_season.suitable_crops.map((crop, idx) => (
                <Grid item xs={12} md={6} lg={4} key={idx}>
                  <CropCard crop={crop} />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No suitable crops identified for this season based on rainfall patterns.
            </Typography>
          )}
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Dry Season Crops */}
        <Box mb={3}>
          <Typography variant="h6" fontWeight="bold" sx={{ color: 'orange' }} mb={1}>
            ☀️ Dry Season: Suitable Crops
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            <strong>Months:</strong> {dry_season.months.join(', ')} • 
            <strong> Avg Rainfall:</strong> {Math.round(dry_season.average_monthly_rainfall_mm)}mm/month
          </Typography>
          {dry_season.suitable_crops && dry_season.suitable_crops.length > 0 ? (
            <Grid container spacing={2}>
              {dry_season.suitable_crops.map((crop, idx) => (
                <Grid item xs={12} md={6} lg={4} key={idx}>
                  <CropCard crop={crop} />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              Limited rainfall for dry season cropping. Irrigation may be required.
            </Typography>
          )}
        </Box>

        {/* Warnings */}
        {warnings && warnings.length > 0 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <WarningIcon color="error" />
                <Typography variant="h6" fontWeight="bold" color="error.main">
                  Warnings
                </Typography>
              </Box>
              {warnings.map((warning, idx) => (
                <Alert key={idx} severity="error" sx={{ mb: 1 }}>
                  {warning}
                </Alert>
              ))}
            </Box>
          </>
        )}

        {/* Advice */}
        {advice && advice.length > 0 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <LightbulbIcon color="success" />
                <Typography variant="h6" fontWeight="bold" color="success.main">
                  Recommendations
                </Typography>
              </Box>
              <Box component="ul" sx={{ pl: 2 }}>
                {advice.map((item, idx) => (
                  <Box component="li" key={idx} sx={{ mb: 1 }}>
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  )
}

export default AgriculturalImplications
