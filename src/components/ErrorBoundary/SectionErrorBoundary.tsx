import React, { Component, ErrorInfo, ReactNode } from 'react'
import {
  Alert,
  AlertTitle,
  Box,
  Typography,
} from '@mui/material'
import {
  Warning as WarningIcon,
} from '@mui/icons-material'

interface Props {
  children: ReactNode
  sectionName: string
  fallbackMessage?: string
}

interface State {
  hasError: boolean
  error: Error | null
}

class SectionErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`SectionErrorBoundary caught an error in ${this.props.sectionName}:`, error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      const { sectionName, fallbackMessage } = this.props

      return (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <AlertTitle>
            <Box display="flex" alignItems="center" gap={1}>
              <WarningIcon />
              {sectionName} - Display Error
            </Box>
          </AlertTitle>
          <Typography variant="body2">
            {fallbackMessage || `There was an error displaying the ${sectionName.toLowerCase()} section. The data might be malformed.`}
          </Typography>
        </Alert>
      )
    }

    return this.props.children
  }
}

export default SectionErrorBoundary
