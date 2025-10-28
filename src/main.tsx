import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Box, CircularProgress } from '@mui/material'
import { store, persistor } from './store/store'
import App from './App'
import { registerSW } from './utils/serviceWorker'
import { clearExpiredCache } from './utils/persistentStorage'

// Create Material-UI theme with agricultural colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // Agriculture Green
      light: '#4CAF50',
      dark: '#1B5E20',
    },
    secondary: {
      main: '#1976D2', // Weather Blue
      light: '#42A5F5',
      dark: '#0D47A1',
    },
    warning: {
      main: '#F57C00', // Alert Orange
    },
    success: {
      main: '#388E3C', // Success Green
    },
    error: {
      main: '#D32F2F', // Error Red
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
      fontSize: '2.125rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 500,
      fontSize: '1.75rem',
      lineHeight: 1.2,
    },
    body1: {
      lineHeight: 1.5,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
})

// Create React Query client with extended cache time to match redux-persist
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 12 * 60 * 60 * 1000, // 12 hours - matches redux-persist cache
      cacheTime: 12 * 60 * 60 * 1000, // 12 hours
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

// Register service worker for PWA functionality
registerSW()

// Clear expired cache on app start
clearExpiredCache()

// Debug: Inspect cache on startup (remove in production)
if (process.env.NODE_ENV === 'development') {
  import('./utils/cacheDebug').then(({ inspectCache }) => {
    setTimeout(() => inspectCache(), 2000) // Wait for rehydration
  })
}

// Loading component for PersistGate
const PersistLoading = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    flexDirection="column"
    gap={2}
  >
    <CircularProgress size={40} />
    <Box color="text.secondary">Loading your data...</Box>
  </Box>
)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={<PersistLoading />} persistor={persistor}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <App />
            </ThemeProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </PersistGate>
    </Provider>
  </React.StrictMode>,
)