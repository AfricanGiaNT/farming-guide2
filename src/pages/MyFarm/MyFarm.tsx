import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material'
import { 
  Agriculture, 
  LocationOn, 
  CalendarToday, 
  TrendingUp,
  Add,
  Edit,
  Delete
} from '@mui/icons-material'
import { cropAPI } from '../../services/api'

interface FarmField {
  id: string
  name: string
  crop: string
  area: number
  plantingDate: string
  expectedHarvest: string
  status: 'planted' | 'growing' | 'harvesting' | 'harvested'
  location: {
    lat: number
    lon: number
  }
}

interface CropRecommendation {
  crop_name: string
  suitability_score: number
  suitability_level: string
  planting_time: string
  yield_potential: string
  description: string
}

const MyFarm: React.FC = () => {
  const [fields, setFields] = useState<FarmField[]>([])
  const [newField, setNewField] = useState({
    name: '',
    crop: '',
    area: '',
    plantingDate: '',
    location: { lat: -13.9833, lon: 33.7833 }
  })
  const [showAddForm, setShowAddForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recommendations, setRecommendations] = useState<CropRecommendation[]>([])

  // Load initial data
  useEffect(() => {
    loadFarmData()
    loadRecommendations()
  }, [])

  const loadFarmData = () => {
    // Mock data for demonstration
    setFields([
      {
        id: '1',
        name: 'North Field',
        crop: 'Maize',
        area: 2.5,
        plantingDate: '2024-11-15',
        expectedHarvest: '2025-03-15',
        status: 'planted',
        location: { lat: -13.9833, lon: 33.7833 }
      },
      {
        id: '2',
        name: 'South Field',
        crop: 'Groundnuts',
        area: 1.8,
        plantingDate: '2024-12-01',
        expectedHarvest: '2025-04-01',
        status: 'growing',
        location: { lat: -13.9833, lon: 33.7833 }
      }
    ])
  }

  const loadRecommendations = async () => {
    try {
      const data = await cropAPI.getCropRecommendations(-13.9833, 33.7833, 'current')
      setRecommendations(data.recommendations?.slice(0, 3) || [])
    } catch (err) {
      console.error('Failed to load recommendations:', err)
    }
  }

  const handleAddField = () => {
    if (!newField.name || !newField.crop || !newField.area) {
      setError('Please fill in all required fields')
      return
    }

    const field: FarmField = {
      id: Date.now().toString(),
      name: newField.name,
      crop: newField.crop,
      area: parseFloat(newField.area),
      plantingDate: newField.plantingDate,
      expectedHarvest: calculateHarvestDate(newField.crop, newField.plantingDate),
      status: 'planted',
      location: newField.location
    }

    setFields([...fields, field])
    setNewField({
      name: '',
      crop: '',
      area: '',
      plantingDate: '',
      location: { lat: -13.9833, lon: 33.7833 }
    })
    setShowAddForm(false)
    setError(null)
  }

  const calculateHarvestDate = (crop: string, plantingDate: string): string => {
    const planting = new Date(plantingDate)
    const daysToHarvest = crop === 'Maize' ? 120 : crop === 'Groundnuts' ? 105 : 90
    const harvest = new Date(planting.getTime() + daysToHarvest * 24 * 60 * 60 * 1000)
    return harvest.toISOString().split('T')[0]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planted': return 'info'
      case 'growing': return 'success'
      case 'harvesting': return 'warning'
      case 'harvested': return 'default'
      default: return 'default'
    }
  }

  const getTotalArea = () => {
    return fields.reduce((total, field) => total + field.area, 0)
  }

  const getActiveFields = () => {
    return fields.filter(field => field.status !== 'harvested').length
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
        My Farm
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage your farm fields, track crop progress, and plan your agricultural activities.
      </Typography>

      {/* Farm Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Agriculture sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6">{fields.length}</Typography>
              <Typography variant="body2" color="text.secondary">Total Fields</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h6">{getActiveFields()}</Typography>
              <Typography variant="body2" color="text.secondary">Active Fields</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <LocationOn sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h6">{getTotalArea().toFixed(1)}</Typography>
              <Typography variant="body2" color="text.secondary">Total Area (ha)</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CalendarToday sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h6">{new Date().getFullYear()}</Typography>
              <Typography variant="body2" color="text.secondary">Season</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Field Button */}
      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowAddForm(true)}
          sx={{ mb: 2 }}
        >
          Add New Field
        </Button>
      </Box>

      {/* Add Field Form */}
      {showAddForm && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Add New Field</Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Field Name"
                  value={newField.name}
                  onChange={(e) => setNewField({...newField, name: e.target.value})}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Crop</InputLabel>
                  <Select
                    value={newField.crop}
                    onChange={(e) => setNewField({...newField, crop: e.target.value})}
                  >
                    <MenuItem value="Maize">Maize</MenuItem>
                    <MenuItem value="Groundnuts">Groundnuts</MenuItem>
                    <MenuItem value="Beans">Beans</MenuItem>
                    <MenuItem value="Soybeans">Soybeans</MenuItem>
                    <MenuItem value="Rice">Rice</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Area (hectares)"
                  type="number"
                  value={newField.area}
                  onChange={(e) => setNewField({...newField, area: e.target.value})}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Planting Date"
                  type="date"
                  value={newField.plantingDate}
                  onChange={(e) => setNewField({...newField, plantingDate: e.target.value})}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button variant="contained" onClick={handleAddField}>
                Add Field
              </Button>
              <Button variant="outlined" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Crop Recommendations */}
      {recommendations.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recommended Crops for Your Location</Typography>
            <Grid container spacing={2}>
              {recommendations.map((rec, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        {rec.crop_name}
                      </Typography>
                      <Chip 
                        label={rec.suitability_level} 
                        color="success" 
                        size="small" 
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {rec.description}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Yield: {rec.yield_potential}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Fields List */}
      <Typography variant="h6" gutterBottom>Your Fields</Typography>
      <Grid container spacing={2}>
        {fields.map((field) => (
          <Grid item xs={12} md={6} key={field.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Typography variant="h6">{field.name}</Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<Edit />}>Edit</Button>
                    <Button size="small" color="error" startIcon={<Delete />}>Delete</Button>
                  </Box>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Crop</Typography>
                    <Typography variant="body1">{field.crop}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Area</Typography>
                    <Typography variant="body1">{field.area} ha</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip 
                      label={field.status} 
                      color={getStatusColor(field.status) as any}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Planting Date</Typography>
                    <Typography variant="body1">
                      {new Date(field.plantingDate).toLocaleDateString()}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {fields.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Agriculture sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No fields added yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Start by adding your first field to track your farming activities
            </Typography>
            <Button variant="contained" startIcon={<Add />} onClick={() => setShowAddForm(true)}>
              Add Your First Field
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default MyFarm
