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
  Paper,
} from '@mui/material'
import DiseaseResistanceDisplay from '../../components/Varieties/DiseaseResistanceDisplay'
import PestDiseaseManagement from '../../components/Varieties/PestDiseaseManagement'
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
  Eco as EcoIcon,
  DriveEta as TractorIcon,
  LocalFlorist as ManureIcon,
  Agriculture as SproutIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { displayToDatabaseName } from '../../utils/cropNameMapping'
import { createSlug } from '../../utils/slugUtils'
import { extractKeyPoints } from '../../utils/extractKeyPoints'

interface VarietyDetailProps {}

const VarietyDetail: React.FC<VarietyDetailProps> = () => {
  const { cropName, varietyName } = useParams<{ cropName: string; varietyName: string }>()
  const navigate = useNavigate()
  const [varietyData, setVarietyData] = useState<any>(null)
  const [cropProductionInfo, setCropProductionInfo] = useState<any>(null)
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
        console.log('🔍 VarietyDetail - API response:', response.data)
        const varieties = response.data.varieties || []
        
        if (!Array.isArray(varieties) || varieties.length === 0) {
          throw new Error(`No varieties found for ${cropName}. The crop may not have any varieties in the database yet.`)
        }
        
        console.log('🔍 VarietyDetail - Debug info:', {
          originalCropName: cropName,
          databaseCropName,
          varietyName,
          url: `/api/varieties/${databaseCropName}`,
          varietiesCount: varieties.length,
          varietyNames: varieties.map(v => v.name),
          varietySlugs: varieties.map(v => ({ name: v.name, slug: createSlug(v.name) }))
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
        
        console.log('🔍 VarietyDetail - Found variety:', variety)
        
        if (!variety) {
          const availableNames = varieties.map((v: any) => v.name).join(', ')
          console.error('🔍 VarietyDetail - Variety not found. Looking for:', varietyName, 'Available:', availableNames)
          throw new Error(`Variety "${varietyName}" not found. Available varieties: ${availableNames || 'none'}`)
        }
        
        console.log('🔍 VarietyDetail - Setting variety data:', {
          name: variety.name,
          yield_potential: variety.yield_potential,
          yield_potential_type: typeof variety.yield_potential,
          expected_yield_per_hectare: variety.expected_yield_per_hectare,
          disease_resistance: variety.disease_resistance,
          disease_resistance_type: typeof variety.disease_resistance,
          fullVariety: variety
        })
        
        // Parse stringified objects if they exist (fix for serialization issue)
        const varietyCopy = { ...variety }
        
        // If yield_potential is an empty object or a string, try to parse it
        if (varietyCopy.yield_potential) {
          if (typeof varietyCopy.yield_potential === 'string') {
            try {
              varietyCopy.yield_potential = JSON.parse(varietyCopy.yield_potential)
            } catch (e) {
              console.warn('Failed to parse yield_potential string:', e)
            }
          } else if (typeof varietyCopy.yield_potential === 'object' && Object.keys(varietyCopy.yield_potential).length === 0) {
            // Try to find a stringified version in the original variety
            const stringified = JSON.stringify(variety)
            const match = stringified.match(/"yield_potential":"({[^}]+})"/)
            if (match) {
              try {
                varietyCopy.yield_potential = JSON.parse(match[1])
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
          } else if (typeof varietyCopy.disease_resistance === 'object' && Object.keys(varietyCopy.disease_resistance).length === 0) {
            const stringified = JSON.stringify(variety)
            const match = stringified.match(/"disease_resistance":"({[^}]+})"/)
            if (match) {
              try {
                varietyCopy.disease_resistance = JSON.parse(match[1])
              } catch (e) {
                // Ignore
              }
            }
          }
        }
        
        const finalVariety = JSON.parse(JSON.stringify(varietyCopy))
        setVarietyData(finalVariety)
        
        // Store crop production info if available
        if (response.data.crop_production_info) {
          setCropProductionInfo(response.data.crop_production_info)
        }
      } catch (err) {
        console.error('🔍 VarietyDetail - Error:', err)
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
      return JSON.stringify(value)
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
                  {(() => {
                    console.log('🔍 VarietyDetail - Rendering yield:', {
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
                      // Check if it's an object with text property - extract directly
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
                    
                    console.log('🔍 VarietyDetail - Final yield display:', yieldDisplay);
                    return yieldDisplay;
                  })()}
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
                  {varietyData.min_rainfall_mm && varietyData.max_rainfall_mm
                    ? `${formatValue(varietyData.min_rainfall_mm)}-${formatValue(varietyData.max_rainfall_mm)} mm`
                    : formatValue(varietyData.drought_tolerance, 'Moderate')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rainfall Requirements
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.50', borderRadius: 2 }}>
                <BugIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Box sx={{ minHeight: '32px' }}>
                  <PestDiseaseManagement 
                    pestManagement={varietyData.pest_management}
                    diseaseManagement={varietyData.disease_management}
                    compact={true}
                  />
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Things to Take Note in Production */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
            <Typography variant="h6">Things to Take Note in Production</Typography>
          </Box>
          
          <Box sx={{ mb: 2 }}>
            {(() => {
              const notes = []
              if (varietyData.disease_management && formatValue(varietyData.disease_management) !== 'Not specified') {
                notes.push(`Disease Management: ${formatValue(varietyData.disease_management)}`)
              }
              if (varietyData.pest_management && formatValue(varietyData.pest_management) !== 'Not specified') {
                notes.push(`Pest Management: ${formatValue(varietyData.pest_management)}`)
              }
              if (varietyData.drought_tolerance && formatValue(varietyData.drought_tolerance) !== 'Not specified') {
                notes.push(`Drought Tolerance: ${formatValue(varietyData.drought_tolerance)}`)
              }
              if (varietyData.description && formatValue(varietyData.description) !== 'Not specified') {
                notes.push(`General Notes: ${formatValue(varietyData.description)}`)
              }
              
              // Use variety-specific if available, otherwise use crop production info
              if (notes.length > 0) {
                return (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {notes.join('\n\n')}
                  </Typography>
                )
              }
              
              // Fallback to crop production info
              const productionNotes = cropProductionInfo?.production_notes
              if (productionNotes) {
                const keyPoints = extractKeyPoints(productionNotes, 5)
                if (keyPoints.length > 0) {
                  return (
                    <List dense>
                      {keyPoints.map((point, index) => (
                        <ListItem key={index} sx={{ pl: 0 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <CheckCircleIcon color="primary" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={point} />
                        </ListItem>
                      ))}
                    </List>
                  )
                }
              }
              
              return (
                <Typography variant="body2" color="text.secondary" paragraph>
                  General production guidelines for {cropName?.replace('-', ' ')}. Monitor growth regularly, ensure adequate water supply, and follow recommended spacing and planting practices.
                </Typography>
              )
            })()}
          </Box>
        </CardContent>
      </Card>

      {/* Land Preparation */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TractorIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Land Preparation</Typography>
          </Box>
          
          {(() => {
            // Try to extract land preparation info from soil_requirements
            const soilInfo = formatValue(varietyData.soil_requirements, '')
            if (soilInfo && soilInfo !== 'Not specified' && soilInfo.toLowerCase().includes('prepar')) {
              return (
                <Typography variant="body2" color="text.secondary" paragraph>
                  {soilInfo}
                </Typography>
              )
            }
            
            // Fallback to crop production info
            const landPrep = cropProductionInfo?.land_preparation
            if (landPrep) {
              // Extract more points for land preparation to show detailed information
              const keyPoints = extractKeyPoints(landPrep, 8)
              if (keyPoints.length > 0) {
                return (
                  <List dense>
                    {keyPoints.map((point, index) => (
                      <ListItem key={index} sx={{ pl: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={point} 
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                )
              }
            }
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {soilInfo && soilInfo !== 'Not specified'
                  ? `Prepare land by plowing and harrowing to achieve fine tilth. Ensure ${soilInfo.toLowerCase()}. Remove weeds and incorporate organic matter if available.`
                  : `Prepare land by plowing and harrowing to achieve fine tilth. Ensure well-drained soil. Remove weeds and incorporate organic matter if available. Level the field for uniform water distribution if irrigation is needed.`}
              </Typography>
            )
          })()}
        </CardContent>
      </Card>

      {/* Manure Application */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <ManureIcon sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="h6">Manure Application</Typography>
          </Box>
          
          {(() => {
            // Check if fertilizer_requirements mentions manure
            const fertInfo = formatValue(varietyData.fertilizer_requirements, '')
            if (fertInfo && fertInfo !== 'Not specified' && fertInfo.toLowerCase().includes('manure')) {
              return (
                <Typography variant="body2" color="text.secondary" paragraph>
                  {fertInfo}
                </Typography>
              )
            }
            
            // Fallback to crop production info
            const manureInfo = cropProductionInfo?.manure_application
            if (manureInfo) {
              const keyPoints = extractKeyPoints(manureInfo, 4)
              if (keyPoints.length > 0) {
                return (
                  <List dense>
                    {keyPoints.map((point, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                )
              }
            }
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fertInfo && fertInfo !== 'Not specified'
                  ? `Apply well-decomposed farmyard manure or compost at 5-10 tons per hectare before planting. ${fertInfo}`
                  : `Apply well-decomposed farmyard manure or compost at 5-10 tons per hectare before planting. Incorporate manure into the soil during land preparation to improve soil structure and fertility.`}
              </Typography>
            )
          })()}
        </CardContent>
      </Card>

      {/* Planting Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PlantingIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Planting Information</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Planting Time"
                    secondary={formatValue(varietyData.planting_time || varietyData.planting_months, 'Seasonal planting recommended')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <LocationIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Spacing Requirements"
                    secondary={formatValue(varietyData.spacing_requirements, 'Follow recommended spacing for optimal growth and yield')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SproutIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Seed Rate"
                    secondary={varietyData.seed_rate_per_hectare 
                      ? `${formatValue(varietyData.seed_rate_per_hectare)} per hectare`
                      : 'Standard seed rate per hectare recommended'}
                  />
                </ListItem>
              </List>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Planting Guidelines
              </Typography>
              {(() => {
                const guidelines = []
                if (varietyData.spacing_requirements && formatValue(varietyData.spacing_requirements) !== 'Not specified') {
                  guidelines.push(`Maintain spacing: ${formatValue(varietyData.spacing_requirements)}`)
                }
                if (varietyData.planting_time && formatValue(varietyData.planting_time) !== 'Not specified') {
                  guidelines.push(`Plant during: ${formatValue(varietyData.planting_time)}`)
                }
                
                // Use variety-specific if available
                if (guidelines.length > 0) {
                  return (
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {guidelines.join('. ') + '. Ensure proper depth and soil contact for optimal germination.'}
                    </Typography>
                  )
                }
                
                // Fallback to crop production info
                const plantingInfo = cropProductionInfo?.planting_info
                if (plantingInfo) {
                  const keyPoints = extractKeyPoints(plantingInfo, 4)
                  if (keyPoints.length > 0) {
                    return (
                      <List dense>
                        {keyPoints.map((point, index) => (
                          <ListItem key={index} sx={{ pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              <CheckCircleIcon color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary={point} />
                          </ListItem>
                        ))}
                      </List>
                    )
                  }
                }
                
                return (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Plant seeds at recommended depth with proper spacing. Ensure good soil contact and adequate moisture for optimal germination and establishment.
                  </Typography>
                )
              })()}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Fertilizer Application */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <FertilizerIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Fertilizer Application</Typography>
          </Box>
          
          {(() => {
            const fertInfo = formatValue(varietyData.fertilizer_requirements, '')
            if (fertInfo && fertInfo !== 'Not specified') {
              return (
                <Typography variant="body2" color="text.secondary" paragraph>
                  {fertInfo}
                </Typography>
              )
            }
            
            // Fallback to crop production info
            const fertilizerInfo = cropProductionInfo?.fertilizer_application
            if (fertilizerInfo) {
              const keyPoints = extractKeyPoints(fertilizerInfo, 4)
              if (keyPoints.length > 0) {
                return (
                  <List dense>
                    {keyPoints.map((point, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                )
              }
            }
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                Apply balanced NPK fertilizer according to soil test results. Generally, apply 100-150 kg/ha of compound fertilizer (e.g., 23:21:0+4S or 10:20:20) at planting. Top-dress with nitrogen fertilizer 4-6 weeks after planting if needed.
              </Typography>
            )
          })()}
        </CardContent>
      </Card>

      {/* Weeding */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CropIcon sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="h6">Weeding</Typography>
          </Box>
          
          {(() => {
            // Check if pest_management mentions weeding
            const pestInfo = formatValue(varietyData.pest_management, '')
            if (pestInfo && pestInfo !== 'Not specified' && pestInfo.toLowerCase().includes('weed')) {
              return (
                <Typography variant="body2" color="text.secondary" paragraph>
                  {pestInfo}
                </Typography>
              )
            }
            
            // Fallback to crop production info
            const weedingInfo = cropProductionInfo?.weeding
            if (weedingInfo) {
              const keyPoints = extractKeyPoints(weedingInfo, 4)
              if (keyPoints.length > 0) {
                return (
                  <List dense>
                    {keyPoints.map((point, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                )
              }
            }
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {pestInfo && pestInfo !== 'Not specified'
                  ? `Weed the crop 2-3 weeks after planting and as needed throughout the growing season. Use hand weeding, hoeing, or appropriate herbicides. Keep the field weed-free especially during the first 6-8 weeks when the crop is establishing. Additional pest management: ${pestInfo}`
                  : 'Weed the crop 2-3 weeks after planting and as needed throughout the growing season. Use hand weeding, hoeing, or appropriate herbicides. Keep the field weed-free especially during the first 6-8 weeks when the crop is establishing.'}
              </Typography>
            )
          })()}
        </CardContent>
      </Card>

      {/* Storing */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Storing</Typography>
          </Box>
          
          {(() => {
            const storageInfo = formatValue(varietyData.storage_requirements, '')
            const harvestInfo = formatValue(varietyData.harvesting_guidelines, '')
            
            // Use variety-specific if available
            if ((storageInfo && storageInfo !== 'Not specified') || (harvestInfo && harvestInfo !== 'Not specified')) {
              return (
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Storage Requirements
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {storageInfo && storageInfo !== 'Not specified'
                        ? storageInfo
                        : 'Store harvested produce in a cool, dry, and well-ventilated place. Ensure proper drying before storage to prevent mold and spoilage. Use clean, dry containers and protect from pests and moisture.'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Harvesting Guidelines
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {harvestInfo && harvestInfo !== 'Not specified'
                        ? harvestInfo
                        : 'Harvest at the appropriate maturity stage. For grains, harvest when pods are dry and seeds are mature. Handle produce carefully to avoid damage and store only fully dried produce.'}
                    </Typography>
                  </Grid>
                </Grid>
              )
            }
            
            // Fallback to crop production info
            const storingInfo = cropProductionInfo?.storing
            if (storingInfo) {
              const keyPoints = extractKeyPoints(storingInfo, 5)
              if (keyPoints.length > 0) {
                return (
                  <List dense>
                    {keyPoints.map((point, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                )
              }
            }
            
            return (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Storage Requirements
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Store harvested produce in a cool, dry, and well-ventilated place. Ensure proper drying before storage to prevent mold and spoilage. Use clean, dry containers and protect from pests and moisture.
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Harvesting Guidelines
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Harvest at the appropriate maturity stage. For grains, harvest when pods are dry and seeds are mature. Handle produce carefully to avoid damage and store only fully dried produce.
                  </Typography>
                </Grid>
              </Grid>
            )
          })()}
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

      {/* Pest and Disease Management */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <PestDiseaseManagement 
            pestManagement={varietyData.pest_management}
            diseaseManagement={varietyData.disease_management}
            compact={false}
          />
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
