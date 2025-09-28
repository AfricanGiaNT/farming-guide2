/**
 * SearchModeToggle Component
 * Provides toggle between "All Crops" and "Specific Crop" search modes
 * Implements Phase 4: Specific Crop Search Integration
 */

import React, { useState } from 'react'
import {
  Box,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Card,
  CardContent,
  Chip,
  Tooltip,
  IconButton,
  Collapse,
  Alert
} from '@mui/material'
import {
  Agriculture as AgricultureIcon,
  Search as SearchIcon,
  List as ListIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

export interface SearchMode {
  type: 'all_crops' | 'specific_crop'
  cropName?: string
}

export interface SearchModeToggleProps {
  searchMode: SearchMode
  onSearchModeChange: (searchMode: SearchMode) => void
  availableCrops?: string[]
  showAdvanced?: boolean
  disabled?: boolean
}

const SearchModeToggle: React.FC<SearchModeToggleProps> = ({
  searchMode,
  onSearchModeChange,
  availableCrops = [],
  showAdvanced = true,
  disabled = false
}) => {
  const [expanded, setExpanded] = useState(false)
  const [customCropName, setCustomCropName] = useState('')

  const handleModeChange = (event: React.MouseEvent<HTMLElement>, newMode: string | null) => {
    if (newMode && !disabled) {
      const newSearchMode: SearchMode = {
        type: newMode as 'all_crops' | 'specific_crop',
        cropName: newMode === 'specific_crop' ? (searchMode.cropName || '') : undefined
      }
      onSearchModeChange(newSearchMode)
    }
  }

  const handleCropNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const cropName = event.target.value.trim()
    setCustomCropName(cropName)
    
    if (searchMode.type === 'specific_crop') {
      onSearchModeChange({
        ...searchMode,
        cropName: cropName || undefined
      })
    }
  }

  const handleCropSelection = (cropName: string) => {
    setCustomCropName(cropName)
    onSearchModeChange({
      ...searchMode,
      cropName: cropName
    })
  }

  const getModeDescription = (mode: string) => {
    switch (mode) {
      case 'all_crops':
        return 'Get recommendations for all suitable crops in your area'
      case 'specific_crop':
        return 'Get detailed analysis for a specific crop only'
      default:
        return ''
    }
  }

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'all_crops':
        return <ListIcon />
      case 'specific_crop':
        return <SearchIcon />
      default:
        return <AgricultureIcon />
    }
  }

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'all_crops':
        return 'primary'
      case 'specific_crop':
        return 'secondary'
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
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Search Mode
            </Typography>
            
            {showAdvanced && (
              <Tooltip title={expanded ? 'Show less options' : 'Show more options'}>
                <IconButton
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  disabled={disabled}
                >
                  {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Tooltip>
            )}
          </Box>

          {/* Mode Selection */}
          <Box sx={{ mb: 2 }}>
            <ToggleButtonGroup
              value={searchMode.type}
              exclusive
              onChange={handleModeChange}
              aria-label="search mode"
              disabled={disabled}
              sx={{
                width: '100%',
                '& .MuiToggleButton-root': {
                  flex: 1,
                  py: 1.5,
                  px: 2,
                },
              }}
            >
              <ToggleButton value="all_crops" aria-label="all crops">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ListIcon color="primary" />
                  <Box sx={{ textAlign: 'left' }}>
                    <Typography variant="body2" fontWeight="bold">
                      All Crops
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Browse all suitable crops
                    </Typography>
                  </Box>
                </Box>
              </ToggleButton>
              
              <ToggleButton value="specific_crop" aria-label="specific crop">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SearchIcon color="secondary" />
                  <Box sx={{ textAlign: 'left' }}>
                    <Typography variant="body2" fontWeight="bold">
                      Specific Crop
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Search for one crop
                    </Typography>
                  </Box>
                </Box>
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Mode Description */}
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              {getModeDescription(searchMode.type)}
            </Typography>
          </Alert>

          {/* Specific Crop Input */}
          <AnimatePresence>
            {searchMode.type === 'specific_crop' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                style={{ overflow: 'hidden' }}
              >
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    Crop Name
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <input
                      type="text"
                      value={customCropName}
                      onChange={handleCropNameChange}
                      placeholder="Enter crop name (e.g., maize, beans, groundnuts)"
                      disabled={disabled}
                      style={{
                        flex: 1,
                        padding: '12px',
                        border: '1px solid #ccc',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontFamily: 'inherit',
                      }}
                    />
                  </Box>

                  {/* Available Crops */}
                  {availableCrops.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        Popular crops:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                        {availableCrops.slice(0, 8).map((crop) => (
                          <Chip
                            key={crop}
                            label={crop}
                            size="small"
                            variant={customCropName.toLowerCase() === crop.toLowerCase() ? 'filled' : 'outlined'}
                            color={customCropName.toLowerCase() === crop.toLowerCase() ? 'primary' : 'default'}
                            onClick={() => handleCropSelection(crop)}
                            disabled={disabled}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Validation */}
                  {searchMode.type === 'specific_crop' && !searchMode.cropName && (
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        Please enter a crop name to get specific recommendations.
                      </Typography>
                    </Alert>
                  )}
                </Box>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Advanced Options */}
          <AnimatePresence>
            {expanded && showAdvanced && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                style={{ overflow: 'hidden' }}
              >
                <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    Advanced Options
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Chip
                      icon={<InfoIcon />}
                      label="All Crops Mode"
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                    <Chip
                      icon={<SearchIcon />}
                      label="Specific Crop Mode"
                      color="secondary"
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    All Crops: Faster loading, shows multiple recommendations. 
                    Specific Crop: Detailed analysis, shows suitability even for unsuitable crops.
                  </Typography>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Current Selection Summary */}
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Current Selection:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={getModeIcon(searchMode.type)}
                label={searchMode.type === 'all_crops' ? 'All Crops' : 'Specific Crop'}
                color={getModeColor(searchMode.type) as any}
                size="small"
                variant="filled"
              />
              {searchMode.type === 'specific_crop' && searchMode.cropName && (
                <Chip
                  label={searchMode.cropName}
                  color="info"
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default SearchModeToggle
