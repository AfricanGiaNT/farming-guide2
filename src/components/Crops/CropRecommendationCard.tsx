import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
} from '@mui/material'
import {
  Agriculture as CropIcon,
  Star as StarIcon,
  TrendingUp as TrendIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface CropRecommendation {
  cropId: string
  cropName: string
  totalScore: number
  suitabilityLevel: 'excellent' | 'very_good' | 'good' | 'fair' | 'poor'
  confidenceScore: number
  confidenceLevel: 'high' | 'medium' | 'low'
  reasons: string[]
}

interface CropRecommendationCardProps {
  crop: CropRecommendation
  onClick: () => void
}

const CropRecommendationCard: React.FC<CropRecommendationCardProps> = ({
  crop,
  onClick,
}) => {
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

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'success'
      case 'medium':
        return 'warning'
      case 'low':
        return 'error'
      default:
        return 'default'
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
                {getCropEmoji(crop.cropName)}
              </Typography>
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {crop.cropName}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {crop.cropId}
                </Typography>
              </Box>
            </Box>
            
            <IconButton size="small" color="primary">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Box>

          {/* Score Display */}
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight="bold">
                Suitability Score
              </Typography>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {crop.totalScore}/125
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(crop.totalScore / 125) * 100}
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

          {/* Suitability and Confidence */}
          <Box display="flex" gap={1} mb={2}>
            <Chip
              label={crop.suitabilityLevel.replace('_', ' ')}
              color={getSuitabilityColor(crop.suitabilityLevel) as any}
              size="small"
              variant="filled"
            />
            <Chip
              label={`${crop.confidenceLevel} confidence`}
              color={getConfidenceColor(crop.confidenceLevel) as any}
              size="small"
              variant="outlined"
            />
          </Box>

          {/* Top Reason */}
          {crop.reasons.length > 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              "{crop.reasons[0]}"
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default CropRecommendationCard