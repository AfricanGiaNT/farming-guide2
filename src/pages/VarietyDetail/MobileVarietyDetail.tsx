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
  DriveEta as TractorIcon,
  LocalFlorist as ManureIcon,
  Agriculture as SproutIcon,
  Warning as WarningIcon,
  Grass as CropIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { displayToDatabaseName } from '../../utils/cropNameMapping'
import { createSlug } from '../../utils/slugUtils'
import { extractKeyPoints } from '../../utils/extractKeyPoints'

interface MobileVarietyDetailProps {}

const MobileVarietyDetail: React.FC<MobileVarietyDetailProps> = () => {
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
        // Normalize the target variety name (handle both space and hyphen variations)
        const targetSlug = varietyName?.toLowerCase().trim().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
        let variety = null
        
        console.log('🔍 Matching strategies - Target slug:', targetSlug, 'Looking for variety:', varietyName)
        
        // Strategy 1: Exact slug match (normalize both sides)
        variety = varieties.find((v: any) => {
          const varietyNameField = v.name || v.variety_name || v.varietyName
          if (!varietyNameField) return false
          const varietySlug = createSlug(varietyNameField)
          const matches = varietySlug === targetSlug
          if (matches) console.log(`✅ Exact slug match: "${varietyNameField}" (slug: ${varietySlug}) === "${targetSlug}"`)
          return matches
        })
        
        // Strategy 2: Case-insensitive name match (normalize spaces and hyphens)
        if (!variety) {
          variety = varieties.find((v: any) => {
            const varietyNameField = v.name || v.variety_name || v.varietyName
            if (!varietyNameField) return false
            // Normalize both: replace spaces/hyphens with single space, then compare
            const vNormalized = varietyNameField.toLowerCase().trim().replace(/[\s-]+/g, ' ')
            const targetNormalized = varietyName.toLowerCase().trim().replace(/[\s-]+/g, ' ')
            const matches = vNormalized === targetNormalized
            if (matches) console.log(`✅ Case-insensitive normalized match: "${varietyNameField}" (normalized: ${vNormalized}) === "${varietyName}" (normalized: ${targetNormalized})`)
            return matches
          })
        }
        
        // Strategy 3: Try matching by removing all non-alphanumeric from both sides
        if (!variety) {
          variety = varieties.find((v: any) => {
            const varietyNameField = v.name || v.variety_name || v.varietyName
            if (!varietyNameField) return false
            const vClean = varietyNameField.toLowerCase().replace(/[^a-z0-9]/g, '')
            const targetClean = varietyName.toLowerCase().replace(/[^a-z0-9]/g, '')
            const matches = vClean === targetClean
            if (matches) console.log(`✅ Clean match: "${varietyNameField}" (clean: ${vClean}) === "${varietyName}" (clean: ${targetClean})`)
            return matches
          })
        }
        
        // Strategy 4: Partial match (check if slug contains the target or vice versa)
        if (!variety) {
          variety = varieties.find((v: any) => {
            const varietyNameField = v.name || v.variety_name || v.varietyName
            if (!varietyNameField) return false
            const varietySlug = createSlug(varietyNameField)
            const normalizedVarietyName = varietyName.toLowerCase().trim().replace(/[^a-z0-9-]/g, '-')
            const matches = varietySlug.includes(normalizedVarietyName) || normalizedVarietyName.includes(varietySlug)
            if (matches) console.log(`✅ Partial match: "${varietyNameField}" (slug: ${varietySlug}) contains "${normalizedVarietyName}" or vice versa`)
            return matches
          })
        }
        
        if (!variety) {
          // Try to get variety names from different possible field names
          const availableNames = varieties.map((v: any) => v.name || v.variety_name || v.varietyName || 'Unknown').join(', ')
          const availableSlugs = varieties.map((v: any) => {
            const vName = v.name || v.variety_name || v.varietyName || 'Unknown'
            return `${vName} (slug: ${createSlug(vName)})`
          }).join(', ')
          
          console.error('🔍 MobileVarietyDetail - Variety not found.', {
            lookingFor: varietyName,
            targetSlug,
            availableNames,
            availableSlugs
          })
          
          // Show a more helpful error message
          setError(`Variety "${varietyName}" not found. Available varieties: ${availableNames || 'none'}. Please go back and select a different variety.`)
          setIsLoading(false)
          return
        }
        
        // Get variety name from any possible field
        const varietyNameField = variety.name || variety.variety_name || variety.varietyName || 'Unknown'
        
        console.log('🔍 MobileVarietyDetail - Setting variety data:', {
          name: varietyNameField,
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
        // Ensure name field is set
        if (!varietyCopy.name) {
          varietyCopy.name = varietyNameField
        }
        
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
        
        // Store crop production info if available
        if (response.data.crop_production_info) {
          console.log('🌱 API returned crop_production_info:', response.data.crop_production_info)
          setCropProductionInfo(response.data.crop_production_info)
        } else {
          console.log('⚠️ No crop_production_info in API response')
        }
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

      {/* Things to Take Note in Production - UPDATED */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>⚠️ Things to Take Note in Production</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            // PRIORITY: Use crop production info from Supabase FIRST (this is the main source)
            const productionNotes = cropProductionInfo?.production_notes
            if (productionNotes) {
              const keyPoints = extractKeyPoints(productionNotes, 6)
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
            
            // Fallback: Collect variety-specific notes if crop_production_info is not available
            const notesText = []
            if (varietyData.disease_management && formatValue(varietyData.disease_management) !== 'Not specified') {
              notesText.push(`Disease Management: ${formatValue(varietyData.disease_management)}`)
            }
            if (varietyData.pest_management && formatValue(varietyData.pest_management) !== 'Not specified') {
              notesText.push(`Pest Management: ${formatValue(varietyData.pest_management)}`)
            }
            if (varietyData.drought_tolerance && formatValue(varietyData.drought_tolerance) !== 'Not specified') {
              notesText.push(`Drought Tolerance: ${formatValue(varietyData.drought_tolerance)}`)
            }
            if (varietyData.description && formatValue(varietyData.description) !== 'Not specified') {
              notesText.push(`General Notes: ${formatValue(varietyData.description)}`)
            }
            
            // Extract key points from variety-specific data if available
            if (notesText.length > 0) {
              // Join with newlines to preserve structure, then extract
              const combinedText = notesText.join('\n\n')
              const keyPoints = extractKeyPoints(combinedText, 6)
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
            
            // Final fallback - extract key points from generic text
            const fallbackText = `General production guidelines for ${cropName?.replace('-', ' ')}. Monitor growth regularly, ensure adequate water supply, and follow recommended spacing and planting practices.`
            const fallbackPoints = extractKeyPoints(fallbackText, 3)
            if (fallbackPoints.length > 0) {
              return (
                <List dense>
                  {fallbackPoints.map((point, index) => (
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
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fallbackText}
              </Typography>
            )
          })()}
        </AccordionDetails>
      </Accordion>

      {/* Land Preparation */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TractorIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Land Preparation</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            // PRIORITY: Use crop production info from Supabase FIRST
            const landPrep = cropProductionInfo?.land_preparation
            console.log('🔍 Land Prep Debug:', {
              hasCropProductionInfo: !!cropProductionInfo,
              hasLandPrep: !!landPrep,
              landPrepLength: landPrep?.length || 0,
              landPrepPreview: landPrep?.substring(0, 200) || 'N/A'
            })
            
            if (landPrep && landPrep.trim().length > 0) {
              // Extract more points for land preparation to show detailed information
              console.log('🌱 Processing land_preparation:', {
                originalLength: landPrep.length,
                first500Chars: landPrep.substring(0, 500),
                hasNewlines: landPrep.includes('\n'),
                paragraphCount: landPrep.split('\n\n').length
              })
              
              const keyPoints = extractKeyPoints(landPrep, 10)
              console.log('🌱 Extracted key points count:', keyPoints.length)
              console.log('🌱 Key points:', keyPoints)
              
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
              } else {
                console.error('⚠️ extractKeyPoints returned empty array for land_preparation')
                // Fallback: Show raw text if extraction fails (truncated)
                const truncatedText = landPrep.length > 500 ? landPrep.substring(0, 500) + '...' : landPrep
                return (
                  <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line' }}>
                    {truncatedText}
                  </Typography>
                )
              }
            } else {
              console.log('⚠️ No land_preparation in crop_production_info or it is empty')
            }
            
            // Fallback: Try to extract land preparation info from soil_requirements
            const soilInfo = formatValue(varietyData.soil_requirements, '')
            if (soilInfo && soilInfo !== 'Not specified' && soilInfo.toLowerCase().includes('prepar')) {
              const keyPoints = extractKeyPoints(soilInfo, 4)
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
            
            // Final fallback - use generic text with key points extraction
            const fallbackText = soilInfo && soilInfo !== 'Not specified'
              ? `Prepare land by plowing and harrowing to achieve fine tilth. Ensure ${soilInfo.toLowerCase()}. Remove weeds and incorporate organic matter if available.`
              : `Prepare land by plowing and harrowing to achieve fine tilth. Ensure well-drained soil. Remove weeds and incorporate organic matter if available. Level the field for uniform water distribution if irrigation is needed.`
            
            const fallbackPoints = extractKeyPoints(fallbackText, 3)
            if (fallbackPoints.length > 0) {
              return (
                <List dense>
                  {fallbackPoints.map((point, index) => (
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
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fallbackText}
              </Typography>
            )
          })()}
        </AccordionDetails>
      </Accordion>

      {/* Manure Application */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ManureIcon sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="subtitle1">Manure Application</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            // PRIORITY: Use crop production info from Supabase FIRST
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
            
            // Fallback: Check if fertilizer_requirements mentions manure
            const fertInfo = formatValue(varietyData.fertilizer_requirements, '')
            if (fertInfo && fertInfo !== 'Not specified' && fertInfo.toLowerCase().includes('manure')) {
              const keyPoints = extractKeyPoints(fertInfo, 4)
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
            
            // Final fallback - extract key points from generic text
            const fallbackText = fertInfo && fertInfo !== 'Not specified'
              ? `Apply well-decomposed farmyard manure or compost at 5-10 tons per hectare before planting. ${fertInfo}`
              : `Apply well-decomposed farmyard manure or compost at 5-10 tons per hectare before planting. Incorporate manure into the soil during land preparation to improve soil structure and fertility.`
            
            const fallbackPoints = extractKeyPoints(fallbackText, 3)
            if (fallbackPoints.length > 0) {
              return (
                <List dense>
                  {fallbackPoints.map((point, index) => (
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
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fallbackText}
              </Typography>
            )
          })()}
        </AccordionDetails>
      </Accordion>

      {/* Planting Information */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <LocationIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Planting Information</Typography>
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
                secondary={formatValue(varietyData.planting_time || varietyData.planting_months, 'Seasonal planting recommended')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LocationIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Spacing Requirements"
                secondary={formatValue(varietyData.spacing_requirements, 'Follow recommended spacing for optimal growth and yield')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <SproutIcon color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Seed Rate"
                secondary={varietyData.seed_rate_per_hectare 
                  ? `${formatValue(varietyData.seed_rate_per_hectare)} per hectare`
                  : 'Standard seed rate per hectare recommended'}
              />
            </ListItem>
          </List>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
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
            
            // PRIORITY: Use crop production info from Supabase FIRST
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
        </AccordionDetails>
      </Accordion>

      {/* Fertilizer Application */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FertilizerIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Fertilizer Application</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            const fertInfo = formatValue(varietyData.fertilizer_requirements, '')
            
            // Always extract key points if we have variety-specific data
            if (fertInfo && fertInfo !== 'Not specified') {
              const keyPoints = extractKeyPoints(fertInfo, 4)
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
            
            // PRIORITY: Use crop production info from Supabase FIRST
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
            
            // Final fallback - extract key points from generic text
            const fallbackText = 'Apply balanced NPK fertilizer according to soil test results. Generally, apply 100-150 kg/ha of compound fertilizer (e.g., 23:21:0+4S or 10:20:20) at planting. Top-dress with nitrogen fertilizer 4-6 weeks after planting if needed.'
            const fallbackPoints = extractKeyPoints(fallbackText, 3)
            if (fallbackPoints.length > 0) {
              return (
                <List dense>
                  {fallbackPoints.map((point, index) => (
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
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fallbackText}
              </Typography>
            )
          })()}
        </AccordionDetails>
      </Accordion>

      {/* Weeding */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CropIcon sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="subtitle1">Weeding</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            // Check if pest_management mentions weeding
            const pestInfo = formatValue(varietyData.pest_management, '')
            
            // Always extract key points if we have variety-specific data
            if (pestInfo && pestInfo !== 'Not specified' && pestInfo.toLowerCase().includes('weed')) {
              const keyPoints = extractKeyPoints(pestInfo, 4)
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
            
            // PRIORITY: Use crop production info from Supabase FIRST
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
            
            // Final fallback - extract key points from generic text
            const fallbackText = pestInfo && pestInfo !== 'Not specified'
              ? `Weed the crop 2-3 weeks after planting and as needed throughout the growing season. Use hand weeding, hoeing, or appropriate herbicides. Keep the field weed-free especially during the first 6-8 weeks when the crop is establishing. Additional pest management: ${pestInfo}`
              : 'Weed the crop 2-3 weeks after planting and as needed throughout the growing season. Use hand weeding, hoeing, or appropriate herbicides. Keep the field weed-free especially during the first 6-8 weeks when the crop is establishing.'
            
            const fallbackPoints = extractKeyPoints(fallbackText, 3)
            if (fallbackPoints.length > 0) {
              return (
                <List dense>
                  {fallbackPoints.map((point, index) => (
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
            
            return (
              <Typography variant="body2" color="text.secondary" paragraph>
                {fallbackText}
              </Typography>
            )
          })()}
        </AccordionDetails>
      </Accordion>

      {/* Storing */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="subtitle1">Storing</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {(() => {
            const storageInfo = formatValue(varietyData.storage_requirements, '')
            const harvestInfo = formatValue(varietyData.harvesting_guidelines, '')
            
            // Use variety-specific if available
            if ((storageInfo && storageInfo !== 'Not specified') || (harvestInfo && harvestInfo !== 'Not specified')) {
              return (
                <>
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Storage Requirements
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {storageInfo && storageInfo !== 'Not specified'
                      ? storageInfo
                      : 'Store harvested produce in a cool, dry, and well-ventilated place. Ensure proper drying before storage to prevent mold and spoilage. Use clean, dry containers and protect from pests and moisture.'}
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Harvesting Guidelines
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {harvestInfo && harvestInfo !== 'Not specified'
                      ? harvestInfo
                      : 'Harvest at the appropriate maturity stage. For grains, harvest when pods are dry and seeds are mature. Handle produce carefully to avoid damage and store only fully dried produce.'}
                  </Typography>
                </>
              )
            }
            
            // PRIORITY: Use crop production info from Supabase FIRST
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
              <>
                <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                  Storage Requirements
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Store harvested produce in a cool, dry, and well-ventilated place. Ensure proper drying before storage to prevent mold and spoilage. Use clean, dry containers and protect from pests and moisture.
                </Typography>
                
                <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                  Harvesting Guidelines
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Harvest at the appropriate maturity stage. For grains, harvest when pods are dry and seeds are mature. Handle produce carefully to avoid damage and store only fully dried produce.
                </Typography>
              </>
            )
          })()}
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
