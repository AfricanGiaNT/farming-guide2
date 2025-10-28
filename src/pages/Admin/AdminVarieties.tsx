import React, { useMemo, useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
} from '@mui/material'
import {
  Agriculture as AgricultureIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { adminAPI, ExtractedVariety, VarietyExtractionParams, VarietyExtractionResult, VarietyValidationResult } from '../../services/api'
import VarietyValidationModal from '../../components/Admin/VarietyValidationModal'

const cropOptions = [
  'Maize',
  'Groundnut',
  'Soybean',
  'Bean',
  'Rice',
  'Cassava',
  'Sorghum',
  'Tomato',
  'Sweet Potato',
  'Cowpea',
]

interface ExtractionSummary extends VarietyExtractionResult {}

const AdminVarieties: React.FC = () => {
  const [selectedCrops, setSelectedCrops] = useState<string[]>([])
  const [isExtracting, setIsExtracting] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [extractionResult, setExtractionResult] = useState<ExtractionSummary | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const totalVarietiesExtracted = extractionResult?.varieties.length ?? 0

  const selectedCropLabels = useMemo(() => {
    if (selectedCrops.length === 0) {
      return 'All crops'
    }
    return selectedCrops.join(', ')
  }, [selectedCrops])

  const toggleCropSelection = (crop: string) => {
    setSelectedCrops(prev => {
      if (prev.includes(crop)) {
        return prev.filter(item => item !== crop)
      }
      return [...prev, crop]
    })
  }

  const handleExtractVarieties = async () => {
    setIsExtracting(true)
    setErrorMessage(null)
    setSuccessMessage(null)

    const payload: VarietyExtractionParams = {}
    if (selectedCrops.length > 0) {
      payload.crops = selectedCrops.map(crop => crop.toLowerCase())
    }

    try {
      const response = await adminAPI.extractVarietiesForValidation(payload)

      if (response.status === 'success') {
        setExtractionResult(response.data)
        setSessionId(response.data.session_id)
        setSuccessMessage(response.message || 'Varieties extracted successfully.')

        if (response.data.session_id && response.data.varieties.length > 0) {
          setModalOpen(true)
        } else {
          setModalOpen(false)
        }
      } else {
        setErrorMessage(response.message || 'Failed to extract varieties.')
      }
    } catch (error) {
      console.error('Variety extraction failed', error)
      setErrorMessage('Extraction failed. Check backend logs for details.')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleValidationSubmit = async (varieties: ExtractedVariety[]) => {
    if (!sessionId) {
      setErrorMessage('Session not found. Please extract varieties again.')
      return
    }

    setIsValidating(true)
    setErrorMessage(null)

    try {
      const response = await adminAPI.validateSelectedVarieties({
        session_id: sessionId,
        selected_varieties: varieties,
      })

      if (response.status === 'success') {
        const data: VarietyValidationResult = response.data
        setSuccessMessage(response.message || `Saved ${data.varieties_saved} varieties.`)
        setModalOpen(false)
        setExtractionResult(null)
      } else {
        setErrorMessage(response.message || 'Validation failed.')
      }
    } catch (error) {
      console.error('Variety validation failed', error)
      setErrorMessage('Validation failed. Please try again.')
    } finally {
      setIsValidating(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom display="flex" alignItems="center" gap={2}>
          <AgricultureIcon color="primary" />
          Varieties Extraction Workflow
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: '800px' }}>
          Launch the varieties extraction pipeline, review detected varieties, and validate the ones that meet quality standards before saving them into the knowledge base.
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <FilterIcon color="primary" />
              <Typography variant="h6">Extraction Filters</Typography>
            </Box>
          }
        />
        <CardContent>
          <Box mb={3}>
            <Typography variant="subtitle2" gutterBottom>
              Target Crops
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Select specific crops or leave empty to process all available crops.
            </Typography>
            
            <FormControl component="fieldset" variant="standard">
              <FormLabel component="legend">Available Crops</FormLabel>
              <FormGroup>
                <Grid container spacing={1}>
                  {cropOptions.map(crop => (
                    <Grid item xs={6} sm={4} md={3} key={crop}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={selectedCrops.includes(crop)}
                            onChange={() => toggleCropSelection(crop)}
                            size="small"
                          />
                        }
                        label={crop}
                      />
                    </Grid>
                  ))}
                </Grid>
              </FormGroup>
            </FormControl>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box display="flex" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={2}>
            <Typography variant="body2" color="text.secondary">
              <strong>Selected Crops:</strong> {selectedCropLabels}
            </Typography>
            <Button
              variant="contained"
              onClick={handleExtractVarieties}
              disabled={isExtracting}
              startIcon={isExtracting ? <CircularProgress size={20} /> : <DownloadIcon />}
              size="large"
            >
              {isExtracting ? 'Extracting...' : 'Extract Varieties'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {extractionResult && (
        <Card sx={{ mb: 3 }}>
          <CardHeader
            title={
              <Box display="flex" alignItems="center" gap={1}>
                <CheckCircleIcon color="primary" />
                <Typography variant="h6">Extraction Summary</Typography>
              </Box>
            }
          />
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Box sx={{ p: 2, border: 1, borderColor: 'primary.main', borderRadius: 1, bgcolor: 'primary.50' }}>
                  <Typography variant="caption" color="primary" sx={{ textTransform: 'uppercase', fontWeight: 'bold' }}>
                    Session
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {sessionId || '—'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 'bold' }}>
                    Varieties Found
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 0.5 }}>
                    {totalVarietiesExtracted}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 'bold' }}>
                    Documents Processed
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 0.5 }}>
                    {extractionResult.stats.documents_processed}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {(errorMessage || successMessage) && (
        <Alert 
          severity={errorMessage ? 'error' : 'success'}
          icon={errorMessage ? <ErrorIcon /> : <CheckCircleIcon />}
          sx={{ mb: 3 }}
        >
          {errorMessage || successMessage}
        </Alert>
      )}

      <VarietyValidationModal
        isOpen={modalOpen}
        sessionId={sessionId}
        varieties={extractionResult?.varieties || []}
        onClose={() => setModalOpen(false)}
        onSubmit={handleValidationSubmit}
        isSubmitting={isValidating}
      />
    </Box>
  )
}

export default AdminVarieties
