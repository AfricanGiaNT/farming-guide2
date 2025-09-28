import React, { Component, ErrorInfo, ReactNode } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Alert,
  AlertTitle,
  Divider,
} from '@mui/material'
import {
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material'

interface Props {
  children: ReactNode
  fallbackTitle?: string
  fallbackMessage?: string
  onRetry?: () => void
  showDetails?: boolean
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class CropDataErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    console.error('CropDataErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })

    // Log to external service if available
    this.logErrorToService(error, errorInfo)
  }

  private logErrorToService(error: Error, errorInfo: ErrorInfo) {
    // In a real application, you would send this to an error reporting service
    // like Sentry, LogRocket, or your own logging service
    try {
      const errorData = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }
      
      // For now, just log to console
      console.error('Error logged:', errorData)
      
      // In production, you might send this to your error service:
      // errorReportingService.log(errorData)
    } catch (loggingError) {
      console.error('Failed to log error:', loggingError)
    }
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })

    if (this.props.onRetry) {
      this.props.onRetry()
    }
  }

  private handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      const { fallbackTitle, fallbackMessage, showDetails = false } = this.props
      const { error, errorInfo } = this.state

      return (
        <Card sx={{ mb: 3, border: '1px solid', borderColor: 'error.main' }}>
          <CardContent>
            <Alert severity="error" sx={{ mb: 2 }}>
              <AlertTitle>
                <Box display="flex" alignItems="center" gap={1}>
                  <ErrorIcon />
                  {fallbackTitle || 'Data Processing Error'}
                </Box>
              </AlertTitle>
              {fallbackMessage || 'There was an error processing the crop data. This might be due to malformed data from the server.'}
            </Alert>

            <Box display="flex" gap={2} mb={2}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={this.handleRetry}
                color="primary"
              >
                Try Again
              </Button>
              <Button
                variant="outlined"
                onClick={this.handleReload}
                color="secondary"
              >
                Reload Page
              </Button>
            </Box>

            {showDetails && error && (
              <>
                <Divider sx={{ my: 2 }} />
                <Box>
                  <Typography variant="h6" gutterBottom color="error">
                    <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Error Details
                  </Typography>
                  
                  <Typography variant="body2" component="pre" sx={{ 
                    backgroundColor: 'grey.100', 
                    p: 2, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontSize: '0.75rem',
                    fontFamily: 'monospace'
                  }}>
                    {error.message}
                  </Typography>

                  {errorInfo && (
                    <Box mt={2}>
                      <Typography variant="body2" fontWeight="bold" gutterBottom>
                        Component Stack:
                      </Typography>
                      <Typography variant="body2" component="pre" sx={{ 
                        backgroundColor: 'grey.100', 
                        p: 2, 
                        borderRadius: 1,
                        overflow: 'auto',
                        fontSize: '0.75rem',
                        fontFamily: 'monospace'
                      }}>
                        {errorInfo.componentStack}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </>
            )}

            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                If this error persists, please check your internet connection and try refreshing the page.
                If the problem continues, the server might be experiencing issues.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )
    }

    return this.props.children
  }
}

export default CropDataErrorBoundary
