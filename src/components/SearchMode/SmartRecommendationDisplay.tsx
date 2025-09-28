/**
 * SmartRecommendationDisplay Component
 * Provides smart recommendation display that adapts based on search mode
 * Implements Phase 4: Specific Crop Search Integration
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  Button,
  Divider,
  CircularProgress,
  Tabs,
  Tab,
  Badge,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  Agriculture as AgricultureIcon,
  Search as SearchIcon,
  List as ListIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import EnhancedCropCard from '../ProgressiveDisclosure/EnhancedCropCard'
import InteractiveRiskAssessment from '../ProgressiveDisclosure/InteractiveRiskAssessment'
import EnhancedManagementTips from '../ProgressiveDisclosure/EnhancedManagementTips'
import { SearchMode } from './SearchModeToggle'

export interface SmartRecommendationDisplayProps {
  searchMode: SearchMode
  recommendations: any[]
  loading?: boolean
  error?: string
  onRetry?: () => void
  onFavorite?: (cropName: string) => void
  favorites?: string[]
  searchParams?: {
    location: string
    season: string
    searchMode: SearchMode
  }
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`recommendation-tabpanel-${index}`}
    aria-labelledby={`recommendation-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
)

const SmartRecommendationDisplay: React.FC<SmartRecommendationDisplayProps> = ({
  searchMode,
  recommendations = [],
  loading = false,
  error,
  onRetry,
  onFavorite,
  favorites = [],
  searchParams
}) => {
  const [activeTab, setActiveTab] = useState(0)
  const [expandedRecommendations, setExpandedRecommendations] = useState<Set<string>>(new Set())

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const handleRecommendationToggle = (cropName: string) => {
    const newExpanded = new Set(expandedRecommendations)
    if (newExpanded.has(cropName)) {
      newExpanded.delete(cropName)
    } else {
      newExpanded.add(cropName)
    }
    setExpandedRecommendations(newExpanded)
  }

  const getSearchModeIcon = () => {
    return searchMode.type === 'all_crops' ? <ListIcon /> : <SearchIcon />
  }

  const getSearchModeColor = () => {
    return searchMode.type === 'all_crops' ? 'primary' : 'secondary'
  }

  const getSearchModeLabel = () => {
    return searchMode.type === 'all_crops' ? 'All Crops' : 'Specific Crop'
  }

  const getSearchModeDescription = () => {
    if (searchMode.type === 'all_crops') {
      return `Showing ${recommendations.length} crop recommendations for your area`
    } else {
      return `Detailed analysis for ${searchMode.cropName || 'selected crop'}`
    }
  }

  const renderAllCropsMode = () => {
    if (recommendations.length === 0) {
      return (
        <Alert severity="info" icon={<InfoIcon />}>
          <Typography variant="h6" gutterBottom>
            No Crop Recommendations Found
          </Typography>
          <Typography variant="body2">
            No suitable crops were found for the current location and season. Try adjusting your search parameters.
          </Typography>
        </Alert>
      )
    }

    return (
      <Box>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Crop Recommendations ({recommendations.length})
        </Typography>
        
        <Grid container spacing={2}>
          {recommendations.map((crop, index) => (
            <Grid item xs={12} key={crop.crop_name}>
              <EnhancedCropCard
                crop={crop}
                rank={index + 1}
                onFavorite={onFavorite}
                isFavorite={favorites.includes(crop.crop_name)}
                showDetails={true}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  const renderSpecificCropMode = () => {
    if (recommendations.length === 0) {
      return (
        <Alert severity="warning" icon={<WarningIcon />}>
          <Typography variant="h6" gutterBottom>
            Crop Not Found
          </Typography>
          <Typography variant="body2">
            No information was found for "{searchMode.cropName}". This crop may not be suitable for your location and season, or it may not be in our database.
          </Typography>
        </Alert>
      )
    }

    const crop = recommendations[0] // Specific crop mode returns only one recommendation
    
    return (
      <Box>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Detailed Analysis: {crop.crop_name?.charAt(0).toUpperCase() + crop.crop_name?.slice(1)}
        </Typography>
        
        <Grid container spacing={3}>
          {/* Main Crop Card */}
          <Grid item xs={12}>
            <EnhancedCropCard
              crop={crop}
              rank={1}
              onFavorite={onFavorite}
              isFavorite={favorites.includes(crop.crop_name)}
              showDetails={true}
              compact={false}
            />
          </Grid>
        </Grid>
      </Box>
    )
  }

  const renderRiskAssessment = () => {
    // Extract risk assessment from the first recommendation or from the data structure
    const riskData = recommendations[0]?.risk_assessment || recommendations[0]?.risk_assessment
    
    if (!riskData || !riskData.weather_risks) {
      return (
        <Alert severity="info" icon={<InfoIcon />}>
          <Typography variant="h6" gutterBottom>
            No Risk Assessment Available
          </Typography>
          <Typography variant="body2">
            Risk assessment information is not available for the current search.
          </Typography>
        </Alert>
      )
    }

    const riskItems = riskData.weather_risks.map((risk: any, index: number) => ({
      id: `risk-${index}`,
      text: typeof risk === 'string' ? risk : risk.text || risk,
      category: 'weather' as const,
      severity: 'medium' as const,
      priority: 5,
    }))

    return (
      <InteractiveRiskAssessment
        risks={riskItems}
        title="Risk Assessment"
        showFilters={true}
        showPriority={true}
      />
    )
  }

  const renderManagementTips = () => {
    // Extract management tips from the first recommendation or from the data structure
    const tipsData = recommendations[0]?.management_tips || recommendations[0]?.management_tips
    
    if (!tipsData || tipsData.length === 0) {
      return (
        <Alert severity="info" icon={<InfoIcon />}>
          <Typography variant="h6" gutterBottom>
            No Management Tips Available
          </Typography>
          <Typography variant="body2">
            Management tips are not available for the current search.
          </Typography>
        </Alert>
      )
    }

    const categorizedTips = {
      planting: tipsData.filter((tip: string) => tip.toLowerCase().includes('plant')),
      maintenance: tipsData.filter((tip: string) => tip.toLowerCase().includes('maintain') || tip.toLowerCase().includes('care')),
      harvest: tipsData.filter((tip: string) => tip.toLowerCase().includes('harvest')),
      general: tipsData.filter((tip: string) => !tip.toLowerCase().includes('plant') && !tip.toLowerCase().includes('maintain') && !tip.toLowerCase().includes('harvest')),
    }

    return (
      <EnhancedManagementTips
        tips={categorizedTips}
        title="Management Tips"
        showIcons={true}
        showPriority={true}
      />
    )
  }

  const renderLoadingState = () => (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
      <CircularProgress size={60} />
      <Typography variant="h6" sx={{ mt: 2 }}>
        {searchMode.type === 'all_crops' ? 'Loading crop recommendations...' : `Analyzing ${searchMode.cropName}...`}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        This may take a few moments
      </Typography>
    </Box>
  )

  const renderErrorState = () => (
    <Alert severity="error" icon={<ErrorIcon />}>
      <Typography variant="h6" gutterBottom>
        Error Loading Recommendations
      </Typography>
      <Typography variant="body2" gutterBottom>
        {error || 'An unexpected error occurred while loading crop recommendations.'}
      </Typography>
      {onRetry && (
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onRetry}
          sx={{ mt: 2 }}
        >
          Try Again
        </Button>
      )}
    </Alert>
  )

  if (loading) {
    return renderLoadingState()
  }

  if (error) {
    return renderErrorState()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Badge badgeContent={recommendations.length} color={getSearchModeColor()}>
                {getSearchModeIcon()}
              </Badge>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {getSearchModeLabel()} Results
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {getSearchModeDescription()}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Share results">
                <IconButton size="small">
                  <ShareIcon />
                </IconButton>
              </Tooltip>
              {onRetry && (
                <Tooltip title="Refresh results">
                  <IconButton size="small" onClick={onRetry}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Search Parameters Summary */}
          {searchParams && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Search Parameters
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label={searchParams.location} size="small" variant="outlined" />
                <Chip label={searchParams.season} size="small" variant="outlined" />
                <Chip 
                  label={searchParams.searchMode.type === 'all_crops' ? 'All Crops' : `Specific: ${searchParams.searchMode.cropName}`} 
                  size="small" 
                  variant="outlined" 
                  color={getSearchModeColor()}
                />
              </Box>
            </Box>
          )}

          {/* Tabs for Different Views */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="recommendation tabs">
              <Tab 
                label="Recommendations" 
                icon={<AgricultureIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="Risk Assessment" 
                icon={<WarningIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="Management Tips" 
                icon={<CheckCircleIcon />} 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <TabPanel value={activeTab} index={0}>
            {searchMode.type === 'all_crops' ? renderAllCropsMode() : renderSpecificCropMode()}
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {renderRiskAssessment()}
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            {renderManagementTips()}
          </TabPanel>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default SmartRecommendationDisplay
