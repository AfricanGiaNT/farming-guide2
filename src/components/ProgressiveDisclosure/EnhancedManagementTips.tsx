/**
 * EnhancedManagementTips Component
 * Provides categorized management tips with improved visual hierarchy
 * Implements Phase 3: Enhanced User Experience
 */

import React, { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
  Badge
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Agriculture as AgricultureIcon,
  WaterDrop as WaterDropIcon,
  PestControl as PestControlIcon,
  Harvest as HarvestIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

export interface ManagementTip {
  text: string
  priority?: number
  actionable?: boolean
  category?: 'planting' | 'maintenance' | 'harvest' | 'general'
}

export interface CategorizedTips {
  planting: string[]
  maintenance: string[]
  harvest: string[]
  general: string[]
}

export interface EnhancedManagementTipsProps {
  tips: CategorizedTips | ManagementTip[]
  title?: string
  showIcons?: boolean
  showPriority?: boolean
  maxTipsPerCategory?: number
  onTipClick?: (tip: string, category: string) => void
}

const categoryConfig = {
  planting: {
    icon: <AgricultureIcon />,
    label: 'Planting Phase',
    color: 'primary' as const,
    bgColor: 'rgba(25, 118, 210, 0.05)',
    borderColor: 'rgba(25, 118, 210, 0.2)',
    emoji: '🌱',
  },
  maintenance: {
    icon: <WaterDropIcon />,
    label: 'Maintenance Phase',
    color: 'info' as const,
    bgColor: 'rgba(33, 150, 243, 0.05)',
    borderColor: 'rgba(33, 150, 243, 0.2)',
    emoji: '💧',
  },
  harvest: {
    icon: <HarvestIcon />,
    label: 'Harvest Phase',
    color: 'success' as const,
    bgColor: 'rgba(76, 175, 80, 0.05)',
    borderColor: 'rgba(76, 175, 80, 0.2)',
    emoji: '🌾',
  },
  general: {
    icon: <InfoIcon />,
    label: 'General Tips',
    color: 'default' as const,
    bgColor: 'rgba(158, 158, 158, 0.05)',
    borderColor: 'rgba(158, 158, 158, 0.2)',
    emoji: '💡',
  },
}

const EnhancedManagementTips: React.FC<EnhancedManagementTipsProps> = ({
  tips,
  title = 'Management Tips',
  showIcons = true,
  showPriority = true,
  maxTipsPerCategory = 5,
  onTipClick
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['planting']) // Default to planting expanded
  )

  // Convert tips to categorized format if needed
  const categorizedTips = React.useMemo(() => {
    if (Array.isArray(tips)) {
      // Convert array format to categorized format
      const categorized: CategorizedTips = {
        planting: [],
        maintenance: [],
        harvest: [],
        general: [],
      }

      tips.forEach(tip => {
        const category = tip.category || 'general'
        if (categorized[category as keyof CategorizedTips]) {
          categorized[category as keyof CategorizedTips].push(tip.text)
        }
      })

      return categorized
    }
    return tips as CategorizedTips
  }, [tips])

  const handleCategoryToggle = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const getTipPriority = (tip: string): number => {
    // Simple priority calculation based on content
    if (tip.toLowerCase().includes('urgent') || tip.toLowerCase().includes('immediately')) return 9
    if (tip.toLowerCase().includes('important') || tip.toLowerCase().includes('critical')) return 8
    if (tip.toLowerCase().includes('recommended') || tip.toLowerCase().includes('should')) return 7
    if (tip.toLowerCase().includes('consider') || tip.toLowerCase().includes('may')) return 6
    return 5
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'error'
    if (priority >= 6) return 'warning'
    return 'success'
  }

  const getPriorityLabel = (priority: number) => {
    if (priority >= 8) return 'High Priority'
    if (priority >= 6) return 'Medium Priority'
    return 'Low Priority'
  }

  const renderTipItem = (tip: string, index: number, category: string) => {
    const priority = getTipPriority(tip)
    const isActionable = tip.toLowerCase().includes('apply') || 
                        tip.toLowerCase().includes('use') || 
                        tip.toLowerCase().includes('plant') ||
                        tip.toLowerCase().includes('harvest')

    return (
      <motion.div
        key={`${category}-${index}`}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2, delay: index * 0.05 }}
      >
        <ListItem
          sx={{
            py: 1,
            px: 0,
            cursor: onTipClick ? 'pointer' : 'default',
            borderRadius: 1,
            '&:hover': onTipClick ? {
              bgcolor: 'action.hover',
              transform: 'translateX(4px)',
            } : {},
            transition: 'all 0.2s ease',
          }}
          onClick={() => onTipClick?.(tip, category)}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>
            {isActionable ? (
              <CheckCircleIcon color="success" fontSize="small" />
            ) : (
              <InfoIcon color="action" fontSize="small" />
            )}
          </ListItemIcon>
          
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" sx={{ flex: 1 }}>
                  {tip}
                </Typography>
                
                {showPriority && (
                  <Chip
                    label={getPriorityLabel(priority)}
                    size="small"
                    color={getPriorityColor(priority) as any}
                    variant="outlined"
                  />
                )}
              </Box>
            }
          />
        </ListItem>
      </motion.div>
    )
  }

  const renderCategory = (category: keyof CategorizedTips) => {
    const tips = categorizedTips[category]
    const config = categoryConfig[category]
    const isExpanded = expandedCategories.has(category)
    const hasTips = tips && tips.length > 0

    if (!hasTips) return null

    const displayTips = tips.slice(0, maxTipsPerCategory)
    const hasMore = tips.length > maxTipsPerCategory

    return (
      <motion.div
        key={category}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card
          sx={{
            mb: 2,
            backgroundColor: config.bgColor,
            border: `1px solid ${config.borderColor}`,
            borderRadius: 2,
            transition: 'all 0.3s ease',
            '&:hover': {
              boxShadow: 2,
            },
          }}
        >
          <CardContent sx={{ p: 2 }}>
            {/* Category Header */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                mb: isExpanded ? 2 : 0,
              }}
              onClick={() => handleCategoryToggle(category)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {showIcons && (
                  <Box sx={{ mr: 1.5, color: `${config.color}.main` }}>
                    {config.icon}
                  </Box>
                )}
                
                <Box>
                  <Typography
                    variant="h6"
                    fontWeight="bold"
                    color={`${config.color}.main`}
                    sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                  >
                    {config.emoji} {config.label}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                    <Badge badgeContent={tips.length} color={config.color}>
                      <ScheduleIcon fontSize="small" color="action" />
                    </Badge>
                    <Typography variant="caption" color="text.secondary">
                      {tips.length} tip{tips.length !== 1 ? 's' : ''}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <IconButton
                size="small"
                sx={{
                  color: `${config.color}.main`,
                  transition: 'transform 0.3s ease',
                  transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                }}
              >
                <ExpandMoreIcon />
              </IconButton>
            </Box>

            {/* Category Content */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  style={{ overflow: 'hidden' }}
                >
                  <Divider sx={{ mb: 2 }} />
                  
                  <List dense>
                    {displayTips.map((tip, index) => 
                      renderTipItem(tip, index, category)
                    )}
                  </List>

                  {hasMore && (
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        +{tips.length - maxTipsPerCategory} more tips available
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

  const totalTips = Object.values(categorizedTips).reduce((sum, tips) => sum + tips.length, 0)

  if (totalTips === 0) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <AgricultureIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Management Tips Available
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Management tips will appear here when crop recommendations are loaded.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            {title}
          </Typography>
          
          <Chip
            label={`${totalTips} Total Tips`}
            color="primary"
            variant="outlined"
            size="small"
          />
        </Box>

        {/* Categories */}
        <Box>
          {(['planting', 'maintenance', 'harvest', 'general'] as const).map(category => 
            renderCategory(category)
          )}
        </Box>
      </CardContent>
    </Card>
  )
}

export default EnhancedManagementTips
