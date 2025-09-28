/**
 * InteractiveRiskAssessment Component
 * Provides interactive risk assessment with visual indicators and filtering
 * Implements Phase 3: Enhanced User Experience
 */

import React, { useState, useMemo } from 'react'
import {
  Box,
  Typography,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Grid,
  Tooltip,
  IconButton,
  Alert
} from '@mui/material'
import {
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import ExpandableSection from './ExpandableSection'

export interface RiskItem {
  id: string
  text: string
  category: 'weather' | 'pest' | 'disease' | 'other'
  severity: 'low' | 'medium' | 'high'
  priority: number
  actionableAdvice?: string
  confidence?: number
}

export interface InteractiveRiskAssessmentProps {
  risks: RiskItem[]
  title?: string
  onRiskSelect?: (risk: RiskItem) => void
  showFilters?: boolean
  showPriority?: boolean
  maxDisplayed?: number
}

const severityConfig = {
  high: {
    color: 'error' as const,
    icon: <ErrorIcon />,
    label: 'High Risk',
    bgColor: 'rgba(244, 67, 54, 0.1)',
  },
  medium: {
    color: 'warning' as const,
    icon: <WarningIcon />,
    label: 'Medium Risk',
    bgColor: 'rgba(255, 152, 0, 0.1)',
  },
  low: {
    color: 'info' as const,
    icon: <InfoIcon />,
    label: 'Low Risk',
    bgColor: 'rgba(33, 150, 243, 0.1)',
  },
}

const categoryConfig = {
  weather: {
    icon: '🌦️',
    label: 'Weather',
    color: 'primary' as const,
  },
  pest: {
    icon: '🐛',
    label: 'Pest',
    color: 'secondary' as const,
  },
  disease: {
    icon: '🦠',
    label: 'Disease',
    color: 'error' as const,
  },
  other: {
    icon: '⚠️',
    label: 'Other',
    color: 'default' as const,
  },
}

const InteractiveRiskAssessment: React.FC<InteractiveRiskAssessmentProps> = ({
  risks,
  title = 'Risk Assessment',
  onRiskSelect,
  showFilters = true,
  showPriority = true,
  maxDisplayed = 10
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'priority' | 'severity' | 'category'>('priority')
  const [expandedRisks, setExpandedRisks] = useState<Set<string>>(new Set())

  // Filter and sort risks
  const filteredRisks = useMemo(() => {
    let filtered = risks

    // Apply severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(risk => risk.severity === severityFilter)
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(risk => risk.category === categoryFilter)
    }

    // Sort risks
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          return b.priority - a.priority
        case 'severity':
          const severityOrder = { high: 3, medium: 2, low: 1 }
          return severityOrder[b.severity] - severityOrder[a.severity]
        case 'category':
          return a.category.localeCompare(b.category)
        default:
          return 0
      }
    })

    return filtered.slice(0, maxDisplayed)
  }, [risks, severityFilter, categoryFilter, sortBy, maxDisplayed])

  const handleRiskToggle = (riskId: string) => {
    const newExpanded = new Set(expandedRisks)
    if (newExpanded.has(riskId)) {
      newExpanded.delete(riskId)
    } else {
      newExpanded.add(riskId)
    }
    setExpandedRisks(newExpanded)
  }

  const clearFilters = () => {
    setSeverityFilter('all')
    setCategoryFilter('all')
    setSortBy('priority')
  }

  const getRiskCategory = (risk: RiskItem) => {
    const config = severityConfig[risk.severity]
    return config
  }

  const getRiskSummary = (risk: RiskItem) => {
    const maxLength = 100
    if (risk.text.length <= maxLength) return risk.text
    return risk.text.substring(0, maxLength) + '...'
  }

  const getRiskDetails = (risk: RiskItem) => {
    const details = []
    
    if (risk.actionableAdvice) {
      details.push(`💡 Actionable Advice: ${risk.actionableAdvice}`)
    }
    
    if (risk.confidence) {
      details.push(`📊 Confidence: ${Math.round(risk.confidence * 100)}%`)
    }
    
    details.push(`🎯 Priority Score: ${risk.priority}/10`)
    
    return details.join('\n\n')
  }

  if (risks.length === 0) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Alert severity="success" icon={<CheckCircleIcon />}>
            <Typography variant="h6" gutterBottom>
              No Significant Risks Detected
            </Typography>
            <Typography variant="body2">
              Current conditions appear favorable for crop cultivation. Continue monitoring weather patterns and crop health.
            </Typography>
          </Alert>
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
          
          {showFilters && (
            <Tooltip title="Clear all filters">
              <IconButton size="small" onClick={clearFilters}>
                <ClearIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Filters */}
        {showFilters && (
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Severity</InputLabel>
                  <Select
                    value={severityFilter}
                    label="Severity"
                    onChange={(e) => setSeverityFilter(e.target.value)}
                  >
                    <MenuItem value="all">All Severities</MenuItem>
                    <MenuItem value="high">High Risk</MenuItem>
                    <MenuItem value="medium">Medium Risk</MenuItem>
                    <MenuItem value="low">Low Risk</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={categoryFilter}
                    label="Category"
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <MenuItem value="all">All Categories</MenuItem>
                    <MenuItem value="weather">Weather</MenuItem>
                    <MenuItem value="pest">Pest</MenuItem>
                    <MenuItem value="disease">Disease</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    label="Sort By"
                    onChange={(e) => setSortBy(e.target.value as any)}
                  >
                    <MenuItem value="priority">Priority</MenuItem>
                    <MenuItem value="severity">Severity</MenuItem>
                    <MenuItem value="category">Category</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Risk Statistics */}
        <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Risk Overview
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              icon={<ErrorIcon />}
              label={`${risks.filter(r => r.severity === 'high').length} High`}
              color="error"
              size="small"
            />
            <Chip
              icon={<WarningIcon />}
              label={`${risks.filter(r => r.severity === 'medium').length} Medium`}
              color="warning"
              size="small"
            />
            <Chip
              icon={<InfoIcon />}
              label={`${risks.filter(r => r.severity === 'low').length} Low`}
              color="info"
              size="small"
            />
          </Box>
        </Box>

        {/* Risk Items */}
        <Box sx={{ maxHeight: '600px', overflowY: 'auto' }}>
          {filteredRisks.map((risk, index) => {
            const config = getRiskCategory(risk)
            const categoryInfo = categoryConfig[risk.category]
            const isExpanded = expandedRisks.has(risk.id)

            return (
              <motion.div
                key={risk.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ExpandableSection
                  title={`${categoryInfo.icon} ${categoryInfo.label} Risk`}
                  summary={getRiskSummary(risk)}
                  details={getRiskDetails(risk)}
                  category={risk.severity === 'high' ? 'critical' : risk.severity === 'medium' ? 'important' : 'helpful'}
                  priority={risk.priority}
                  icon={config.icon}
                  tooltip={`Click to ${isExpanded ? 'collapse' : 'expand'} details`}
                  defaultExpanded={isExpanded}
                  onToggle={() => handleRiskToggle(risk.id)}
                >
                  {risk.actionableAdvice && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                      <Typography variant="body2" fontWeight="bold" color="primary.main" gutterBottom>
                        💡 Recommended Action:
                      </Typography>
                      <Typography variant="body2">
                        {risk.actionableAdvice}
                      </Typography>
                    </Box>
                  )}
                </ExpandableSection>
              </motion.div>
            )
          })}
        </Box>

        {/* Show More/Less */}
        {risks.length > maxDisplayed && (
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Showing {filteredRisks.length} of {risks.length} risks
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default InteractiveRiskAssessment
