import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  BottomNavigation as MuiBottomNavigation,
  BottomNavigationAction,
  Paper,
} from '@mui/material'
import {
  Home as HomeIcon,
  WbSunny as WeatherIcon,
  Agriculture as CropIcon,
  Agriculture as VarietyIcon,
  MenuBook as KnowledgeIcon,
} from '@mui/icons-material'

const bottomNavItems = [
  { path: '/', label: 'Home', icon: HomeIcon },
  { path: '/weather', label: 'Weather', icon: WeatherIcon },
  { path: '/crops', label: 'Crops', icon: CropIcon },
  { path: '/varieties', label: 'Varieties', icon: VarietyIcon },
  { path: '/knowledge', label: 'Knowledge', icon: KnowledgeIcon },
]

const BottomNavigation: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const currentIndex = bottomNavItems.findIndex(item => item.path === location.pathname)

  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    navigate(bottomNavItems[newValue].path)
  }

  return (
    <Paper 
      sx={{ 
        position: 'fixed', 
        bottom: 0, 
        left: 0, 
        right: 0, 
        zIndex: 1000,
        borderTop: 1,
        borderColor: 'divider',
      }} 
      elevation={8}
    >
      <MuiBottomNavigation
        value={currentIndex}
        onChange={handleChange}
        showLabels
        sx={{
          '& .MuiBottomNavigationAction-root': {
            minWidth: 'auto',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          },
        }}
      >
        {bottomNavItems.map((item) => {
          const Icon = item.icon
          return (
            <BottomNavigationAction
              key={item.path}
              label={item.label}
              icon={<Icon />}
            />
          )
        })}
      </MuiBottomNavigation>
    </Paper>
  )
}

export default BottomNavigation