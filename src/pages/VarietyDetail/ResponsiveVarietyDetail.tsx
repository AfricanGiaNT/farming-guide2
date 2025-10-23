import React from 'react'
import { useMediaQuery, useTheme } from '@mui/material'
import VarietyDetail from './VarietyDetail'
import MobileVarietyDetail from './MobileVarietyDetail'

/**
 * Responsive wrapper component that renders either the mobile or desktop
 * version of the VarietyDetail component based on screen size
 */
const ResponsiveVarietyDetail: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  return isMobile ? <MobileVarietyDetail /> : <VarietyDetail />
}

export default ResponsiveVarietyDetail
