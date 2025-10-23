import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Skeleton,
  IconButton,
  Breadcrumbs,
  Link,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Agriculture as AgricultureIcon,
  Schedule as ScheduleIcon,
  TrendingUp as YieldIcon,
  WaterDrop as WaterIcon,
  BugReport as BugIcon,
  Landscape as SoilIcon,
  LocationOn as LocationIcon,
  Grass as CropIcon,
  LocalFlorist as PlantingIcon,
  Handyman as ToolsIcon,
  Storage as StorageIcon,
  MonetizationOn as MarketIcon,
  CheckCircle as CheckCircleIcon,
  Science as FertilizerIcon,
  PestControl as PestIcon,
  LocalShipping as TransportIcon,
  CalendarMonth as CalendarIcon,
  Info as InfoIcon,
  Home as HomeIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { displayToDatabaseName } from '../../utils/cropNameMapping'
import { createSlug } from '../../utils/slugUtils'

interface VarietyDetailProps {}

const VarietyDetail: React.FC<VarietyDetailProps> = () => {
  const { cropName, varietyName } = useParams<{ cropName: string; varietyName: string }>()
  const navigate = useNavigate()
  const [varietyData, setVarietyData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchVarietyData = async () => {
      if (!cropName || !varietyName) return
      
      try {
        setIsLoading(true)
        
        // Convert display crop name to database name
        const databaseCropName = displayToDatabaseName(cropName)
        
        // First get all varieties for the crop
        const response = await axios.get(`/api/varieties/${databaseCropName}`)
        console.log('🔍 VarietyDetail - API response:', response.data)
        const varieties = response.data.varieties || []
        
        console.log('🔍 VarietyDetail - Debug info:', {
          originalCropName: cropName,
          databaseCropName,
          varietyName,
          url: `/api/varieties/${databaseCropName}`,
          varietiesCount: varieties.length,
          varietyNames: varieties.map(v => v.name),
          varietySlugs: varieties.map(v => ({ name: v.name, slug: createSlug(v.name) }))
        })
        
        // Find the specific variety
        const variety = varieties.find((v: any) => {
          const varietySlug = createSlug(v.name)
          return varietySlug === varietyName?.toLowerCase()
        })
        
        console.log('🔍 VarietyDetail - Found variety:', variety)
        
        if (!variety) {
          console.error('🔍 VarietyDetail - Variety not found. Available varieties:', varieties.map(v => v.name))
          throw new Error('Variety not found')
        }
        
        setVarietyData(variety)
      } catch (err) {
        console.error('🔍 VarietyDetail - Error:', err)
        setError(err instanceof Error ? err.message : 'Failed to load variety data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchVarietyData()
  }, [cropName, varietyName])

  const formatValue = (value: any, fallback: string = 'Not specified') => {
    if (value === null || value === undefined || value === '') return fallback
    return value
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={200} sx={{ mb: 2 }} />
        <Skeleton variant="text" height={40} sx={{ mb: 1 }} />
        <Skeleton variant="text" height={30} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={300} />
      </Box>
    )
  }

  if (error || !varietyData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Unable to load variety details. Please try again.
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/varieties')}
        >
          Back to Varieties
        </Button>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/')}
          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
        >
          <HomeIcon fontSize="small" />
          Home
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/varieties')}
        >
          Varieties
        </Link>
        <Typography color="text.primary" sx={{ textTransform: 'capitalize' }}>
          {cropName?.replace('-', ' ')}
        </Typography>
        <Typography color="text.primary" fontWeight="bold">
          {varietyData.name}
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton
          onClick={() => navigate('/varieties')}
          sx={{ mr: 2 }}
        >
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {varietyData.name}
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
            {cropName?.replace('-', ' ')} Variety
          </Typography>
        </Box>
        <Chip
          icon={<AgricultureIcon />}
          label={formatValue(varietyData.type, 'Standard')}
          color="primary"
          variant="outlined"
        />
      </Box>

      {/* Production Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CalendarIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Production Overview</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.50', borderRadius: 2 }}>
                <ScheduleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h6" color="primary">
                  {formatValue(varietyData.maturity_days, '120')} days
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Maturity Period
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.50', borderRadius: 2 }}>
                <YieldIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                <Typography variant="h6" color="success.main">
                  {formatValue(varietyData.yield_potential, 'High')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Yield Potential
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.50', borderRadius: 2 }}>
                <WaterIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                <Typography variant="h6" color="info.main">
                  {formatValue(varietyData.drought_tolerance, 'Moderate')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Drought Tolerance
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.50', borderRadius: 2 }}>
                <BugIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Typography variant="h6" color="warning.main">
                  {formatValue(varietyData.disease_resistance, 'Good')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Disease Resistance
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Production Guide */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PlantingIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Detailed Production Guide</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Planting Requirements
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Planting Time"
                    secondary={formatValue(varietyData.planting_time, 'Seasonal planting')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SoilIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Soil Requirements"
                    secondary={formatValue(varietyData.soil_requirements, 'Well-drained loamy soil')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <LocationIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Spacing"
                    secondary={formatValue(varietyData.spacing_requirements, 'Standard spacing')}
                  />
                </ListItem>
              </List>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Growing Conditions
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <WaterIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Rainfall Range"
                    secondary={`${formatValue(varietyData.min_rainfall_mm, '400')} - ${formatValue(varietyData.max_rainfall_mm, '800')} mm`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Temperature Range"
                    secondary={`${formatValue(varietyData.optimal_temperature_min, '20')}°C - ${formatValue(varietyData.optimal_temperature_max, '30')}°C`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <BugIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Disease Resistance"
                    secondary={formatValue(varietyData.disease_resistance, 'Good resistance to common diseases')}
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Required Inputs */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <FertilizerIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Required Inputs</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Fertilizers
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.fertilizer_requirements, 'Standard NPK fertilizer application recommended')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Pest Management
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.pest_management, 'Regular monitoring and integrated pest management recommended')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Disease Management
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.disease_management, 'Preventive measures and early detection recommended')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Seed Rate
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.seed_rate_per_hectare, 'Standard seed rate per hectare')}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Harvesting & Storage */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Harvesting & Storage</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Harvesting Guidelines
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.harvesting_guidelines, 'Harvest when pods are dry and seeds are mature')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Storage Requirements
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatValue(varietyData.storage_requirements, 'Store in cool, dry place with proper ventilation')}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Market Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <MarketIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Market Information</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Expected Yield
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.expected_yield_per_hectare, 'Not specified')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Market Preference
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.market_preference, 'Good market demand')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Seed Availability
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.seed_availability, 'Available at agricultural stores')}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Source Information */}
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            <strong>Source:</strong> {formatValue(varietyData.source_document, 'Agricultural Database')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Confidence Score:</strong> {formatValue(varietyData.extraction_confidence, '0')}/100
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default VarietyDetail
