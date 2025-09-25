import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
} from '@mui/material'
import { motion } from 'framer-motion'

interface FarmingTipCardProps {
  title: string
  content: string
  category: string
}

const FarmingTipCard: React.FC<FarmingTipCardProps> = ({
  title,
  content,
  category,
}) => {
  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'seasonal':
        return 'primary'
      case 'soil health':
        return 'warning'
      case 'post-harvest':
        return 'success'
      case 'pest control':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-1px)',
          },
        }}
      >
        <CardContent sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Typography variant="subtitle1" fontWeight="bold" sx={{ flex: 1 }}>
              {title}
            </Typography>
            <Chip
              label={category}
              size="small"
              color={getCategoryColor(category) as any}
              variant="outlined"
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            {content}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default FarmingTipCard