/**
 * EnhancedCropCard Component
 * Provides enhanced crop recommendation display with improved visual hierarchy
 * Implements Phase 3: Enhanced User Experience
 */

import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Collapse,
  Grid,
  LinearProgress,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
  Avatar
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  TrendingUp as TrendingUpIcon,
  WaterDrop as WaterDropIcon,
  Thermostat as ThermostatIcon,
  CalendarToday as CalendarIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

export interface EnhancedCropCardProps {
  crop: {
    crop_name: string
    score: number
    suitability_level: 'excellent' | 'very_good' | 'good' | 'fair' | 'poor'
    rainfall_match: 'excellent' | 'good' | 'fair' | 'poor'
    temperature_match: 'excellent' | 'good' | 'fair' | 'poor'
    season_suitability: 'excellent' | 'good' | 'fair' | 'poor'
    sources?: string[]
    guide_recommendations?: string[]
    varieties?: string[]
    planting_time?: string
    yield_potential?: string
    description?: string
    ai_summary?: string
    key_benefits?: string[]
    potential_challenges?: string[]
    actionable_steps?: string[]
    seasonal_advice?: string
    confidence_score?: number
  }
  rank?: number
  onFavorite?: (cropName: string) => void
  isFavorite?: boolean
  showDetails?: boolean
  compact?: boolean
}

const suitabilityConfig = {
  excellent: {
    color: 'success' as const,
    label: 'Excellent',
    icon: <StarIcon />,
    bgColor: 'rgba(76, 175, 80, 0.1)',
    borderColor: 'rgba(76, 175, 80, 0.3)',
  },
  very_good: {
    color: 'success' as const,
    label: 'Very Good',
    icon: <StarIcon />,
    bgColor: 'rgba(76, 175, 80, 0.08)',
    borderColor: 'rgba(76, 175, 80, 0.2)',
  },
  good: {
    color: 'info' as const,
    label: 'Good',
    icon: <CheckCircleIcon />,
    bgColor: 'rgba(33, 150, 243, 0.08)',
    borderColor: 'rgba(33, 150, 243, 0.2)',
  },
  fair: {
    color: 'warning' as const,
    label: 'Fair',
    icon: <WarningIcon />,
    bgColor: 'rgba(255, 152, 0, 0.08)',
    borderColor: 'rgba(255, 152, 0, 0.2)',
  },
  poor: {
    color: 'error' as const,
    label: 'Poor',
    icon: <ErrorIcon />,
    bgColor: 'rgba(244, 67, 54, 0.08)',
    borderColor: 'rgba(244, 67, 54, 0.2)',
  },
}

const matchConfig = {
  excellent: { color: 'success', icon: '🟢', label: 'Excellent' },
  good: { color: 'info', icon: '🟡', label: 'Good' },
  fair: { color: 'warning', icon: '🟠', label: 'Fair' },
  poor: { color: 'error', icon: '🔴', label: 'Poor' },
}

const EnhancedCropCard: React.FC<EnhancedCropCardProps> = ({
  crop,
  rank = 1,
  onFavorite,
  isFavorite = false,
  showDetails = true,
  compact = false
}) => {
  const [expanded, setExpanded] = useState(false)
  const [showAIInsights, setShowAIInsights] = useState(false)

  const config = suitabilityConfig[crop.suitability_level]
  const scorePercentage = Math.round(crop.score)

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'info'
    if (score >= 40) return 'warning'
    return 'error'
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return '🥇'
      case 2: return '🥈'
      case 3: return '🥉'
      default: return `#${rank}`
    }
  }

  const handleToggle = () => {
    setExpanded(!expanded)
  }

  const handleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation()
    onFavorite?.(crop.crop_name)
  }

  const renderMatchIndicator = (match: string, label: string, icon: string) => {
    const matchInfo = matchConfig[match as keyof typeof matchConfig]
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <Typography variant="caption">{icon}</Typography>
        <Typography variant="caption" color={`${matchInfo.color}.main`}>
          {label}
        </Typography>
      </Box>
    )
  }

  const renderAIInsights = () => {
    if (!crop.ai_summary && !crop.key_benefits && !crop.potential_challenges) {
      return null
    }

    return (
      <Box sx={{ mt: 2 }}>
        <Divider sx={{ mb: 2 }} />
        
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom color="primary.main">
          🤖 AI-Enhanced Insights
        </Typography>

        {crop.ai_summary && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
              "{crop.ai_summary}"
            </Typography>
          </Box>
        )}

        <Grid container spacing={2}>
          {crop.key_benefits && crop.key_benefits.length > 0 && (
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1, opacity: 0.1 }}>
                <Typography variant="subtitle2" fontWeight="bold" color="success.dark" gutterBottom>
                  ✅ Key Benefits
                </Typography>
                <List dense>
                  {crop.key_benefits.map((benefit, index) => (
                    <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckCircleIcon color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2">
                            {benefit}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Grid>
          )}

          {crop.potential_challenges && crop.potential_challenges.length > 0 && (
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1, opacity: 0.1 }}>
                <Typography variant="subtitle2" fontWeight="bold" color="warning.dark" gutterBottom>
                  ⚠️ Potential Challenges
                </Typography>
                <List dense>
                  {crop.potential_challenges.map((challenge, index) => (
                    <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <WarningIcon color="warning" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2">
                            {challenge}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Grid>
          )}
        </Grid>

        {crop.actionable_steps && crop.actionable_steps.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom color="primary.main">
              📋 Actionable Steps
            </Typography>
            <List dense>
              {crop.actionable_steps.map((step, index) => (
                <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <Typography variant="body2" fontWeight="bold" color="primary.main">
                      {index + 1}.
                    </Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2">
                        {step}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {crop.seasonal_advice && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 1, opacity: 0.1 }}>
            <Typography variant="subtitle2" fontWeight="bold" color="info.dark" gutterBottom>
              📅 Seasonal Advice
            </Typography>
            <Typography variant="body2">
              {crop.seasonal_advice}
            </Typography>
          </Box>
        )}
      </Box>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: (rank - 1) * 0.1 }}
    >
      <Card
        sx={{
          mb: 2,
          backgroundColor: config.bgColor,
          border: `2px solid ${config.borderColor}`,
          borderRadius: 3,
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-4px)',
            borderColor: `${config.color}.main`,
          },
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              {/* Rank */}
              <Avatar
                sx={{
                  bgcolor: `${config.color}.main`,
                  color: 'white',
                  mr: 2,
                  width: 40,
                  height: 40,
                  fontSize: '1.2rem',
                }}
              >
                {getRankIcon(rank)}
              </Avatar>

              {/* Crop Name and Score */}
              <Box sx={{ flex: 1 }}>
                <Typography variant="h5" fontWeight="bold" color={`${config.color}.main`}>
                  {crop.crop_name.charAt(0).toUpperCase() + crop.crop_name.slice(1)}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6" fontWeight="bold" color={`${getScoreColor(scorePercentage)}.main`}>
                      {scorePercentage}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={scorePercentage}
                      color={getScoreColor(scorePercentage) as any}
                      sx={{ width: 100, height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  
                  <Chip
                    icon={config.icon}
                    label={config.label}
                    color={config.color}
                    variant="filled"
                    size="small"
                  />
                </Box>
              </Box>
            </Box>

            {/* Actions */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {onFavorite && (
                <Tooltip title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}>
                  <IconButton size="small" onClick={handleFavorite}>
                    {isFavorite ? <StarIcon color="warning" /> : <StarBorderIcon />}
                  </IconButton>
                </Tooltip>
              )}
              
              {showDetails && (
                <Tooltip title={expanded ? 'Show less' : 'Show more details'}>
                  <IconButton size="small" onClick={handleToggle}>
                    {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Match Indicators */}
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <WaterDropIcon color="info" sx={{ mb: 0.5 }} />
                  <Typography variant="caption" display="block">
                    Rainfall
                  </Typography>
                  {renderMatchIndicator(crop.rainfall_match, 'Rainfall', matchConfig[crop.rainfall_match].icon)}
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <ThermostatIcon color="warning" sx={{ mb: 0.5 }} />
                  <Typography variant="caption" display="block">
                    Temperature
                  </Typography>
                  {renderMatchIndicator(crop.temperature_match, 'Temperature', matchConfig[crop.temperature_match].icon)}
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <CalendarIcon color="primary" sx={{ mb: 0.5 }} />
                  <Typography variant="caption" display="block">
                    Season
                  </Typography>
                  {renderMatchIndicator(crop.season_suitability, 'Season', matchConfig[crop.season_suitability].icon)}
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* Quick Info */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            {crop.planting_time && (
              <Chip
                icon={<CalendarIcon />}
                label={`Plant: ${crop.planting_time}`}
                size="small"
                variant="outlined"
              />
            )}
            {crop.yield_potential && (
              <Chip
                icon={<TrendingUpIcon />}
                label={`Yield: ${crop.yield_potential}`}
                size="small"
                variant="outlined"
              />
            )}
            {crop.confidence_score && (
              <Chip
                icon={<InfoIcon />}
                label={`Confidence: ${Math.round(crop.confidence_score * 100)}%`}
                size="small"
                variant="outlined"
                color="info"
              />
            )}
          </Box>

          {/* Expandable Details */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                style={{ overflow: 'hidden' }}
              >
                <Divider sx={{ mb: 2 }} />

                {/* Description */}
                {crop.description && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Description
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {crop.description}
                    </Typography>
                  </Box>
                )}

                {/* Varieties */}
                {crop.varieties && crop.varieties.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Recommended Varieties
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {crop.varieties.map((variety, index) => (
                        <Chip
                          key={index}
                          label={variety}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Guide Recommendations */}
                {crop.guide_recommendations && crop.guide_recommendations.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Guide Recommendations
                    </Typography>
                    <List dense>
                      {crop.guide_recommendations.map((rec, index) => (
                        <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Typography variant="body2" fontWeight="bold" color="primary.main">
                              {index + 1}.
                            </Typography>
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Typography variant="body2">
                                {rec}
                              </Typography>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {/* AI Insights */}
                {renderAIInsights()}

                {/* Sources */}
                {crop.sources && crop.sources.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Sources: {crop.sources.join(', ')}
                    </Typography>
                  </Box>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default EnhancedCropCard
