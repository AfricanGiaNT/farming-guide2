import React, { Suspense, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useDispatch } from 'react-redux'
import { setUserLocation } from './store/slices/userSlice'
import Layout from './components/Layout/Layout'
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary'

// Lazy load pages for better performance
const Dashboard = React.lazy(() => import('./pages/Dashboard/Dashboard'))
const Weather = React.lazy(() => import('./pages/Weather/Weather'))
const CropRecommendations = React.lazy(() => import('./pages/CropRecommendations/CropRecommendations'))
const Varieties = React.lazy(() => import('./pages/Varieties/Varieties'))
const ResponsiveVarietyDetail = React.lazy(() => import('./pages/VarietyDetail/ResponsiveVarietyDetail'))
const KnowledgeBase = React.lazy(() => import('./pages/KnowledgeBase/KnowledgeBase'))
const MyFarm = React.lazy(() => import('./pages/MyFarm/MyFarm'))
const Analytics = React.lazy(() => import('./pages/Analytics/Analytics'))
const AdminVarieties = React.lazy(() => import('./pages/Admin/AdminVarieties'))

// Loading component
const PageLoader = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="60vh"
    flexDirection="column"
    gap={2}
  >
    <CircularProgress size={40} />
    <Box color="text.secondary">Loading...</Box>
  </Box>
)

function App() {
  const dispatch = useDispatch()

  useEffect(() => {
    // Get user's location on app load
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          dispatch(setUserLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
            accuracy: position.coords.accuracy,
          }))
        },
        (error) => {
          console.warn('Location access denied:', error)
          // Default to Lilongwe coordinates
          dispatch(setUserLocation({
            lat: -13.9833,
            lon: 33.7833,
            accuracy: null,
          }))
        },
        {
          enableHighAccuracy: false,
          timeout: 10000,
          maximumAge: 300000, // 5 minutes
        }
      )
    } else {
      // Fallback to Lilongwe coordinates
      dispatch(setUserLocation({
        lat: -13.9833,
        lon: 33.7833,
        accuracy: null,
      }))
    }
  }, [dispatch])

  return (
    <ErrorBoundary>
      <Layout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/crops" element={<CropRecommendations />} />
            <Route path="/varieties" element={<Varieties />} />
            <Route path="/varieties/:cropName/:varietyName" element={<ResponsiveVarietyDetail />} />
            <Route path="/knowledge" element={<KnowledgeBase />} />
            <Route path="/farm" element={<MyFarm />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/admin/varieties" element={<AdminVarieties />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </Layout>
    </ErrorBoundary>
  )
}

export default App