import React from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Paper,
} from '@mui/material'
import {
  TrendingUp as TrendIcon,
  WbSunny as CurrentIcon,
  Grain as RainyIcon,
  WbSunnyOutlined as DryIcon,
} from '@mui/icons-material'

interface SeasonalData {
  season: string
  recommendations: Array<{
    cropName: string
    totalScore: number
    suitabilityLevel: string
  }>
  environmentalSummary: {
    estimatedSeasonalRainfall: number
    currentTemperature: number
    currentSeason: string
  }
}

interface SeasonalComparisonProps {
  data: {
    seasonComparison?: {
      rainy_season: SeasonalData
      dry_season: SeasonalData
      current_season: SeasonalData
    }
    recommendations?: Array<{
      cropName: string
      seasonScores: {
        rainy: number
        dry: number
        current: number
      }
    }>
  } | null
}

const SeasonalComparison: React.FC<SeasonalComparisonProps> = ({ data }) => {
  if (!data) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            Seasonal comparison data unavailable
          </Typography>
        </CardContent>
      </Card>
    )
  }

  const getSuitabilityColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'excellent':
        return 'success'
      case 'very_good':
        return 'primary'
      case 'good':
        return 'info'
      case 'fair':
        return 'warning'
      case 'poor':
        return 'error'
      default:
        return 'default'
    }
  }

  const getSeasonIcon = (season: string) => {
    switch (season) {
      case 'rainy_season':
        return RainyIcon
      case 'dry_season':
        return DryIcon
      default:
        return CurrentIcon
    }
  }

  const seasonData = data.seasonComparison
  const yearRoundCrops = data.recommendations || []

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        Seasonal Comparison
      </Typography>

      {/* Season Overview Cards */}
      {seasonData && (
        <Grid container spacing={3} mb={4}>
          {Object.entries(seasonData).map(([seasonKey, season]) => {
            const Icon = getSeasonIcon(seasonKey)
            const seasonName = seasonKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
            
            return (
              <Grid item xs={12} md={4} key={seasonKey}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      <Icon color="primary" />
                      <Typography variant="h6" fontWeight="bold">
                        {seasonName}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Rainfall: {season.environmentalSummary.estimatedSeasonalRainfall}mm
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Top Crops:
                    </Typography>
                    
                    <Box display="flex" flexDirection="column" gap={1}>
                      {season.recommendations.slice(0, 3).map((crop, index) => (
                        <Box key={index} display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">
                            {index + 1}. {crop.cropName}
                          </Typography>
                          <Chip
                            label={`${crop.totalScore}/125`}
                            color={getSuitabilityColor(crop.suitabilityLevel) as any}
                            size="small"
                          />
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      )}

      {/* Year-Round Crop Performance Table */}
      {yearRoundCrops.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <TrendIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Year-Round Crop Performance
              </Typography>
            </Box>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Compare how different crops perform across all seasons
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Crop</strong></TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                        <RainyIcon fontSize="small" />
                        <strong>Rainy</strong>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                        <DryIcon fontSize="small" />
                        <strong>Dry</strong>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                        <CurrentIcon fontSize="small" />
                        <strong>Current</strong>
                      </Box>
                    </TableCell>
                    <TableCell align="center"><strong>Average</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {yearRoundCrops.slice(0, 8).map((crop) => {
                    const avgScore = (crop.seasonScores.rainy + crop.seasonScores.dry + crop.seasonScores.current) / 3
                    
                    return (
                      <TableRow key={crop.cropName} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {crop.cropName}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={crop.seasonScores.rainy}
                            color={crop.seasonScores.rainy > 80 ? 'success' : crop.seasonScores.rainy > 60 ? 'primary' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={crop.seasonScores.dry}
                            color={crop.seasonScores.dry > 80 ? 'success' : crop.seasonScores.dry > 60 ? 'primary' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={crop.seasonScores.current}
                            color={crop.seasonScores.current > 80 ? 'success' : crop.seasonScores.current > 60 ? 'primary' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={avgScore.toFixed(0)}
                            color={avgScore > 80 ? 'success' : avgScore > 60 ? 'primary' : 'default'}
                            size="small"
                            variant="filled"
                          />
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default SeasonalComparison