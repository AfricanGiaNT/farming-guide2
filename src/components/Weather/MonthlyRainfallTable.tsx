import React from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  useTheme,
  useMediaQuery,
  LinearProgress,
  Tooltip,
} from '@mui/material'
import {
  Cloud as RainIcon,
  TrendingUp as TrendIcon,
  TrendingDown as DownTrendIcon,
  WaterDrop as DropIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'

interface MonthlyRainfallData {
  average_rainfall: number
  min_rainfall: number
  max_rainfall: number
  average_temperature: number
  years_analyzed: number
}

interface HistoricalData {
  monthly_averages: Record<string, MonthlyRainfallData>
  climate_summary: {
    total_annual_rainfall: number
    wettest_month: string
    driest_month: string
    climate_trend: string
    drought_risk: string
    analysis_period: string
  }
  years_analyzed: number
  location: string
  timestamp: string
  mock_data?: boolean
  per_year?: Array<{ year: number; annual_rainfall: number; monthly: Record<string, number>; months_covered?: number; coverage?: 'full' | 'partial' }>
  multi_year?: { annual_average: number; monthly_average: Record<string, number> }
}

interface MonthlyRainfallTableProps {
  historical: HistoricalData | null
  loading?: boolean
}

const MonthlyRainfallTable: React.FC<MonthlyRainfallTableProps> = ({ 
  historical, 
  loading = false 
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Loading monthly rainfall data...
        </Typography>
      </Box>
    )
  }

  if (!historical) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Real historical data unavailable
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          We only use real weather data. Please check your internet connection and API configuration.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          The system is configured to use real data only - no mock data fallbacks.
        </Typography>
      </Box>
    )
  }

  if (!historical.monthly_averages) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Monthly averages data unavailable
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Available keys: {Object.keys(historical).join(', ')}
        </Typography>
      </Box>
    )
  }

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  // Calculate average rainfall for trend analysis
  const monthlyRainfallValues = months.map(month => 
    historical.monthly_averages[month]?.average_rainfall || 0
  )
  const averageRainfall = monthlyRainfallValues.reduce((sum, val) => sum + val, 0) / 12

  const getRainfallLevel = (rainfall: number): { level: string; color: 'success' | 'warning' | 'error' | 'info' } => {
    if (rainfall >= 100) return { level: 'High', color: 'success' }
    if (rainfall >= 50) return { level: 'Moderate', color: 'info' }
    if (rainfall >= 20) return { level: 'Low', color: 'warning' }
    return { level: 'Very Low', color: 'error' }
  }

  const getCardBackground = (rainfallLevel: { level: string; color: 'success' | 'warning' | 'error' | 'info' }) => {
    switch (rainfallLevel.color) {
      case 'success':
        return 'linear-gradient(135deg, rgba(56, 142, 60, 0.4) 0%, rgba(76, 175, 80, 0.5) 50%, rgba(56, 142, 60, 0.4) 100%)'
      case 'info':
        return 'linear-gradient(135deg, rgba(25, 118, 210, 0.4) 0%, rgba(33, 150, 243, 0.5) 50%, rgba(25, 118, 210, 0.4) 100%)'
      case 'warning':
        return 'linear-gradient(135deg, rgba(230, 126, 34, 0.4) 0%, rgba(255, 152, 0, 0.5) 50%, rgba(230, 126, 34, 0.4) 100%)'
      case 'error':
        return 'linear-gradient(135deg, rgba(211, 47, 47, 0.4) 0%, rgba(244, 67, 54, 0.5) 50%, rgba(211, 47, 47, 0.4) 100%)'
      default:
        return 'linear-gradient(135deg, rgba(97, 97, 97, 0.3) 0%, rgba(158, 158, 158, 0.4) 50%, rgba(97, 97, 97, 0.3) 100%)'
    }
  }

  const getTrendIcon = (month: string) => {
    const rainfall = historical.monthly_averages[month]?.average_rainfall || 0
    if (rainfall > averageRainfall * 1.2) {
      return <TrendIcon color="success" fontSize="small" />
    } else if (rainfall < averageRainfall * 0.8) {
      return <DownTrendIcon color="error" fontSize="small" />
    }
    return null
  }

  const isWettestMonth = (month: string) => month === historical.climate_summary.wettest_month
  const isDriestMonth = (month: string) => month === historical.climate_summary.driest_month

  // Find the maximum rainfall for progress bar scaling
  const maxRainfall = Math.max(...monthlyRainfallValues)

  return (
    <Box sx={{ width: '100%' }}>
      {/* Annual Rainfall Display - Compact */}
      <Card 
        sx={{ 
          mb: 2, 
          bgcolor: 'primary.main', 
          color: 'primary.contrastText',
          borderRadius: 2,
          textAlign: 'center'
        }}
      >
        <CardContent sx={{ py: isMobile ? 1.5 : 2 }}>
          <Typography variant={isMobile ? "h4" : "h3"} fontWeight="bold" gutterBottom>
            {(historical.multi_year?.annual_average ?? historical.climate_summary.total_annual_rainfall).toFixed(0)} mm
          </Typography>
          <Typography variant={isMobile ? "body1" : "h6"} sx={{ opacity: 0.9 }}>
            Annual Rainfall ({historical.years_analyzed} year{historical.years_analyzed > 1 ? 's' : ''} average)
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8, mt: 1, display: 'block' }}>
            {historical.climate_summary.analysis_period}
          </Typography>
        </CardContent>
      </Card>

      {/* Per-Year Accordions */}
      {Array.isArray(historical.per_year) && historical.per_year.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant={isMobile ? "h6" : "h5"} gutterBottom fontWeight="bold" sx={{ mb: 1 }}>
            Yearly Breakdown
          </Typography>
          {historical.per_year.map((yearItem, idx) => (
            <Accordion key={yearItem.year} defaultExpanded={idx === 0}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                  <Typography variant={isMobile ? "subtitle1" : "h6"} fontWeight="bold">
                    {yearItem.year}
                  </Typography>
                  <Typography variant={isMobile ? "subtitle2" : "subtitle1"}>
                    {yearItem.annual_rainfall.toFixed(0)} mm
                  </Typography>
                  {yearItem.coverage === 'partial' && (
                    <Chip size="small" label={`Partial (${yearItem.months_covered || 0}/12)`} color="warning" sx={{ ml: 1 }} />
                  )}
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={isMobile ? 1 : 1.5}>
                  {months.map(m => {
                    const val = yearItem.monthly[m] || 0
                    const level = getRainfallLevel(val)
                    const progressValue = val > 0 ? Math.min(100, (val / 250) * 100) : 0 // simple scale per month card
                    return (
                      <Grid item xs={4} sm={3} md={2} key={`${yearItem.year}-${m}`}>
                        <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
                          <CardContent sx={{ p: isMobile ? 1 : 1.5, '&:last-child': { pb: isMobile ? 1 : 1.5 } }}>
                            <Box display="flex" alignItems="center" justifyContent="space-between" mb={0.5}>
                              <Typography variant={isMobile ? 'caption' : 'subtitle2'} fontWeight="bold">
                                {m.slice(0,3)}
                              </Typography>
                            </Box>
                            <Typography variant={isMobile ? 'body2' : 'subtitle1'} fontWeight="bold" gutterBottom>
                              {val.toFixed(1)} mm
                            </Typography>
                            <Box mb={0.5}>
                              <LinearProgress 
                                variant="determinate" 
                                value={progressValue}
                                sx={{ height: 4, borderRadius: 2 }}
                              />
                            </Box>
                            <Chip label={level.level} color={level.color} size="small" variant="outlined" />
                          </CardContent>
                        </Card>
                      </Grid>
                    )
                  })}
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {/* Monthly Rainfall Grid - Compact Cards */}
      <Typography variant={isMobile ? "h6" : "h5"} gutterBottom fontWeight="bold" sx={{ mb: 2 }}>
        Monthly Rainfall Breakdown
      </Typography>

      <Grid container spacing={isMobile ? 1 : 1.5}>
        {months.map((month, index) => {
          const monthData = historical.monthly_averages[month]
          const rainfall = monthData?.average_rainfall || 0
          const minRainfall = monthData?.min_rainfall || 0
          const maxRainfall = monthData?.max_rainfall || 0
          const rainfallLevel = getRainfallLevel(rainfall)
          const trendIcon = getTrendIcon(month)
          const progressValue = maxRainfall > 0 ? (rainfall / maxRainfall) * 100 : 0

          return (
            <Grid item xs={4} sm={3} md={2} key={month}>
              <Card 
                sx={{ 
                  height: '100%',
                  border: isWettestMonth(month) ? '2px solid' : isDriestMonth(month) ? '2px solid' : '1px solid',
                  borderColor: isWettestMonth(month) ? 'success.main' : isDriestMonth(month) ? 'error.main' : 'divider',
                  background: getCardBackground(rainfallLevel),
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3,
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: `
                      repeating-linear-gradient(
                        45deg,
                        transparent,
                        transparent 3px,
                        rgba(255, 255, 255, 0.02) 3px,
                        rgba(255, 255, 255, 0.02) 6px
                      ),
                      radial-gradient(
                        ellipse at center,
                        rgba(255, 255, 255, 0.05) 0%,
                        transparent 70%
                      )
                    `,
                    pointerEvents: 'none',
                  }
                }}
              >
                <CardContent sx={{ p: isMobile ? 1 : 1.5, '&:last-child': { pb: isMobile ? 1 : 1.5 } }}>
                  {/* Month Header */}
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={0.5}>
                    <Typography 
                      variant={isMobile ? "caption" : "subtitle2"}
                      fontWeight="bold" 
                      sx={{
                        color: 'black',
                        textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)',
                      }}
                    >
                      {month.slice(0, 3)}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={0.5}>
                      {trendIcon}
                      {isWettestMonth(month) && (
                        <Tooltip title="Wettest Month">
                          <DropIcon color="success" fontSize="small" />
                        </Tooltip>
                      )}
                      {isDriestMonth(month) && (
                        <Tooltip title="Driest Month">
                          <DropIcon color="error" fontSize="small" />
                        </Tooltip>
                      )}
                    </Box>
                  </Box>

                  {/* Rainfall Amount */}
                  <Typography 
                    variant={isMobile ? "body1" : "h6"}
                    fontWeight="bold" 
                    sx={{
                      color: 'black',
                      textShadow: '0 1px 3px rgba(255, 255, 255, 0.5)',
                      filter: 'drop-shadow(0 1px 2px rgba(255, 255, 255, 0.3))',
                    }}
                    gutterBottom
                  >
                    {rainfall.toFixed(1)} mm
                  </Typography>

                  {/* Progress Bar */}
                  <Box mb={0.5}>
                    <LinearProgress 
                      variant="determinate" 
                      value={progressValue}
                      sx={{
                        height: 4,
                        borderRadius: 2,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: rainfallLevel.color === 'success' ? 'success.main' : 
                                  rainfallLevel.color === 'warning' ? 'warning.main' :
                                  rainfallLevel.color === 'error' ? 'error.main' : 'primary.main',
                        }
                      }}
                    />
                  </Box>

                  {/* Level Badge */}
                  <Chip
                    label={rainfallLevel.level}
                    color={rainfallLevel.color}
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5 }}
                  />

                  {/* Range */}
                  <Typography 
                    variant="caption" 
                    display="block"
                    sx={{
                      color: 'rgba(0, 0, 0, 0.7)',
                      textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)',
                    }}
                  >
                    Range: {minRainfall.toFixed(0)}-{maxRainfall.toFixed(0)} mm
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {/* Summary Cards */}
      <Grid container spacing={isMobile ? 1 : 1.5} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6}>
          <Card 
            sx={{ 
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.4) 0%, rgba(76, 175, 80, 0.5) 50%, rgba(76, 175, 80, 0.4) 100%)',
              border: '1px solid',
              borderColor: 'success.200',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `
                  repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 3px,
                    rgba(255, 255, 255, 0.02) 3px,
                    rgba(255, 255, 255, 0.02) 6px
                  ),
                  radial-gradient(
                    ellipse at center,
                    rgba(255, 255, 255, 0.05) 0%,
                    transparent 70%
                  )
                `,
                pointerEvents: 'none',
              }
            }}
          >
            <CardContent sx={{ p: isMobile ? 1 : 1.5, position: 'relative' }}>
              <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
                <DropIcon sx={{ color: 'black' }} fontSize="small" />
                <Typography 
                  variant={isMobile ? "caption" : "subtitle2"} 
                  fontWeight="bold" 
                  sx={{ 
                    color: 'black',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  Wettest Month
                </Typography>
              </Box>
              <Typography 
                variant={isMobile ? "body1" : "h6"} 
                sx={{ 
                  color: 'black',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                }}
              >
                {historical.climate_summary.wettest_month}
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(0, 0, 0, 0.7)',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                }}
              >
                {historical.monthly_averages[historical.climate_summary.wettest_month]?.average_rainfall.toFixed(1)} mm
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <Card 
            sx={{ 
              background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.4) 0%, rgba(244, 67, 54, 0.5) 50%, rgba(244, 67, 54, 0.4) 100%)',
              border: '1px solid',
              borderColor: 'error.200',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `
                  repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 3px,
                    rgba(255, 255, 255, 0.02) 3px,
                    rgba(255, 255, 255, 0.02) 6px
                  ),
                  radial-gradient(
                    ellipse at center,
                    rgba(255, 255, 255, 0.05) 0%,
                    transparent 70%
                  )
                `,
                pointerEvents: 'none',
              }
            }}
          >
            <CardContent sx={{ p: isMobile ? 1 : 1.5, position: 'relative' }}>
              <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
                <DropIcon sx={{ color: 'black' }} fontSize="small" />
                <Typography 
                  variant={isMobile ? "caption" : "subtitle2"} 
                  fontWeight="bold" 
                  sx={{ 
                    color: 'black',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  Driest Month
                </Typography>
              </Box>
              <Typography 
                variant={isMobile ? "body1" : "h6"} 
                sx={{ 
                  color: 'black',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                }}
              >
                {historical.climate_summary.driest_month}
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(0, 0, 0, 0.7)',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                }}
              >
                {historical.monthly_averages[historical.climate_summary.driest_month]?.average_rainfall.toFixed(1)} mm
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agricultural Insights - Compact */}
      <Card 
        sx={{ 
          mt: 2, 
          background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.4) 0%, rgba(33, 150, 243, 0.5) 50%, rgba(33, 150, 243, 0.4) 100%)',
          border: '1px solid', 
          borderColor: 'primary.200',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              repeating-linear-gradient(
                45deg,
                transparent,
                transparent 3px,
                rgba(255, 255, 255, 0.02) 3px,
                rgba(255, 255, 255, 0.02) 6px
              ),
              radial-gradient(
                ellipse at center,
                rgba(255, 255, 255, 0.05) 0%,
                transparent 70%
              )
            `,
            pointerEvents: 'none',
          }
        }}
      >
        <CardContent sx={{ p: isMobile ? 1 : 1.5, position: 'relative' }}>
          <Typography 
            variant={isMobile ? "body1" : "h6"} 
            gutterBottom 
            fontWeight="bold" 
            sx={{ 
              color: 'black',
              textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
            }}
          >
            Agricultural Insights
          </Typography>
          
          <Grid container spacing={isMobile ? 1 : 1.5}>
            <Grid item xs={12} sm={6}>
              <Box>
                <Typography 
                  variant="body2" 
                  fontWeight="bold" 
                  gutterBottom
                  sx={{ 
                    color: 'black',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  Wet Season
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'rgba(0, 0, 0, 0.8)',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  {months.slice(10).concat(months.slice(0, 4)).filter(month => 
                    (historical.monthly_averages[month]?.average_rainfall || 0) > 50
                  ).join(', ')}
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Box>
                <Typography 
                  variant="body2" 
                  fontWeight="bold" 
                  gutterBottom
                  sx={{ 
                    color: 'black',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  Dry Season
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'rgba(0, 0, 0, 0.8)',
                    textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                  }}
                >
                  {months.filter(month => 
                    (historical.monthly_averages[month]?.average_rainfall || 0) <= 50
                  ).join(', ')}
                </Typography>
              </Box>
            </Grid>
          </Grid>
          
          {historical.climate_summary.climate_trend.includes('decreasing') && (
            <Box sx={{ mt: 2, p: 1, bgcolor: 'rgba(244, 67, 54, 0.2)', borderRadius: 1 }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'black',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                }}
              >
                ⚠️ Decreasing rainfall trend detected. Consider drought-resistant varieties.
              </Typography>
            </Box>
          )}
          
          <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(255, 152, 0, 0.2)', borderRadius: 1 }}>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'black',
                textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
              }}
            >
              ⚠️ High rainfall variability. Plan for both drought and excess water scenarios.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default MonthlyRainfallTable
