import React, { useState } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  useTheme,
  useMediaQuery,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  WbSunny as WeatherIcon,
  Agriculture as CropIcon,
  Agriculture as VarietyIcon,
  MenuBook as KnowledgeIcon,
  Dashboard as FarmIcon,
  Analytics as AnalyticsIcon,
  Notifications as NotificationIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import BottomNavigation from './BottomNavigation'

interface LayoutProps {
  children: React.ReactNode
}

const navigationItems = [
  { path: '/', label: 'Home', icon: HomeIcon },
  { path: '/weather', label: 'Weather', icon: WeatherIcon },
  { path: '/crops', label: 'Crops', icon: CropIcon },
  { path: '/varieties', label: 'Varieties', icon: VarietyIcon },
  { path: '/knowledge', label: 'Knowledge', icon: KnowledgeIcon },
  { path: '/farm', label: 'My Farm', icon: FarmIcon },
  { path: '/analytics', label: 'Analytics', icon: AnalyticsIcon },
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const location = useLocation()

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen)
  }

  const handleNavigation = (path: string) => {
    navigate(path)
    if (isMobile) {
      setDrawerOpen(false)
    }
  }

  const drawer = (
    <Box sx={{ width: 280 }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" color="primary" fontWeight="bold">
          🌾 Mlangizi wa Ulimi
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Agricultural Advisory
        </Typography>
      </Box>
      <List>
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive}
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  mb: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ color: isActive ? 'white' : 'inherit' }}>
                  <Icon />
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, #2E7D32 0%, #388E3C 100%)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            🌾 Mlangizi wa Ulimi
          </Typography>
          
          <IconButton color="inherit">
            <Badge badgeContent={2} color="error">
              <NotificationIcon />
            </Badge>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? drawerOpen : true}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            mt: { md: 8 }, // Account for app bar on desktop
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 1, sm: 2, md: 3 },
          mt: 8, // Account for app bar
          ml: { md: '280px' }, // Account for drawer on desktop
          mb: { xs: 7, md: 0 }, // Account for bottom navigation on mobile
        }}
      >
        {children}
      </Box>

      {/* Bottom Navigation for Mobile */}
      {isMobile && <BottomNavigation />}
    </Box>
  )
}

export default Layout