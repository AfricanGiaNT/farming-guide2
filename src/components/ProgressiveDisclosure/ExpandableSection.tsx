/**
 * ExpandableSection Component
 * Provides progressive disclosure for information sections
 * Implements Phase 3: Enhanced User Experience
 */

import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Collapse,
  Box,
  Chip,
  Tooltip,
  Divider
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

export interface ExpandableSectionProps {
  title: string
  summary: string
  details: string | React.ReactNode
  category: 'critical' | 'important' | 'helpful'
  priority?: number
  icon?: React.ReactNode
  tooltip?: string
  defaultExpanded?: boolean
  onToggle?: (expanded: boolean) => void
  children?: React.ReactNode
}

const categoryConfig = {
  critical: {
    color: 'error' as const,
    icon: <ErrorIcon />,
    bgColor: 'rgba(244, 67, 54, 0.05)',
    borderColor: 'rgba(244, 67, 54, 0.2)',
    chipColor: 'error' as const,
  },
  important: {
    color: 'warning' as const,
    icon: <WarningIcon />,
    bgColor: 'rgba(255, 152, 0, 0.05)',
    borderColor: 'rgba(255, 152, 0, 0.2)',
    chipColor: 'warning' as const,
  },
  helpful: {
    color: 'success' as const,
    icon: <CheckCircleIcon />,
    bgColor: 'rgba(76, 175, 80, 0.05)',
    borderColor: 'rgba(76, 175, 80, 0.2)',
    chipColor: 'success' as const,
  },
}

const ExpandableSection: React.FC<ExpandableSectionProps> = ({
  title,
  summary,
  details,
  category,
  priority = 5,
  icon,
  tooltip,
  defaultExpanded = false,
  onToggle,
  children
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const config = categoryConfig[category]

  const handleToggle = () => {
    const newExpanded = !expanded
    setExpanded(newExpanded)
    onToggle?.(newExpanded)
  }

  const getPriorityLabel = (priority: number) => {
    if (priority >= 8) return 'High Priority'
    if (priority >= 5) return 'Medium Priority'
    return 'Low Priority'
  }

  return (
    <motion.div
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
            transform: 'translateY(-2px)',
          },
        }}
      >
        <CardContent sx={{ p: 2 }}>
          {/* Header */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
            onClick={handleToggle}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              {/* Category Icon */}
              <Box sx={{ mr: 1.5, color: `${config.color}.main` }}>
                {icon || config.icon}
              </Box>

              {/* Title and Summary */}
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <Typography
                    variant="h6"
                    fontWeight="bold"
                    color={`${config.color}.main`}
                    sx={{ mr: 1 }}
                  >
                    {title}
                  </Typography>
                  
                  {/* Priority Chip */}
                  <Chip
                    label={getPriorityLabel(priority)}
                    size="small"
                    color={config.chipColor}
                    variant="outlined"
                    sx={{ mr: 1 }}
                  />

                  {/* Tooltip */}
                  {tooltip && (
                    <Tooltip title={tooltip} arrow>
                      <InfoIcon fontSize="small" color="action" />
                    </Tooltip>
                  )}
                </Box>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: expanded ? 'none' : 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    transition: 'all 0.3s ease',
                  }}
                >
                  {summary}
                </Typography>
              </Box>
            </Box>

            {/* Expand/Collapse Button */}
            <IconButton
              size="small"
              sx={{
                color: `${config.color}.main`,
                transition: 'transform 0.3s ease',
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>

          {/* Expandable Content */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                style={{ overflow: 'hidden' }}
              >
                <Divider sx={{ my: 2 }} />
                
                <Box sx={{ mt: 1 }}>
                  {typeof details === 'string' ? (
                    <Typography
                      variant="body2"
                      color="text.primary"
                      sx={{ lineHeight: 1.6 }}
                    >
                      {details}
                    </Typography>
                  ) : (
                    details
                  )}
                  
                  {children && (
                    <Box sx={{ mt: 2 }}>
                      {children}
                    </Box>
                  )}
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default ExpandableSection
