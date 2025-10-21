import React, { useState, useEffect } from 'react'
import {
  Box,
  TextField,
  Button,
  Typography,
  Chip,
  useTheme,
  useMediaQuery,
  InputAdornment,
  IconButton,
  Collapse,
  Fade,
  Paper,
  Stack,
} from '@mui/material'
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material'

interface CropSearchProps {
  onSearch: (cropName: string) => void
  onClear: () => void
  onGetRecommendations?: () => void
  isLoading?: boolean
  currentCrop?: string
  isSearchMode?: boolean // New prop to indicate if we're in search mode
}

const CropSearch: React.FC<CropSearchProps> = ({
  onSearch,
  onClear,
  onGetRecommendations,
  isLoading = false,
  currentCrop,
  isSearchMode = false
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [searchTerm, setSearchTerm] = useState(currentCrop || '')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  // Update search term when currentCrop changes
  useEffect(() => {
    setSearchTerm(currentCrop || '')
  }, [currentCrop])

  // Popular crops for suggestions - organized by category
  const popularCrops = {
    'Staple Crops': ['Maize', 'Cassava', 'Sweet Potato', 'Rice', 'Sorghum'],
    'Legumes': ['Beans', 'Groundnuts', 'Soybeans', 'Cowpeas', 'Pigeon Peas'],
    'Vegetables': ['Tomatoes', 'Onions', 'Cabbage', 'Lettuce', 'Carrots'],
    'Cash Crops': ['Tobacco', 'Cotton', 'Sugarcane', 'Coffee', 'Tea']
  }

  const allCrops = Object.values(popularCrops).flat()

  const handleSearch = () => {
    if (searchTerm.trim()) {
      onSearch(searchTerm.trim())
      setShowSuggestions(false)
    } else if (onGetRecommendations) {
      onGetRecommendations()
    }
  }

  const handleClear = () => {
    setSearchTerm('')
    onClear()
    setShowSuggestions(false)
  }

  const handleSuggestionClick = (crop: string) => {
    setSearchTerm(crop)
    onSearch(crop)
    setShowSuggestions(false)
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch()
    }
  }

  const handleFocus = () => {
    setIsFocused(true)
    if (searchTerm.length > 0) {
      setShowSuggestions(true)
    }
  }

  const handleBlur = () => {
    setIsFocused(false)
    // Delay hiding suggestions to allow clicks
    setTimeout(() => setShowSuggestions(false), 150)
  }

  const filteredSuggestions = allCrops.filter(crop =>
    crop.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, 8)

  const showBackToGeneral = isSearchMode && searchTerm

  return (
    <Box>
      {/* Global CSS fix for cursor visibility */}
      <style>
        {`
          .crop-search-input input {
            cursor: text !important;
            caret-color: ${theme.palette.text.primary} !important;
          }
          .crop-search-input input:focus {
            cursor: text !important;
            caret-color: ${theme.palette.text.primary} !important;
          }
          .crop-search-input input:hover {
            cursor: text !important;
          }
        `}
      </style>
      
      {/* Modern Search Interface */}
      <Paper
        elevation={isFocused ? 2 : 0}
        sx={{
          borderRadius: 3,
          border: `2px solid ${isFocused ? theme.palette.primary.main : 'transparent'}`,
          backgroundColor: 'white',
          transition: 'all 0.2s ease-in-out',
          overflow: 'hidden',
          cursor: 'default',
          '&:hover': {
            cursor: 'default',
          },
        }}
      >
        <Box 
          display="flex" 
          alignItems="center"
          sx={{
            p: isMobile ? 1.5 : 2,
            gap: 1,
          }}
        >
          <TextField
            fullWidth
            placeholder={isSearchMode ? "Search for a specific crop..." : "Search crops or get recommendations..."}
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setShowSuggestions(e.target.value.length > 0)
            }}
            onKeyPress={handleKeyPress}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={isLoading}
            variant="outlined"
            autoComplete="off"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon 
                    fontSize={isMobile ? "small" : "medium"} 
                    color={isFocused ? "primary" : "action"} 
                  />
                </InputAdornment>
              ),
              endAdornment: searchTerm && (
                <InputAdornment position="end">
                  <IconButton
                    size="small"
                    onClick={handleClear}
                    edge="end"
                    sx={{ 
                      p: 0.5,
                      '&:hover': {
                        backgroundColor: theme.palette.grey[100],
                      }
                    }}
                  >
                    <ClearIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            className="crop-search-input"
            sx={{
              fontSize: isMobile ? '0.9rem' : '1rem',
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'transparent',
                fontSize: isMobile ? '0.9rem' : '1rem',
                '& fieldset': {
                  border: 'none',
                },
                '&:hover fieldset': {
                  border: 'none',
                },
                '&.Mui-focused fieldset': {
                  border: 'none',
                },
                '& .MuiInputBase-input': {
                  fontSize: isMobile ? '0.9rem' : '1rem',
                  py: 0.5,
                  cursor: 'text !important',
                  caretColor: theme.palette.text.primary,
                  '&:focus': {
                    cursor: 'text !important',
                    caretColor: theme.palette.text.primary,
                  },
                  '&:hover': {
                    cursor: 'text !important',
                  },
                },
              },
            }}
          />
          
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={isLoading}
            sx={{
              minWidth: isMobile ? 60 : 80,
              height: isMobile ? 36 : 40,
              fontSize: isMobile ? '0.8rem' : '0.9rem',
              fontWeight: 600,
              borderRadius: 2,
              px: 2,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              '&:hover': {
                background: `linear-gradient(45deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                transform: 'translateY(-1px)',
              },
              '&:active': {
                transform: 'translateY(0)',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            {isLoading ? '...' : (searchTerm.trim() ? 'Search' : 'Go')}
          </Button>
        </Box>

        {/* Back to General Recommendations */}
        {showBackToGeneral && (
          <Fade in={showBackToGeneral}>
            <Box
              sx={{
                px: 2,
                pb: 1,
                borderTop: `1px solid ${theme.palette.grey[200]}`,
                backgroundColor: theme.palette.grey[50],
              }}
            >
              <Button
                fullWidth
                variant="text"
                startIcon={<TrendingUpIcon />}
                onClick={handleClear}
                sx={{
                  fontSize: '0.8rem',
                  color: theme.palette.text.secondary,
                  textTransform: 'none',
                  py: 0.5,
                  '&:hover': {
                    backgroundColor: theme.palette.grey[100],
                    color: theme.palette.text.primary,
                  },
                }}
              >
                View all crop recommendations
              </Button>
            </Box>
          </Fade>
        )}
      </Paper>

      {/* Enhanced Suggestions */}
      <Collapse in={showSuggestions && filteredSuggestions.length > 0}>
        <Box mt={1.5}>
          <Paper
            elevation={2}
            sx={{
              borderRadius: 2,
              p: 1.5,
              backgroundColor: 'white',
              border: `1px solid ${theme.palette.grey[200]}`,
            }}
          >
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ 
                display: 'block', 
                mb: 1,
                fontWeight: 500,
                fontSize: '0.75rem',
              }}
            >
              Popular crops:
            </Typography>
            <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
              {filteredSuggestions.map((crop) => (
                <Chip
                  key={crop}
                  label={crop}
                  onClick={() => handleSuggestionClick(crop)}
                  variant="outlined"
                  size="small"
                  sx={{
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    height: 24,
                    mb: 0.5,
                    borderColor: theme.palette.grey[300],
                    '&:hover': {
                      backgroundColor: theme.palette.primary.light,
                      color: 'white',
                      borderColor: theme.palette.primary.light,
                      transform: 'scale(1.05)',
                    },
                    transition: 'all 0.2s ease-in-out',
                  }}
                />
              ))}
            </Stack>
          </Paper>
        </Box>
      </Collapse>
    </Box>
  )
}

export default CropSearch
