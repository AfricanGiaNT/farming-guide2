import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface SearchResult {
  id: string
  title: string
  content: string
  source: string
  relevanceScore: number
  category: string
  snippet: string
}

interface SearchFilters {
  category?: string
  dateRange?: {
    start: string
    end: string
  }
  qualityScore?: number
  language?: string
}

interface KnowledgeState {
  searchResults: SearchResult[]
  searchQuery: string
  searchFilters: SearchFilters
  searchHistory: string[]
  bookmarkedArticles: string[]
  categories: string[]
  selectedVariety: string | null // UI state: currently viewing variety
  selectedVarieties: string[] // For comparison mode
  loading: boolean
  error: string | null
  totalResults: number
  currentPage: number
  resultsPerPage: number
}

const initialState: KnowledgeState = {
  searchResults: [],
  searchQuery: '',
  searchFilters: {},
  searchHistory: [],
  bookmarkedArticles: [],
  selectedVariety: null,
  selectedVarieties: [],
  categories: [
    'Crop Management',
    'Pest Control',
    'Soil Health',
    'Post-Harvest',
    'Weather & Climate',
    'Varieties',
    'Planting',
    'Irrigation',
  ],
  loading: false,
  error: null,
  totalResults: 0,
  currentPage: 1,
  resultsPerPage: 10,
}

const knowledgeSlice = createSlice({
  name: 'knowledge',
  initialState,
  reducers: {
    setKnowledgeLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
      if (action.payload) {
        state.error = null
      }
    },
    setSearchResults: (state, action: PayloadAction<{
      results: SearchResult[]
      totalResults: number
      query: string
    }>) => {
      state.searchResults = action.payload.results
      state.totalResults = action.payload.totalResults
      state.searchQuery = action.payload.query
      
      // Add to search history if not already present
      if (action.payload.query && !state.searchHistory.includes(action.payload.query)) {
        state.searchHistory = [action.payload.query, ...state.searchHistory.slice(0, 9)]
      }
    },
    setSearchFilters: (state, action: PayloadAction<SearchFilters>) => {
      state.searchFilters = action.payload
    },
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload
    },
    addBookmark: (state, action: PayloadAction<string>) => {
      if (!state.bookmarkedArticles.includes(action.payload)) {
        state.bookmarkedArticles.push(action.payload)
      }
    },
    removeBookmark: (state, action: PayloadAction<string>) => {
      state.bookmarkedArticles = state.bookmarkedArticles.filter(
        id => id !== action.payload
      )
    },
    clearSearchHistory: (state) => {
      state.searchHistory = []
    },
    setKnowledgeError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.loading = false
    },
    clearKnowledgeError: (state) => {
      state.error = null
    },
    setSelectedVariety: (state, action: PayloadAction<string | null>) => {
      state.selectedVariety = action.payload
    },
    setSelectedVarieties: (state, action: PayloadAction<string[]>) => {
      state.selectedVarieties = action.payload
    },
    addSelectedVariety: (state, action: PayloadAction<string>) => {
      if (!state.selectedVarieties.includes(action.payload) && state.selectedVarieties.length < 3) {
        state.selectedVarieties.push(action.payload)
      }
    },
    removeSelectedVariety: (state, action: PayloadAction<string>) => {
      state.selectedVarieties = state.selectedVarieties.filter(v => v !== action.payload)
    },
  },
})

export const {
  setKnowledgeLoading,
  setSearchResults,
  setSearchFilters,
  setCurrentPage,
  addBookmark,
  removeBookmark,
  clearSearchHistory,
  setKnowledgeError,
  clearKnowledgeError,
  setSelectedVariety,
  setSelectedVarieties,
  addSelectedVariety,
  removeSelectedVariety,
} = knowledgeSlice.actions

export default knowledgeSlice.reducer