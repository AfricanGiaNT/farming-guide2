/**
 * EnhancedSectionHeader Component
 * Provides enhanced section headers with improved visual hierarchy and interactive elements
 * Implements Phase 3: Enhanced User Experience
 */

import React from 'react'
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Tooltip,
  Divider,
  Avatar,
  Badge
} from '@mui/material'
import {
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  FilterList as FilterIcon,
  Sort as SortIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

export interface EnhancedSectionHeaderProps {
  title: string
  subtitle?: string
  icon?: React.ReactNode
  emoji?: string
  badge?: {
    content: string | number
    color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  }
  priority?: 'high' | 'medium' | 'low'
  status?: 'active' | 'inactive' | 'loading' | 'error' | 'success'
  actions?: {
    type: 'expand' | 'refresh' | 'settings' | 'filter' | 'sort' | 'favorite'
    onClick: () => void
    tooltip?: string
    active?: boolean
  }[]
  onToggle?: (expanded: boolean) => void
  expanded?: boolean
  showDivider?: boolean
  variant?: 'default' | 'compact' | 'detailed'
}

const priorityConfig = {
  high: {
    color: 'error' as const,
    bgColor: 'rgba(244, 67, 54, 0.1)',
    borderColor: 'rgba(244, 67, 54, 0.3)',
    label: 'High Priority',
  },
  medium: {
    color: 'warning' as const,
    bgColor: 'rgba(255, 152, 0, 0.1)',
    borderColor: 'rgba(255, 152, 0, 0.3)',
    label: 'Medium Priority',
  },
  low: {
    color: 'info' as const,
    bgColor: 'rgba(33, 150, 243, 0.1)',
    borderColor: 'rgba(33, 150, 243, 0.3)',
    label: 'Low Priority',
  },
}

const statusConfig = {
  active: {
    color: 'success' as const,
    icon: '🟢',
    label: 'Active',
  },
  inactive: {
    color: 'default' as const,
    icon: '⚪',
    label: 'Inactive',
  },
  loading: {
    color: 'info' as const,
    icon: '🔄',
    label: 'Loading',
  },
  error: {
    color: 'error' as const,
    icon: '❌',
    label: 'Error',
  },
  success: {
    color: 'success' as const,
    icon: '✅',
    label: 'Success',
  },
}

const EnhancedSectionHeader: React.FC<EnhancedSectionHeaderProps> = ({
  title,
  subtitle,
  icon,
  emoji,
  badge,
  priority,
  status,
  actions = [],
  onToggle,
  expanded = false,
  showDivider = true,
  variant = 'default'
}) => {
  const priorityInfo = priority ? priorityConfig[priority] : null
  const statusInfo = status ? statusConfig[status] : null

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'expand':
        return expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />
      case 'refresh':
        return <RefreshIcon />
      case 'settings':
        return <SettingsIcon />
      case 'filter':
        return <FilterIcon />
      case 'sort':
        return <SortIcon />
      case 'favorite':
        return expanded ? <StarIcon /> : <StarBorderIcon />
      default:
        return <InfoIcon />
    }
  }

  const getActionColor = (type: string, active?: boolean) => {
    if (active) return 'primary'
    switch (type) {
      case 'expand':
        return 'primary'
      case 'refresh':
        return 'info'
      case 'settings':
        return 'default'
      case 'filter':
        return 'secondary'
      case 'sort':
        return 'secondary'
      case 'favorite':
        return 'warning'
      default:
        return 'default'
    }
  }

  const handleActionClick = (action: any) => {
    if (action.type === 'expand' && onToggle) {
      onToggle(!expanded)
    }
    action.onClick()
  }

  const renderCompactVariant = () => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
      {emoji && <Typography variant="h6">{emoji}</Typography>}
      <Typography variant="h6" fontWeight="bold">
        {title}
      </Typography>
      {badge && (
        <Badge
          badgeContent={badge.content}
          color={badge.color || 'primary'}
          sx={{ ml: 1 }}
        />
      )}
      {actions.map((action, index) => (
        <Tooltip key={index} title={action.tooltip || action.type}>
          <IconButton
            size="small"
            color={getActionColor(action.type, action.active)}
            onClick={() => handleActionClick(action)}
          >
            {getActionIcon(action.type)}
          </IconButton>
        </Tooltip>
      ))}
    </Box>
  )

  const renderDetailedVariant = () => (
    <Box
      sx={{
        p: 3,
        backgroundColor: priorityInfo?.bgColor || 'transparent',
        border: priorityInfo ? `1px solid ${priorityInfo.borderColor}` : 'none',
        borderRadius: 2,
        mb: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Icon/Emoji */}
          <Avatar
            sx={{
              bgcolor: priorityInfo?.color ? `${priorityInfo.color}.main` : 'primary.main',
              color: 'white',
              width: 48,
              height: 48,
            }}
          >
            {icon || (emoji && <Typography variant="h6">{emoji}</Typography>)}
          </Avatar>

          {/* Title and Subtitle */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="h5" fontWeight="bold">
                {title}
              </Typography>
              
              {badge && (
                <Chip
                  label={badge.content}
                  color={badge.color || 'primary'}
                  size="small"
                  variant="outlined"
                />
              )}
              
              {priority && (
                <Chip
                  label={priorityInfo?.label}
                  color={priorityInfo?.color}
                  size="small"
                  variant="filled"
                />
              )}
              
              {status && (
                <Chip
                  icon={<Typography variant="caption">{statusInfo?.icon}</Typography>}
                  label={statusInfo?.label}
                  color={statusInfo?.color}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
            
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {actions.map((action, index) => (
            <Tooltip key={index} title={action.tooltip || action.type}>
              <IconButton
                color={getActionColor(action.type, action.active)}
                onClick={() => handleActionClick(action)}
              >
                {getActionIcon(action.type)}
              </IconButton>
            </Tooltip>
          ))}
        </Box>
      </Box>
    </Box>
  )

  const renderDefaultVariant = () => (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {emoji && <Typography variant="h6">{emoji}</Typography>}
          <Typography variant="h6" fontWeight="bold">
            {title}
          </Typography>
          {badge && (
            <Badge
              badgeContent={badge.content}
              color={badge.color || 'primary'}
            />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {actions.map((action, index) => (
            <Tooltip key={index} title={action.tooltip || action.type}>
              <IconButton
                size="small"
                color={getActionColor(action.type, action.active)}
                onClick={() => handleActionClick(action)}
              >
                {getActionIcon(action.type)}
              </IconButton>
            </Tooltip>
          ))}
        </Box>
      </Box>
      
      {subtitle && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {subtitle}
        </Typography>
      )}
    </Box>
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {variant === 'compact' && renderCompactVariant()}
      {variant === 'detailed' && renderDetailedVariant()}
      {variant === 'default' && renderDefaultVariant()}
      
      {showDivider && (
        <Divider sx={{ mt: variant === 'detailed' ? 0 : 1 }} />
      )}
    </motion.div>
  )
}

export default EnhancedSectionHeader
