import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Chip,
  CircularProgress,
  Alert,
  InputAdornment,
  IconButton
} from '@mui/material'
import { Search, BookOpen, FilterList } from '@mui/icons-material'
import { knowledgeAPI } from '../../services/api'

interface SearchResult {
  title: string
  content: string
  source: string
  category: string
  relevance_score: number
}

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [categories] = useState([
    { id: 'crops', name: 'Crops', count: 245 },
    { id: 'pest_control', name: 'Pest Control', count: 156 },
    { id: 'soil_management', name: 'Soil Management', count: 189 },
    { id: 'weather', name: 'Weather', count: 98 },
    { id: 'markets', name: 'Markets', count: 67 },
    { id: 'post_harvest', name: 'Post-Harvest', count: 101 }
  ])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    setError(null)

    try {
      const results = await knowledgeAPI.searchDocuments(searchQuery)
      setSearchResults(results.results || [])
    } catch (err) {
      setError('Failed to search knowledge base. Please try again.')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
        Knowledge Base
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Search our comprehensive agricultural knowledge base for farming guidance, best practices, and expert advice.
      </Typography>

      {/* Search Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              placeholder="Search for farming advice, crop information, pest control methods..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={loading || !searchQuery.trim()}
              sx={{ minWidth: 120 }}
            >
              {loading ? <CircularProgress size={20} /> : 'Search'}
            </Button>
          </Box>

          {/* Categories */}
          <Box>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList fontSize="small" />
              Browse Categories
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {categories.map((category) => (
                <Chip
                  key={category.id}
                  label={`${category.name} (${category.count})`}
                  variant="outlined"
                  onClick={() => setSearchQuery(category.name)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Search Results ({searchResults.length})
          </Typography>
          <Grid container spacing={2}>
            {searchResults.map((result, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <BookOpen fontSize="small" color="primary" />
                      <Typography variant="subtitle2" color="primary">
                        {result.category}
                      </Typography>
                      <Chip 
                        label={`${Math.round(result.relevance_score * 100)}%`} 
                        size="small" 
                        color="success"
                      />
                    </Box>
                    
                    <Typography variant="h6" gutterBottom>
                      {result.title}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {result.content.length > 200 
                        ? `${result.content.substring(0, 200)}...` 
                        : result.content
                      }
                    </Typography>
                    
                    <Typography variant="caption" color="text.secondary">
                      Source: {result.source}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* No Results */}
      {searchResults.length === 0 && !loading && searchQuery && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <BookOpen sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No results found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try different keywords or browse our categories above
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Initial State */}
      {searchResults.length === 0 && !searchQuery && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <BookOpen sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Welcome to the Knowledge Base
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Search for agricultural guidance, crop information, pest control methods, and more.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start by typing your question above or browse our categories.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default KnowledgeBase
