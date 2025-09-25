import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  useTheme,
} from '@mui/material'
import { SvgIconComponent } from '@mui/icons-material'
import { motion } from 'framer-motion'

interface QuickActionCardProps {
  title: string
  description: string
  icon: SvgIconComponent
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  onClick: () => void
}

const QuickActionCard: React.FC<QuickActionCardProps> = ({
  title,
  description,
  icon: Icon,
  color,
  onClick,
}) => {
  const theme = useTheme()

  const colorMap = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    success: theme.palette.success.main,
    warning: theme.palette.warning.main,
    error: theme.palette.error.main,
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
            boxShadow: theme.shadows[8],
            transform: 'translateY(-2px)',
          },
        }}
        onClick={onClick}
      >
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="flex-start" gap={2}>
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: `${colorMap[color]}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Icon sx={{ color: colorMap[color], fontSize: 28 }} />
            </Box>
            
            <Box flex={1}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                {title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {description}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default QuickActionCard