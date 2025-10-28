import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import DiseaseResistanceDisplay from '../../components/Varieties/DiseaseResistanceDisplay'
import PestDiseaseManagement from '../../components/Varieties/PestDiseaseManagement'
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
        setError(null)
        
        // Convert display crop name to database name
        const databaseCropName = displayToDatabaseName(cropName)
        
        // First get all varieties for the crop
        const response = await axios.get(`/api/varieties/${databaseCropName}`)
        const varieties = response.data.varieties || []
        
        console.log('🔍 MobileVarietyDetail - Full API Response:', {
          dataSource: response.data.data_source,
          totalFound: response.data.total_found,
          varietiesReceived: varieties.length,
          firstFewVarietyNames: varieties.slice(0, 5).map((v: any) => v.name)
        })
        
        // Debug: Check the actual first variety's yield_potential
        if (varieties.length > 0) {
          console.log('🔍 MobileVarietyDetail - First variety from API:', {
            name: varieties[0].name,
            yield_potential: varieties[0].yield_potential,
            yield_potential_stringified: JSON.stringify(varieties[0].yield_potential),
            disease_resistance: varieties[0].disease_resistance,
            disease_resistance_stringified: JSON.stringify(varieties[0].disease_resistance)
          })
        }
        
        if (!Array.isArray(varieties) || varieties.length === 0) {
          throw new Error(`No varieties found for ${cropName}. The crop may not have any varieties in the database yet.`)
        }
        
        console.log('🔍 MobileVarietyDetail - Debug info:', {
          originalCropName: cropName,
          databaseCropName,
          varietyName,
          url: `/api/varieties/${databaseCropName}`,
          varietiesCount: varieties.length,
          varietyNames: varieties.map((v: any) => v.name),
          varietySlugs: varieties.map((v: any) => ({ 
            name: v.name, 
            slug: createSlug(v.name),
            matches: createSlug(v.name) === varietyName?.toLowerCase().trim()
          })),
          lookingForSlug: varietyName?.toLowerCase().trim(),
          exactMatchFound: varieties.some((v: any) => createSlug(v.name) === varietyName?.toLowerCase().trim())
        })
        
        // Find the specific variety - try multiple matching strategies
        const targetSlug = varietyName?.toLowerCase().trim()
        let variety = null
        
        // Strategy 1: Exact slug match
        variety = varieties.find((v: any) => {
          const varietySlug = createSlug(v.name)
          const matches = varietySlug === targetSlug
          if (matches) console.log(`✅ Exact slug match: "${v.name}" (slug: ${varietySlug}) === "${targetSlug}"`)
          return matches
        })
        
        // Strategy 2: Case-insensitive name match (without slug conversion)
        if (!variety) {
          variety = varieties.find((v: any) => {
            const matches = v.name.toLowerCase().trim() === varietyName.toLowerCase().trim()
            if (matches) console.log(`✅ Case-insensitive name match: "${v.name}" === "${varietyName}"`)
            return matches
          })
        }
        
        // Strategy 3: Try matching by removing non-alphanumeric from both sides
        if (!variety) {
          variety = varieties.find((v: any) => {
            const vClean = v.name.toLowerCase().replace(/[^a-z0-9]/g, '')
            const targetClean = varietyName.toLowerCase().replace(/[^a-z0-9]/g, '')
            const matches = vClean === targetClean
            if (matches) console.log(`✅ Clean match: "${v.name}" (clean: ${vClean}) === "${varietyName}" (clean: ${targetClean})`)
            return matches
          })
        }
        
        // Strategy 4: Partial match
        if (!variety) {
          variety = varieties.find((v: any) => {
            const varietySlug = createSlug(v.name)
            const normalizedVarietyName = varietyName.toLowerCase().trim().replace(/[^a-z0-9-]/g, '-')
            const matches = varietySlug.includes(normalizedVarietyName) || normalizedVarietyName.includes(varietySlug)
            if (matches) console.log(`✅ Partial match: "${v.name}" (slug: ${varietySlug}) contains "${normalizedVarietyName}" or vice versa`)
            return matches
          })
        }
        
        if (!variety) {
          const availableNames = varieties.map((v: any) => v.name).join(', ')
          console.error('🔍 MobileVarietyDetail - Variety not found. Looking for:', varietyName, 'Available:', availableNames)
          throw new Error(`Variety "${varietyName}" not found. Available: ${availableNames || 'none'}`)
        }
        
        console.log('🔍 MobileVarietyDetail - Setting variety data:', {
          name: variety.name,
          yield_potential: variety.yield_potential,
          yield_potential_type: typeof variety.yield_potential,
          yield_potential_keys: variety.yield_potential ? Object.keys(variety.yield_potential) : 'none',
          expected_yield_per_hectare: variety.expected_yield_per_hectare,
          disease_resistance: variety.disease_resistance,
          disease_resistance_type: typeof variety.disease_resistance,
          disease_resistance_keys: variety.disease_resistance ? Object.keys(variety.disease_resistance) : 'none'
        })
        
        // Parse stringified objects if they exist (fix for serialization issue)
        const varietyCopy = { ...variety }
        
        // Check if fields are objects but appear empty - might be stringified in the original
        if (varietyCopy.yield_potential) {
          // If it's a string, parse it
          if (typeof varietyCopy.yield_potential === 'string') {
            try {
              varietyCopy.yield_potential = JSON.parse(varietyCopy.yield_potential)
            } catch (e) {
              console.warn('Failed to parse yield_potential string:', e)
            }
          } 
          // If it's an empty object, check if we can find a stringified version
          else if (typeof varietyCopy.yield_potential === 'object' && Object.keys(varietyCopy.yield_potential).length === 0) {
            // Try to extract from the original variety's stringified form
            const origStr = JSON.stringify(variety)
            const match = origStr.match(/"yield_potential":\s*"({[^}]+})"/)
            if (match && match[1]) {
              try {
                varietyCopy.yield_potential = JSON.parse(match[1].replace(/\\"/g, '"'))
              } catch (e) {
                // Ignore
              }
            }
          }
        }
        
        // Same for disease_resistance
        if (varietyCopy.disease_resistance) {
          if (typeof varietyCopy.disease_resistance === 'string') {
            try {
              varietyCopy.disease_resistance = JSON.parse(varietyCopy.disease_resistance)
            } catch (e) {
              console.warn('Failed to parse disease_resistance string:', e)
            }
          }
          else if (typeof varietyCopy.disease_resistance === 'object' && Object.keys(varietyCopy.disease_resistance).length === 0) {
            const origStr = JSON.stringify(variety)
            const match = origStr.match(/"disease_resistance":\s*"({[^}]+})"/)
            if (match && match[1]) {
              try {
                varietyCopy.disease_resistance = JSON.parse(match[1].replace(/\\"/g, '"'))
              } catch (e) {
                // Ignore
              }
            }
          }
        }
        
        // Make a proper deep copy - this should preserve the parsed objects
        const finalVariety = JSON.parse(JSON.stringify(varietyCopy))
        
        console.log('🔍 MobileVarietyDetail - After parsing and copy:', {
          yield_potential: finalVariety.yield_potential,
          yield_potential_keys: finalVariety.yield_potential ? Object.keys(finalVariety.yield_potential) : 'none',
          disease_resistance: finalVariety.disease_resistance,
          disease_resistance_keys: finalVariety.disease_resistance ? Object.keys(finalVariety.disease_resistance) : 'none'
        })
        
        setVarietyData(finalVariety)
      } catch (err) {
        console.error('🔍 MobileVarietyDetail - Error:', err)
        if (axios.isAxiosError(err)) {
          const status = err.response?.status
          if (status === 404) {
            setError('Crop not found. Please go back and try selecting a different crop.')
          } else {
            setError(`Failed to load variety data: ${err.message}`)
          }
        } else {
          setError(err instanceof Error ? err.message : 'Failed to load variety data')
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchVarietyData()
  }, [cropName, varietyName])

  // Helper function to safely display object values
  const formatValue = (value: any, fallback: string = 'Not specified') => {
    if (value === null || value === undefined || value === '') return fallback
    
    // Handle empty objects - check early
    if (typeof value === 'object' && value !== null && Object.keys(value).length === 0) {
      return fallback
    }
    
    // Handle object values (like formatted disease resistance)
    if (typeof value === 'object' && value !== null) {
      // If it has a text property (our formatted objects), return that
      if ('text' in value && value.text) {
        return value.text
      }
      
      // If it has items (for disease resistance), join them
      if ('items' in value && Array.isArray(value.items) && value.items.length > 0) {
        return value.items.join(', ')
      }
      
      // For arrays, join them
      if (Array.isArray(value) && value.length > 0) {
        return value.join(', ')
      }
      
      // If object is empty or has no displayable content, return fallback
      if (Object.keys(value).length === 0) {
        return fallback
      }
      
      // Return a stringified version as last resort
      try {
        return JSON.stringify(value)
      } catch (e) {
        return fallback
      }
    }
    
    // Handle string values
    if (typeof value === 'string' && value.trim() !== '') {
      return value
    }
    
    // Convert to string for display
    return String(value) || fallback
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
                    {(() => {
                      console.log('🔍 MobileVarietyDetail - Rendering yield:', {
                        expected_yield_per_hectare: varietyData.expected_yield_per_hectare,
                        yield_potential: varietyData.yield_potential,
                        yield_potential_type: typeof varietyData.yield_potential,
                        yield_potential_keys: varietyData.yield_potential ? Object.keys(varietyData.yield_potential) : 'none'
                      });
                      
                      let yieldDisplay = 'Not specified';
                      
                      // Prioritize expected_yield_per_hectare (but only if it's a valid number)
                      if (varietyData.expected_yield_per_hectare && 
                          varietyData.expected_yield_per_hectare !== 'Not specified' && 
                          !isNaN(Number(varietyData.expected_yield_per_hectare))) {
                        yieldDisplay = `${formatValue(varietyData.expected_yield_per_hectare)} kg/ha`;
                      } 
                      // Otherwise use yield_potential (could be string like "2500 kg/ha" or object {text, level})
                      else if (varietyData.yield_potential) {
                        // Check if it's an object with text property
                        if (typeof varietyData.yield_potential === 'object' && varietyData.yield_potential !== null && 'text' in varietyData.yield_potential) {
                          yieldDisplay = varietyData.yield_potential.text || 'Not specified';
                        } else {
                          const yieldValue = formatValue(varietyData.yield_potential);
                          // If it already has units, use as-is, otherwise add kg/ha for numeric values
                          if (typeof yieldValue === 'string' && (yieldValue.includes('kg/ha') || yieldValue.includes('t/ha'))) {
                            yieldDisplay = yieldValue;
                          } else if (!isNaN(Number(yieldValue))) {
                            yieldDisplay = `${yieldValue} kg/ha`;
                          } else {
                            yieldDisplay = yieldValue;
                          }
                        }
                      }
                      
                      console.log('🔍 MobileVarietyDetail - Final yield display:', yieldDisplay);
                      return yieldDisplay;
                    })()}
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
                    {varietyData.min_rainfall_mm && varietyData.max_rainfall_mm
                      ? `${formatValue(varietyData.min_rainfall_mm)}-${formatValue(varietyData.max_rainfall_mm)} mm`
                      : formatValue(varietyData.drought_tolerance, 'Moderate')}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" align="center">
                  Rainfall Requirements
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={6}>
              <Paper elevation={0} sx={{ p: 1, bgcolor: 'warning.50', borderRadius: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
                  <BugIcon sx={{ color: 'warning.main', fontSize: 20, mb: 0.5 }} />
                  <Box>
                    <PestDiseaseManagement 
                      pestManagement={varietyData.pest_management}
                      diseaseManagement={varietyData.disease_management}
                      compact={true}
                    />
                  </Box>
                </Box>
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
            {/* Pest and Disease Management will be shown as a separate expandable section */}
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

      {/* Pest and Disease Management */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
            Pest & Disease Management
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <PestDiseaseManagement 
            pestManagement={varietyData.pest_management}
            diseaseManagement={varietyData.disease_management}
            compact={false}
          />
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
