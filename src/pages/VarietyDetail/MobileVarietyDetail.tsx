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
  IconButton,
  Breadcrumbs,
  Link,
  Alert,
  Skeleton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
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
  CalendarMonth as CalendarIcon,
  Info as InfoIcon,
  Science as FertilizerIcon,
  PestControl as PestIcon,
  Storage as StorageIcon,
  MonetizationOn as MarketIcon,
  ExpandMore as ExpandMoreIcon,
  Home as HomeIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { displayToDatabaseName } from '../../utils/cropNameMapping'
import { createSlug } from '../../utils/slugUtils'

interface MobileVarietyDetailProps {}

const MobileVarietyDetail: React.FC<MobileVarietyDetailProps> = () => {
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
        const varieties = response.data.varieties || []
        
        console.log('🔍 MobileVarietyDetail - Debug info:', {
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
        
        if (!variety) {
          throw new Error('Variety not found')
        }
        
        setVarietyData(variety)
      } catch (err) {
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
      <Box sx={{ p: 2 }}>
        <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
        <Skeleton variant="text" height={40} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" height={120} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={200} />
      </Box>
    )
  }

  if (error || !varietyData) {
    return (
      <Box sx={{ p: 2 }}>
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
    <Box sx={{ p: 2, maxWidth: 600, mx: 'auto' }}>
      {/* Simplified Breadcrumbs for Mobile */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton
          onClick={() => navigate('/varieties')}
          sx={{ mr: 1 }}
          size="small"
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="body2" color="text.secondary">
          {cropName?.replace('-', ' ')} / {varietyData.name}
        </Typography>
      </Box>

      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          {varietyData.name}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="subtitle1" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
            {cropName?.replace('-', ' ')} Variety
          </Typography>
          <Chip
            size="small"
            icon={<AgricultureIcon />}
            label={formatValue(varietyData.type, 'Standard')}
            color="primary"
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Compact Production Overview */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Production Overview
          </Typography>
          
          <Grid container spacing={1}>
            {/* First Row - 2 columns */}
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 1, bgcolor: 'primary.50', borderRadius: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
                  <ScheduleIcon sx={{ color: 'primary.main', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="h6" color="primary" align="center">
                    {formatValue(varietyData.maturity_days, '120')} days
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" align="center">
                  Maturity Period
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 1, bgcolor: 'success.50', borderRadius: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
                  <YieldIcon sx={{ color: 'success.main', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="h6" color="success.main" align="center">
                    {formatValue(varietyData.yield_potential, 'High')}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" align="center">
                  Yield Potential
                </Typography>
              </Paper>
            </Grid>
            
            {/* Second Row - 2 columns */}
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 1, bgcolor: 'info.50', borderRadius: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
                  <WaterIcon sx={{ color: 'info.main', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="h6" color="info.main" align="center">
                    {formatValue(varietyData.drought_tolerance, 'Moderate')}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" align="center">
                  Drought Tolerance
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 1, bgcolor: 'warning.50', borderRadius: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
                  <BugIcon sx={{ color: 'warning.main', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="h6" color="warning.main" align="center">
                    {formatValue(varietyData.disease_resistance, 'Good')}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" align="center">
                  Disease Resistance
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Accordion Sections for Details */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <LocationIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Planting Requirements</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <List dense disablePadding>
            <ListItem>
              <ListItemIcon>
                <CalendarIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Planting Time"
                secondary={formatValue(varietyData.planting_time, 'Seasonal planting')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <SoilIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Soil Requirements"
                secondary={formatValue(varietyData.soil_requirements, 'Well-drained loamy soil')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LocationIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Spacing"
                secondary={formatValue(varietyData.spacing_requirements, 'Standard spacing')}
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <WaterIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Growing Conditions</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <List dense disablePadding>
            <ListItem>
              <ListItemIcon>
                <WaterIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Rainfall Range"
                secondary={`${formatValue(varietyData.min_rainfall_mm, '400')} - ${formatValue(varietyData.max_rainfall_mm, '800')} mm`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Temperature Range"
                secondary={`${formatValue(varietyData.optimal_temperature_min, '20')}°C - ${formatValue(varietyData.optimal_temperature_max, '30')}°C`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <BugIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Disease Resistance"
                secondary={formatValue(varietyData.disease_resistance, 'Good resistance to common diseases')}
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FertilizerIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Required Inputs</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Fertilizers
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {formatValue(varietyData.fertilizer_requirements, 'Standard NPK fertilizer application recommended')}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Pest Management
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {formatValue(varietyData.pest_management, 'Regular monitoring and integrated pest management recommended')}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Disease Management
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {formatValue(varietyData.disease_management, 'Preventive measures and early detection recommended')}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Harvesting & Storage</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Harvesting Guidelines
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {formatValue(varietyData.harvesting_guidelines, 'Harvest when pods are dry and seeds are mature')}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Storage Requirements
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {formatValue(varietyData.storage_requirements, 'Store in cool, dry place with proper ventilation')}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <MarketIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Market Information</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Expected Yield
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.expected_yield_per_hectare, 'Not specified')}
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Market Preference
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.market_preference, 'Good market demand')}
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Seed Availability
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatValue(varietyData.seed_availability, 'Available at agricultural stores')}
              </Typography>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Source Information */}
      <Card sx={{ mt: 2 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
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

export default MobileVarietyDetail
