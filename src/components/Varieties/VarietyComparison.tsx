import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Divider,
} from '@mui/material'
import {
  Close as CloseIcon,
  Schedule as ScheduleIcon,
  TrendingUp as YieldIcon,
  WaterDrop as WaterIcon,
  BugReport as BugIcon,
} from '@mui/icons-material'

interface Variety {
  name: string
  maturity_days: number
  yield_potential: string
  drought_tolerance: string
  disease_resistance: string
  planting_time: string
  description: string
  weather_requirements?: string
  soil_requirements?: string
  growing_areas?: string
}

interface VarietyComparisonProps {
  varieties: Variety[]
  onClose: () => void
}

const VarietyComparison: React.FC<VarietyComparisonProps> = ({
  varieties,
  onClose,
}) => {
  if (varieties.length === 0) return null

  const comparisonFields = [
    { key: 'maturity_days', label: 'Maturity Period', icon: <ScheduleIcon fontSize="small" />, suffix: ' days' },
    { key: 'yield_potential', label: 'Yield Potential', icon: <YieldIcon fontSize="small" /> },
    { key: 'drought_tolerance', label: 'Drought Tolerance', icon: <WaterIcon fontSize="small" /> },
    { key: 'disease_resistance', label: 'Disease Resistance', icon: <BugIcon fontSize="small" /> },
    { key: 'planting_time', label: 'Planting Time', icon: <ScheduleIcon fontSize="small" /> },
    { key: 'weather_requirements', label: 'Weather Requirements' },
    { key: 'soil_requirements', label: 'Soil Requirements' },
    { key: 'growing_areas', label: 'Best Growing Areas' },
  ]

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            🔍 Variety Comparison ({varieties.length} varieties)
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Comparison Table */}
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 'bold', minWidth: 180 }}>
                  Characteristic
                </TableCell>
                {varieties.map((variety, index) => (
                  <TableCell key={index} sx={{ fontWeight: 'bold', minWidth: 200 }}>
                    🌱 {variety.name}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {comparisonFields.map((field) => {
                // Skip fields where all varieties have "Not specified" values
                const hasSpecifiedValues = varieties.some(variety => {
                  const value = variety[field.key as keyof Variety]
                  return value && value !== 'Not specified' && value !== ''
                })

                if (!hasSpecifiedValues && field.key !== 'maturity_days' && field.key !== 'planting_time') {
                  return null
                }

                return (
                  <TableRow key={field.key}>
                    <TableCell sx={{ fontWeight: 'medium', bgcolor: 'grey.25' }}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {field.icon}
                        {field.label}
                      </Box>
                    </TableCell>
                    {varieties.map((variety, index) => {
                      let value = variety[field.key as keyof Variety]
                      
                      if (field.key === 'maturity_days') {
                        value = `${value}${field.suffix || ''}`
                      } else if (!value || value === 'Not specified') {
                        value = '—'
                      }

                      return (
                        <TableCell key={index}>
                          <Typography variant="body2">
                            {value}
                          </Typography>
                        </TableCell>
                      )
                    })}
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Variety Descriptions */}
        <Box mt={3}>
          <Typography variant="subtitle1" gutterBottom>
            📝 Variety Descriptions
          </Typography>
          <Grid container spacing={2}>
            {varieties.map((variety, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Box p={2} bgcolor="grey.50" borderRadius={1}>
                  <Typography variant="subtitle2" gutterBottom>
                    🌱 {variety.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {variety.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Comparison Tips */}
        <Box mt={3} p={2} bgcolor="info.light" borderRadius={1}>
          <Typography variant="subtitle2" gutterBottom>
            💡 Comparison Tips
          </Typography>
          <Typography variant="body2">
            • Consider your local climate when comparing drought tolerance
            • Match maturity periods with your planting calendar
            • Choose varieties with disease resistance for your area
            • Higher yield potential may require better soil and management
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default VarietyComparison
