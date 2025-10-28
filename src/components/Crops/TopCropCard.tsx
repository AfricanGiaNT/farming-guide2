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
  Stack,
} from '@mui/material'
import {
  TrendingUp as TrendIcon,
  CalendarToday as CalendarIcon,
  ArrowForward as ArrowIcon,
  Star as StarIcon,
  Agriculture as CropIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface TopCropCardProps {
  crop: {
    crop_name: string
    score: number
    suitability_level: string
    top_varieties?: string[]
    planting_time?: string
    yield_potential?: string
    description?: string
  }
  rank: number
  onClick: () => void
}

const TopCropCard: React.FC<TopCropCardProps> = ({
  crop,
  rank,
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

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'warning' // Gold
      case 2:
        return 'info' // Silver
      case 3:
        return 'success' // Bronze
      default:
        return 'default'
    }
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇'
      case 2:
        return '🥈'
      case 3:
        return '🥉'
      default:
        return '⭐'
    }
  }

  const cropEmoji = getCropEmoji(crop.crop_name)
  const suitabilityColor = getSuitabilityColor(crop.suitability_level)
  const rankColor = getRankColor(rank)
  const rankIcon = getRankIcon(rank)

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: rank * 0.1 }}
    >
      <Card
        sx={{
          cursor: 'pointer',
          height: '100%',
          transition: 'all 0.3s ease',
          position: 'relative',
          overflow: 'visible',
          '&:hover': {
            boxShadow: 8,
            transform: 'translateY(-4px)',
          },
        }}
        onClick={onClick}
      >
        {/* Rank Badge */}
        <Box
          sx={{
            position: 'absolute',
            top: -8,
            right: 16,
            zIndex: 1,
          }}
        >
          <Chip
            icon={<StarIcon />}
            label={`#${rank}`}
            color={rankColor as any}
            size="small"
            sx={{
              fontWeight: 'bold',
              fontSize: '0.75rem',
              height: 24,
              '& .MuiChip-icon': {
                fontSize: '0.875rem',
              },
            }}
          />
        </Box>

        <CardContent sx={{ p: isMobile ? 2.5 : 3, pt: isMobile ? 3.5 : 4 }}>
          {/* Header with emoji and crop name */}
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Typography variant={isMobile ? "h2" : "h1"} component="span">
              {cropEmoji}
            </Typography>
            <Box flex={1}>
              <Typography 
                variant={isMobile ? "h5" : "h4"} 
                fontWeight="bold" 
                color="primary.main"
                sx={{ lineHeight: 1.2 }}
              >
                {crop.crop_name}
              </Typography>
              {crop.description && (
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ 
                    display: 'block',
                    mt: 0.5,
                    lineHeight: 1.3,
                    fontSize: isMobile ? '0.875rem' : '1rem'
                  }}
                >
                  {crop.description}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Suitability Score - More Prominent */}
          <Box mb={2.5}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight="bold" color="text.secondary">
                Suitability Score
              </Typography>
              <Typography 
                variant={isMobile ? "h4" : "h3"} 
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
                height: isMobile ? 8 : 10,
                borderRadius: 5,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                },
              }}
            />
          </Box>

          {/* Suitability Level - More Prominent */}
          <Box mb={2.5}>
            <Chip
              label={crop.suitability_level.replace('_', ' ')}
              color={suitabilityColor as any}
              size={isMobile ? "medium" : "large"}
              variant="filled"
              sx={{ 
                fontWeight: 'bold',
                fontSize: isMobile ? '0.875rem' : '1rem',
                height: isMobile ? 32 : 36,
              }}
            />
          </Box>

          {/* Top Varieties - More Prominent */}
          {crop.top_varieties && crop.top_varieties.length > 0 && (
            <Box mb={2.5}>
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
                    sx={{ 
                      fontSize: isMobile ? '0.75rem' : '0.875rem',
                      height: isMobile ? 24 : 28,
                    }}
                  />
                ))}
                {crop.top_varieties.length > 3 && (
                  <Chip
                    label={`+${crop.top_varieties.length - 3} more`}
                    size="small"
                    variant="outlined"
                    color="default"
                    sx={{ 
                      fontSize: isMobile ? '0.75rem' : '0.875rem',
                      height: isMobile ? 24 : 28,
                    }}
                  />
                )}
              </Box>
            </Box>
          )}

          {/* Quick Info - Better Layout */}
          <Stack direction="row" spacing={2} mb={2.5} flexWrap="wrap">
            {crop.planting_time && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <CalendarIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  {crop.planting_time}
                </Typography>
              </Box>
            )}
            {crop.yield_potential && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <TrendIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  {crop.yield_potential}
                </Typography>
              </Box>
            )}
          </Stack>

          {/* View Varieties Button - More Prominent */}
          <Button
            variant="contained"
            fullWidth
            endIcon={<ArrowIcon />}
            sx={{
              mt: 1,
              minHeight: isMobile ? 44 : 52,
              fontSize: isMobile ? '0.875rem' : '1rem',
              fontWeight: 'bold',
              borderRadius: 2,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              '&:hover': {
                background: `linear-gradient(45deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                transform: 'translateY(-1px)',
              },
            }}
          >
            View Varieties & Details
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default TopCropCard
