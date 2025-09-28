import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Divider,
  Tooltip,
} from '@mui/material'
import {
  Agriculture as CropIcon,
  Star as StarIcon,
  TrendingUp as TrendIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  WaterDrop as WaterIcon,
  Thermostat as TempIcon,
  CalendarToday as CalendarIcon,
  Source as SourceIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface CropRecommendation {
  crop_name: string
  suitability_score: number
  score: number
  suitability_level: 'excellent' | 'very_good' | 'good' | 'fair' | 'poor'
  rainfall_match: 'excellent' | 'good' | 'fair' | 'poor'
  temperature_match: 'excellent' | 'good' | 'fair' | 'poor'
  season_suitability: 'excellent' | 'good' | 'fair' | 'poor'
  sources: string[]
  guide_recommendations: string[]
  varieties?: string[]
  planting_time?: string
  yield_potential?: string
  description?: string
}

interface CropRecommendationCardProps {
  crop: CropRecommendation
  onClick: () => void
}

const CropRecommendationCard: React.FC<CropRecommendationCardProps> = ({
  crop,
  onClick,
}) => {
  const [expanded, setExpanded] = useState(false)

  const getSuitabilityColor = (level: string) => {
    switch (level) {
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

  const getMatchColor = (level: string) => {
    switch (level) {
      case 'excellent':
        return 'success'
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

  const getMatchEmoji = (level: string) => {
    switch (level) {
      case 'excellent':
        return '🟢'
      case 'good':
        return '🟡'
      case 'fair':
        return '🟠'
      case 'poor':
        return '🔴'
      default:
        return '⚪'
    }
  }

  const getCropEmoji = (cropName: string) => {
    const name = cropName.toLowerCase()
    if (name.includes('maize') || name.includes('corn')) return '🌽'
    if (name.includes('bean')) return '🫘'
    if (name.includes('groundnut') || name.includes('peanut')) return '🥜'
    if (name.includes('cassava')) return '🍠'
    if (name.includes('sweet potato')) return '🍠'
    if (name.includes('sorghum')) return '🌾'
    if (name.includes('soybean')) return '🫘'
    return '🌱'
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        sx={{
          cursor: 'pointer',
          height: '100%',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 8,
            transform: 'translateY(-2px)',
          },
        }}
        onClick={onClick}
      >
        <CardContent sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h4" component="span">
                {getCropEmoji(crop.crop_name)}
              </Typography>
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {crop.crop_name}
                </Typography>
                {crop.description && (
                  <Typography variant="caption" color="text.secondary">
                    {crop.description}
                  </Typography>
                )}
              </Box>
            </Box>
            
            <IconButton 
              size="small" 
              color="primary"
              onClick={(e) => {
                e.stopPropagation()
                setExpanded(!expanded)
              }}
            >
              {expanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
            </IconButton>
          </Box>

          {/* Score Display */}
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight="bold">
                Suitability Score
              </Typography>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {Math.round(crop.score)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={crop.score}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                },
              }}
            />
          </Box>

          {/* Match Indicators */}
          <Box display="flex" gap={1} mb={2} flexWrap="wrap">
            <Tooltip title="Rainfall Match">
              <Chip
                icon={<WaterIcon />}
                label={`${getMatchEmoji(crop.rainfall_match)} Rain`}
                color={getMatchColor(crop.rainfall_match) as any}
                size="small"
                variant="outlined"
              />
            </Tooltip>
            <Tooltip title="Temperature Match">
              <Chip
                icon={<TempIcon />}
                label={`${getMatchEmoji(crop.temperature_match)} Temp`}
                color={getMatchColor(crop.temperature_match) as any}
                size="small"
                variant="outlined"
              />
            </Tooltip>
            <Tooltip title="Season Suitability">
              <Chip
                icon={<CalendarIcon />}
                label={`${getMatchEmoji(crop.season_suitability)} Season`}
                color={getMatchColor(crop.season_suitability) as any}
                size="small"
                variant="outlined"
              />
            </Tooltip>
          </Box>

          {/* Suitability Level */}
          <Box display="flex" gap={1} mb={2}>
            <Chip
              label={crop.suitability_level.replace('_', ' ')}
              color={getSuitabilityColor(crop.suitability_level) as any}
              size="small"
              variant="filled"
            />
            {crop.sources && crop.sources.length > 0 && (
              <Tooltip title={`Sources: ${crop.sources.join(', ')}`}>
                <Chip
                  icon={<SourceIcon />}
                  label={`${crop.sources.length} source${crop.sources.length > 1 ? 's' : ''}`}
                  size="small"
                  variant="outlined"
                />
              </Tooltip>
            )}
          </Box>

          {/* Basic Info */}
          <Box display="flex" gap={2} mb={2}>
            {crop.planting_time && (
              <Typography variant="body2" color="text.secondary">
                <CalendarIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                {crop.planting_time}
              </Typography>
            )}
            {crop.yield_potential && (
              <Typography variant="body2" color="text.secondary">
                <TrendIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                {crop.yield_potential}
              </Typography>
            )}
          </Box>

          {/* Varieties */}
          {crop.varieties && crop.varieties.length > 0 && (
            <Box mb={2}>
              <Typography variant="body2" fontWeight="bold" gutterBottom>
                Recommended Varieties:
              </Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap">
                {crop.varieties.slice(0, 3).map((variety, index) => (
                  <Chip
                    key={index}
                    label={variety}
                    size="small"
                    variant="outlined"
                    color="primary"
                  />
                ))}
                {crop.varieties.length > 3 && (
                  <Chip
                    label={`+${crop.varieties.length - 3} more`}
                    size="small"
                    variant="outlined"
                    color="default"
                  />
                )}
              </Box>
            </Box>
          )}

          {/* Expandable Details */}
          <Collapse in={expanded}>
            <Divider sx={{ my: 2 }} />
            
            {/* Guide Recommendations */}
            {crop.guide_recommendations && crop.guide_recommendations.length > 0 && (
              <Box mb={2}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Guide Recommendations:
                </Typography>
                <List dense>
                  {crop.guide_recommendations.slice(0, 3).map((rec, index) => (
                    <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={rec}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Sources */}
            {crop.sources && crop.sources.length > 0 && (
              <Box>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Sources:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {crop.sources.join(', ')}
                </Typography>
              </Box>
            )}
          </Collapse>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default CropRecommendationCard