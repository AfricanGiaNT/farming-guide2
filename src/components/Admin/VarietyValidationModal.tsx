import React, { useEffect, useMemo, useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material'
import {
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Search as SearchIcon,
  SelectAll as SelectAllIcon,
  Deselect as DeselectIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material'
import { ExtractedVariety } from '../../services/api'

interface VarietyValidationModalProps {
  isOpen: boolean
  sessionId: string | null
  varieties: ExtractedVariety[]
  onClose: () => void
  onSubmit: (selectedVarieties: ExtractedVariety[]) => Promise<void> | void
  isSubmitting?: boolean
}

type SelectableVariety = ExtractedVariety & { _selectionKey: string }

const VarietyValidationModal: React.FC<VarietyValidationModalProps> = ({
  isOpen,
  sessionId,
  varieties,
  onClose,
  onSubmit,
  isSubmitting = false,
}) => {
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!isOpen) {
      setSelectedKeys(new Set())
      setSearchTerm('')
    }
  }, [isOpen])

  useEffect(() => {
    // Reset selection when a new session is loaded
    setSelectedKeys(new Set())
  }, [sessionId])

  const toggleSelection = (key: string) => {
    setSelectedKeys(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const selectableVarieties: SelectableVariety[] = useMemo(
    () =>
      varieties.map((variety, index) => ({
        ...variety,
        _selectionKey: `${variety.variety_name || 'variety'}-${variety.crop_name}-${index}`,
      })),
    [varieties]
  )

  const filteredVarieties: SelectableVariety[] = useMemo(() => {
    return selectableVarieties
      .filter(variety => {
        if (!searchTerm) return true
        const haystack = [
          variety.variety_name,
          variety.crop_name,
          variety.variety_type,
          variety.source_document,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
        return haystack.includes(searchTerm.toLowerCase())
      })
  }, [selectableVarieties, searchTerm])

  const handleSelectAll = () => {
    setSelectedKeys(new Set(filteredVarieties.map(v => v._selectionKey)))
  }

  const handleDeselectAll = () => {
    setSelectedKeys(new Set())
  }

  const selectedVarieties = selectableVarieties.filter(variety => selectedKeys.has(variety._selectionKey))
  const totalSelected = selectedVarieties.length

  const handleSubmit = async () => {
    if (selectedVarieties.length === 0) {
      return
    }

    await onSubmit(selectedVarieties.map(({ _selectionKey, ...rest }) => rest))
  }

  const renderConfidenceBadge = (score: number | undefined) => {
    if (typeof score !== 'number') {
      return <Chip label="No score" size="small" variant="outlined" />
    }

    const confidenceColor = score >= 80 ? 'success' : score >= 60 ? 'warning' : 'error'

    return (
      <Chip 
        label={`Confidence ${score}%`} 
        size="small" 
        color={confidenceColor}
        variant="filled"
      />
    )
  }

  if (!isOpen) {
    return null
  }

  return (
    <Dialog 
      open={isOpen} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <ShieldIcon color="primary" />
            <Box>
              <Typography variant="h6">Validate Extracted Varieties</Typography>
              <Typography variant="body2" color="text.secondary">
                Session ID: {sessionId || '—'}
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box mb={3}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Stage 2 of 3</strong> · Review and select the varieties you want to add to the database
            </Typography>
          </Alert>
          
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="body2" color="text.secondary">
              {totalSelected} selected · {filteredVarieties.length} varieties detected
            </Typography>
          </Box>

          <Box display="flex" gap={2} mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search varieties, crops, or sources"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
            <Button
              variant="outlined"
              startIcon={<SelectAllIcon />}
              onClick={handleSelectAll}
              size="small"
            >
              Select All
            </Button>
            <Button
              variant="outlined"
              startIcon={<DeselectIcon />}
              onClick={handleDeselectAll}
              size="small"
            >
              Deselect All
            </Button>
          </Box>
        </Box>

        <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
          {filteredVarieties.length === 0 ? (
            <Alert severity="warning">
              No varieties match your search filter.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {filteredVarieties.map(variety => {
                const selected = selectedKeys.has(variety._selectionKey)
                const confidence = variety.confidence_score ?? 0
                const previewContext = variety.context ? 
                  `${variety.context.slice(0, 160)}${variety.context.length > 160 ? '…' : ''}` : 
                  'No context available'

                return (
                  <Grid item xs={12} key={variety._selectionKey}>
                    <Card 
                      sx={{ 
                        border: selected ? 2 : 1,
                        borderColor: selected ? 'primary.main' : 'divider',
                        backgroundColor: selected ? 'primary.50' : 'background.paper',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          boxShadow: 2,
                        }
                      }}
                      onClick={() => toggleSelection(variety._selectionKey)}
                    >
                      <CardContent>
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                          <Box display="flex" alignItems="center" gap={2}>
                            {selected ? (
                              <CheckCircleIcon color="primary" />
                            ) : (
                              <RadioButtonUncheckedIcon color="action" />
                            )}
                            <Box>
                              <Typography variant="h6">
                                {variety.variety_name || 'Unnamed Variety'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                                {variety.crop_name}
                              </Typography>
                            </Box>
                          </Box>
                          {renderConfidenceBadge(confidence)}
                        </Box>

                        <Divider sx={{ my: 1 }} />

                        <Grid container spacing={2} mb={2}>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                              Variety Type
                            </Typography>
                            <Typography variant="body2">
                              {variety.variety_type || '—'}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                              Yield Potential
                            </Typography>
                            <Typography variant="body2">
                              {variety.yield_potential || '—'}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                              Maturity Days
                            </Typography>
                            <Typography variant="body2">
                              {variety.maturity_days ?? '—'}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                              Source
                            </Typography>
                            <Typography variant="body2">
                              {variety.source_document || '—'}
                            </Typography>
                          </Grid>
                        </Grid>

                        <Box>
                          <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                            Context Preview
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {previewContext}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              })}
            </Grid>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
          Selected varieties will be saved with <strong>validated</strong> status.
        </Typography>
        <Button onClick={onClose} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={isSubmitting || selectedVarieties.length === 0}
          variant="contained"
          startIcon={isSubmitting ? <CircularProgress size={16} /> : <ShieldIcon />}
        >
          {isSubmitting ? 'Saving...' : `Save ${selectedVarieties.length || ''} Varieties`}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default VarietyValidationModal
