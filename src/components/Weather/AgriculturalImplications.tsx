import React from 'react'
import { useNavigate } from 'react-router-dom'
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
  Button,
} from '@mui/material'
import {
  Opacity as DropletsIcon,
  Warning as WarningIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  CalendarMonth as CalendarIcon,
  Agriculture as SproutIcon,
  ArrowForward as ArrowForwardIcon,
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
  const navigate = useNavigate()
  const { wet_season, dry_season, variability, extreme_events, warnings, advice } = data

  const handleSeeMore = () => {
    navigate('/crops')
  }

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
            <>
              <Grid container spacing={2}>
                {wet_season.suitable_crops.map((crop, idx) => (
                  <Grid item xs={12} md={6} lg={4} key={idx}>
                    <CropCard crop={crop} />
                  </Grid>
                ))}
              </Grid>
              
              <Box display="flex" justifyContent="center" mt={3}>
                <Button
                  variant="contained"
                  color="primary"
                  endIcon={<ArrowForwardIcon />}
                  onClick={handleSeeMore}
                  size="large"
                >
                  See More
                </Button>
              </Box>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No suitable crops identified for this season based on rainfall patterns.
            </Typography>
          )}
        </Box>

      </CardContent>
    </Card>
  )
}

export default AgriculturalImplications
