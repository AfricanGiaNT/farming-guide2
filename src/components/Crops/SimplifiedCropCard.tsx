import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Button,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Agriculture as CropIcon,
  TrendingUp as TrendIcon,
  CalendarToday as CalendarIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface SimplifiedCropCardProps {
  crop: {
    crop_name: string
    score: number
    suitability_level: string
    top_varieties?: string[]
    planting_time?: string
    yield_potential?: string
    description?: string
  }
  onClick: () => void
}

const SimplifiedCropCard: React.FC<SimplifiedCropCardProps> = ({
  crop,
  onClick
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const getCropEmoji = (cropName: string) => {
    const name = cropName.toLowerCase()
    if (name.includes('maize') || name.includes('corn')) return '🌽'
    if (name.includes('bean')) return '🫘'
    if (name.includes('groundnut') || name.includes('peanut')) return '🥜'
    if (name.includes('cassava')) return '🍠'
    if (name.includes('sweet potato')) return '🍠'
    if (name.includes('sorghum')) return '🌾'
    if (name.includes('soybean')) return '🫘'
    if (name.includes('rice')) return '🍚'
    if (name.includes('millet')) return '🌾'
    if (name.includes('wheat')) return '🌾'
    if (name.includes('tomato')) return '🍅'
    if (name.includes('onion')) return '🧅'
    if (name.includes('cabbage')) return '🥬'
    if (name.includes('lettuce')) return '🥬'
    if (name.includes('spinach')) return '🥬'
    if (name.includes('carrot')) return '🥕'
    if (name.includes('pepper')) return '🌶️'
    if (name.includes('eggplant')) return '🍆'
    if (name.includes('cucumber')) return '🥒'
    if (name.includes('pumpkin')) return '🎃'
    if (name.includes('watermelon')) return '🍉'
    return '🌱'
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

  const cropEmoji = getCropEmoji(crop.crop_name)
  const suitabilityColor = getSuitabilityColor(crop.suitability_level)

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
        <CardContent sx={{ p: isMobile ? 2 : 3 }}>
          {/* Header with emoji and crop name */}
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Typography variant={isMobile ? "h3" : "h2"} component="span">
              {cropEmoji}
            </Typography>
            <Box flex={1}>
              <Typography 
                variant={isMobile ? "h6" : "h5"} 
                fontWeight="bold" 
                color="primary.main"
                sx={{ lineHeight: 1.2 }}
              >
                {crop.crop_name}
              </Typography>
              {crop.description && (
                <Typography 
                  variant="caption" 
                  color="text.secondary"
                  sx={{ 
                    display: 'block',
                    mt: 0.5,
                    lineHeight: 1.3
                  }}
                >
                  {crop.description}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Suitability Score */}
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight="bold" color="text.secondary">
                Suitability Score
              </Typography>
              <Typography 
                variant={isMobile ? "h6" : "h5"} 
                fontWeight="bold" 
                color="primary.main"
              >
                {Math.round(crop.score)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={crop.score}
              sx={{
                height: isMobile ? 6 : 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                },
              }}
            />
          </Box>

          {/* Suitability Level */}
          <Box mb={2}>
            <Chip
              label={crop.suitability_level.replace('_', ' ')}
              color={suitabilityColor as any}
              size={isMobile ? "small" : "medium"}
              variant="filled"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>

          {/* Top Varieties */}
          {crop.top_varieties && crop.top_varieties.length > 0 && (
            <Box mb={2}>
              <Typography variant="body2" fontWeight="bold" gutterBottom color="text.secondary">
                Top Varieties:
              </Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap">
                {crop.top_varieties.slice(0, 3).map((variety, index) => (
                  <Chip
                    key={index}
                    label={variety}
                    size="small"
                    variant="outlined"
                    color="primary"
                    sx={{ fontSize: '0.75rem' }}
                  />
                ))}
                {crop.top_varieties.length > 3 && (
                  <Chip
                    label={`+${crop.top_varieties.length - 3} more`}
                    size="small"
                    variant="outlined"
                    color="default"
                    sx={{ fontSize: '0.75rem' }}
                  />
                )}
              </Box>
            </Box>
          )}

          {/* Quick Info */}
          <Box display="flex" gap={2} mb={2} flexWrap="wrap">
            {crop.planting_time && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <CalendarIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {crop.planting_time}
                </Typography>
              </Box>
            )}
            {crop.yield_potential && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <TrendIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {crop.yield_potential}
                </Typography>
              </Box>
            )}
          </Box>

          {/* View Details Button */}
          <Button
            variant="contained"
            fullWidth
            endIcon={<ArrowIcon />}
            sx={{
              mt: 1,
              minHeight: isMobile ? 40 : 48,
              fontSize: isMobile ? '0.875rem' : '1rem',
              fontWeight: 'bold',
            }}
          >
            View Details & Varieties
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default SimplifiedCropCard
