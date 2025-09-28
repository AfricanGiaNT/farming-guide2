/**
 * VisualDesignSystem Component
 * Provides enhanced visual design with improved typography, spacing, and color coding
 * Implements Phase 3: Enhanced User Experience
 */

import React from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Divider,
  Grid,
  Avatar,
  Badge,
  Paper
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  WaterDrop as WaterDropIcon,
  Thermostat as ThermostatIcon,
  Agriculture as AgricultureIcon
} from '@mui/icons-material'

// Design System Constants
export const DESIGN_SYSTEM = {
  colors: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
      contrastText: '#ffffff',
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
      contrastText: '#ffffff',
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
      contrastText: '#ffffff',
    },
    error: {
      main: '#d32f2f',
      light: '#f44336',
      dark: '#c62828',
      contrastText: '#ffffff',
    },
    info: {
      main: '#0288d1',
      light: '#29b6f6',
      dark: '#01579b',
      contrastText: '#ffffff',
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  typography: {
    h1: { fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 },
    h2: { fontSize: '2rem', fontWeight: 600, lineHeight: 1.3 },
    h3: { fontSize: '1.75rem', fontWeight: 600, lineHeight: 1.4 },
    h4: { fontSize: '1.5rem', fontWeight: 500, lineHeight: 1.4 },
    h5: { fontSize: '1.25rem', fontWeight: 500, lineHeight: 1.5 },
    h6: { fontSize: '1rem', fontWeight: 500, lineHeight: 1.5 },
    body1: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', fontWeight: 400, lineHeight: 1.6 },
    caption: { fontSize: '0.75rem', fontWeight: 400, lineHeight: 1.4 },
  },
  shadows: {
    light: '0 2px 4px rgba(0,0,0,0.1)',
    medium: '0 4px 8px rgba(0,0,0,0.15)',
    heavy: '0 8px 16px rgba(0,0,0,0.2)',
  },
  borderRadius: {
    small: 4,
    medium: 8,
    large: 12,
    xlarge: 16,
  },
}

// Enhanced Typography Components
export const EnhancedTypography: React.FC<{
  variant: keyof typeof DESIGN_SYSTEM.typography
  color?: string
  children: React.ReactNode
  sx?: any
}> = ({ variant, color, children, sx }) => (
  <Typography
    sx={{
      ...DESIGN_SYSTEM.typography[variant],
      color: color || 'text.primary',
      ...sx,
    }}
  >
    {children}
  </Typography>
)

// Enhanced Card Component
export const EnhancedCard: React.FC<{
  children: React.ReactNode
  elevation?: 'light' | 'medium' | 'heavy'
  borderRadius?: 'small' | 'medium' | 'large' | 'xlarge'
  sx?: any
}> = ({ children, elevation = 'medium', borderRadius = 'medium', sx }) => (
  <Card
    sx={{
      boxShadow: DESIGN_SYSTEM.shadows[elevation],
      borderRadius: DESIGN_SYSTEM.borderRadius[borderRadius],
      transition: 'all 0.3s ease',
      '&:hover': {
        boxShadow: DESIGN_SYSTEM.shadows.heavy,
        transform: 'translateY(-2px)',
      },
      ...sx,
    }}
  >
    {children}
  </Card>
)

// Enhanced Chip Component
export const EnhancedChip: React.FC<{
  label: string
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  variant?: 'filled' | 'outlined'
  size?: 'small' | 'medium'
  icon?: React.ReactNode
  sx?: any
}> = ({ label, color = 'primary', variant = 'filled', size = 'medium', icon, sx }) => (
  <Chip
    label={label}
    color={color}
    variant={variant}
    size={size}
    icon={icon}
    sx={{
      fontWeight: 500,
      borderRadius: DESIGN_SYSTEM.borderRadius.small,
      ...sx,
    }}
  />
)

// Enhanced Progress Bar
export const EnhancedProgressBar: React.FC<{
  value: number
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  height?: number
  showLabel?: boolean
  label?: string
  sx?: any
}> = ({ value, color = 'primary', height = 8, showLabel = false, label, sx }) => (
  <Box sx={{ width: '100%', ...sx }}>
    {showLabel && (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {label || 'Progress'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {Math.round(value)}%
        </Typography>
      </Box>
    )}
    <LinearProgress
      variant="determinate"
      value={value}
      color={color}
      sx={{
        height,
        borderRadius: DESIGN_SYSTEM.borderRadius.small,
        backgroundColor: 'rgba(0,0,0,0.1)',
        '& .MuiLinearProgress-bar': {
          borderRadius: DESIGN_SYSTEM.borderRadius.small,
        },
      }}
    />
  </Box>
)

// Enhanced Avatar Component
export const EnhancedAvatar: React.FC<{
  children: React.ReactNode
  size?: 'small' | 'medium' | 'large'
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  sx?: any
}> = ({ children, size = 'medium', color = 'primary', sx }) => {
  const sizeMap = {
    small: 32,
    medium: 40,
    large: 56,
  }

  return (
    <Avatar
      sx={{
        width: sizeMap[size],
        height: sizeMap[size],
        bgcolor: `${color}.main`,
        color: `${color}.contrastText`,
        fontWeight: 600,
        boxShadow: DESIGN_SYSTEM.shadows.light,
        ...sx,
      }}
    >
      {children}
    </Avatar>
  )
}

// Enhanced Badge Component
export const EnhancedBadge: React.FC<{
  children: React.ReactNode
  badgeContent: React.ReactNode
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  sx?: any
}> = ({ children, badgeContent, color = 'primary', sx }) => (
  <Badge
    badgeContent={badgeContent}
    color={color}
    sx={{
      '& .MuiBadge-badge': {
        fontWeight: 600,
        fontSize: '0.75rem',
        ...sx,
      },
    }}
  >
    {children}
  </Badge>
)

// Enhanced Divider Component
export const EnhancedDivider: React.FC<{
  orientation?: 'horizontal' | 'vertical'
  variant?: 'fullWidth' | 'inset' | 'middle'
  sx?: any
}> = ({ orientation = 'horizontal', variant = 'fullWidth', sx }) => (
  <Divider
    orientation={orientation}
    variant={variant}
    sx={{
      borderColor: 'rgba(0,0,0,0.1)',
      ...sx,
    }}
  />
)

// Enhanced Paper Component
export const EnhancedPaper: React.FC<{
  children: React.ReactNode
  elevation?: 'light' | 'medium' | 'heavy'
  borderRadius?: 'small' | 'medium' | 'large' | 'xlarge'
  sx?: any
}> = ({ children, elevation = 'light', borderRadius = 'medium', sx }) => (
  <Paper
    elevation={0}
    sx={{
      boxShadow: DESIGN_SYSTEM.shadows[elevation],
      borderRadius: DESIGN_SYSTEM.borderRadius[borderRadius],
      ...sx,
    }}
  >
    {children}
  </Paper>
)

// Enhanced Tooltip Component
export const EnhancedTooltip: React.FC<{
  title: string
  children: React.ReactNode
  placement?: 'top' | 'bottom' | 'left' | 'right'
  sx?: any
}> = ({ title, children, placement = 'top', sx }) => (
  <Tooltip
    title={title}
    placement={placement}
    arrow
    sx={{
      '& .MuiTooltip-tooltip': {
        backgroundColor: 'rgba(0,0,0,0.8)',
        fontSize: '0.75rem',
        fontWeight: 500,
        borderRadius: DESIGN_SYSTEM.borderRadius.small,
        ...sx,
      },
    }}
  >
    {children}
  </Tooltip>
)

// Enhanced Icon Button Component
export const EnhancedIconButton: React.FC<{
  children: React.ReactNode
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  size?: 'small' | 'medium' | 'large'
  onClick?: () => void
  sx?: any
}> = ({ children, color = 'primary', size = 'medium', onClick, sx }) => (
  <IconButton
    color={color}
    size={size}
    onClick={onClick}
    sx={{
      transition: 'all 0.2s ease',
      '&:hover': {
        transform: 'scale(1.1)',
        boxShadow: DESIGN_SYSTEM.shadows.light,
      },
      ...sx,
    }}
  >
    {children}
  </IconButton>
)

// Enhanced Grid Component
export const EnhancedGrid: React.FC<{
  container?: boolean
  item?: boolean
  xs?: number
  sm?: number
  md?: number
  lg?: number
  xl?: number
  spacing?: number
  children: React.ReactNode
  sx?: any
}> = ({ container = false, item = false, xs, sm, md, lg, xl, spacing = 2, children, sx }) => (
  <Grid
    container={container}
    item={item}
    xs={xs}
    sm={sm}
    md={md}
    lg={lg}
    xl={xl}
    spacing={spacing}
    sx={sx}
  >
    {children}
  </Grid>
)

// Enhanced Box Component
export const EnhancedBox: React.FC<{
  children: React.ReactNode
  sx?: any
}> = ({ children, sx }) => (
  <Box
    sx={{
      ...sx,
    }}
  >
    {children}
  </Box>
)

// Enhanced CardContent Component
export const EnhancedCardContent: React.FC<{
  children: React.ReactNode
  sx?: any
}> = ({ children, sx }) => (
  <CardContent
    sx={{
      padding: DESIGN_SYSTEM.spacing.md,
      '&:last-child': {
        paddingBottom: DESIGN_SYSTEM.spacing.md,
      },
      ...sx,
    }}
  >
    {children}
  </CardContent>
)

export default {
  EnhancedTypography,
  EnhancedCard,
  EnhancedChip,
  EnhancedProgressBar,
  EnhancedAvatar,
  EnhancedBadge,
  EnhancedDivider,
  EnhancedPaper,
  EnhancedTooltip,
  EnhancedIconButton,
  EnhancedGrid,
  EnhancedBox,
  EnhancedCardContent,
  DESIGN_SYSTEM,
}
