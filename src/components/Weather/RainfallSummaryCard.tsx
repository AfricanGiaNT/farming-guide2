import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Skeleton,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  WaterDrop as RainIcon,
  CalendarToday as CalendarIcon,
  TrendingUp as TrendIcon,
} from '@mui/icons-material'

interface RainfallSummaryCardProps {
  historicalData: any
  year: number
  loading: boolean
  error: any
}

const RainfallSummaryCard: React.FC<RainfallSummaryCardProps> = ({
  historicalData,
  year,
  loading,
  error
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  if (loading) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: isMobile ? 2 : 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <RainIcon color="primary" />
            <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold">
              Previous Rainy Season
            </Typography>
          </Box>
          <Skeleton variant="rectangular" height={60} />
        </CardContent>
      </Card>
    )
  }

  if (error || !historicalData) {
    return (
      <Card sx={{ mb: 2, opacity: 0.7 }}>
        <CardContent sx={{ p: isMobile ? 2 : 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <RainIcon color="disabled" />
            <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold" color="text.secondary">
              Previous Rainy Season
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Historical rainfall data unavailable for this location
          </Typography>
        </CardContent>
      </Card>
    )
  }

  // Extract rainfall data from historical data with proper validation
  const monthlyAverages = Array.isArray(historicalData.monthly_averages) 
    ? historicalData.monthly_averages 
    : []
  
  const rainySeasonMonths = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr']
  
  // Calculate total rainfall for rainy season months
  const rainySeasonRainfall = monthlyAverages
    .filter((month: any) => month && month.month && rainySeasonMonths.includes(month.month))
    .reduce((total: number, month: any) => total + (month.rainfall || 0), 0)

  const seasonPeriod = `${year} Rainy Season`
  const periodRange = `Nov ${year} - Apr ${year + 1}`

  // If no rainfall data available, show fallback
  if (rainySeasonRainfall === 0 && monthlyAverages.length === 0) {
    return (
      <Card sx={{ mb: 2, opacity: 0.7 }}>
        <CardContent sx={{ p: isMobile ? 2 : 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <RainIcon color="disabled" />
            <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold" color="text.secondary">
              Previous Rainy Season
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            No rainfall data available for {year} rainy season
          </Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent sx={{ p: isMobile ? 2 : 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <RainIcon color="primary" />
          <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold">
            Previous Rainy Season
          </Typography>
        </Box>
        
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box>
            <Typography variant={isMobile ? "h5" : "h4"} fontWeight="bold" color="primary.main">
              {rainySeasonRainfall.toFixed(0)}mm
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total Rainfall
            </Typography>
          </Box>
          
          <Box textAlign="right">
            <Chip
              icon={<CalendarIcon />}
              label={seasonPeriod}
              color="primary"
              variant="outlined"
              size={isMobile ? "small" : "medium"}
            />
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
              {periodRange}
            </Typography>
          </Box>
        </Box>

        {/* Additional context */}
        <Box display="flex" alignItems="center" gap={1} mt={2}>
          <TrendIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            Based on historical weather data for your location
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default RainfallSummaryCard
