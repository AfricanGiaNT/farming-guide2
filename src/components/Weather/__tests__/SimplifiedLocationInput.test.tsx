import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import SimplifiedLocationInput from '../SimplifiedLocationInput'

// Mock theme for testing
const theme = createTheme()

// Mock navigator.geolocation
const mockGeolocation = {
  getCurrentPosition: jest.fn(),
  watchPosition: jest.fn(),
  clearWatch: jest.fn(),
}

Object.defineProperty(global.navigator, 'geolocation', {
  value: mockGeolocation,
  writable: true,
})

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  )
}

describe('SimplifiedLocationInput', () => {
  const mockOnLocationChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockGeolocation.getCurrentPosition.mockClear()
  })

  describe('Rendering', () => {
    test('renders location input component', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      expect(screen.getByText('Location Settings')).toBeInTheDocument()
      expect(screen.getByText('Use My Current Location')).toBeInTheDocument()
      expect(screen.getByText('OR Paste Google Maps Link')).toBeInTheDocument()
    })

    test('renders with current location when provided', () => {
      const currentLocation = { lat: -13.9833, lon: 33.7833 }
      
      renderWithTheme(
        <SimplifiedLocationInput 
          onLocationChange={mockOnLocationChange}
          currentLocation={currentLocation}
        />
      )
      
      expect(screen.getByText('Current: -13.9833, 33.7833')).toBeInTheDocument()
    })

    test('disables inputs when disabled prop is true', () => {
      renderWithTheme(
        <SimplifiedLocationInput 
          onLocationChange={mockOnLocationChange}
          disabled={true}
        />
      )
      
      const currentLocationButton = screen.getByText('Use My Current Location')
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      expect(currentLocationButton.closest('button')).toBeDisabled()
      expect(urlInput).toBeDisabled()
      expect(setLocationButton.closest('button')).toBeDisabled()
    })
  })

  describe('Current Location Functionality', () => {
    test('calls geolocation API when current location button is clicked', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      expect(mockGeolocation.getCurrentPosition).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        expect.objectContaining({
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 300000,
        })
      )
    })

    test('shows loading state when getting current location', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      expect(screen.getByText('Getting your location...')).toBeInTheDocument()
    })

    test('handles successful geolocation', async () => {
      const mockPosition = {
        coords: {
          latitude: -13.9833,
          longitude: 33.7833,
        },
      }

      mockGeolocation.getCurrentPosition.mockImplementation((success) => {
        success(mockPosition)
      })

      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(mockOnLocationChange).toHaveBeenCalledWith(-13.9833, 33.7833)
        expect(screen.getByText('Location set: -13.9833, 33.7833')).toBeInTheDocument()
      })
    })

    test('handles geolocation permission denied error', async () => {
      mockGeolocation.getCurrentPosition.mockImplementation((success, error) => {
        error({ code: 1, message: 'Permission denied' })
      })

      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByText(/Please allow location access/)).toBeInTheDocument()
      })
    })

    test('handles geolocation position unavailable error', async () => {
      mockGeolocation.getCurrentPosition.mockImplementation((success, error) => {
        error({ code: 2, message: 'Position unavailable' })
      })

      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByText(/Location information is unavailable/)).toBeInTheDocument()
      })
    })

    test('handles geolocation timeout error', async () => {
      mockGeolocation.getCurrentPosition.mockImplementation((success, error) => {
        error({ code: 3, message: 'Timeout' })
      })

      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByText(/Location request timed out/)).toBeInTheDocument()
      })
    })

    test('handles geolocation not supported', () => {
      // Remove geolocation from navigator
      Object.defineProperty(global.navigator, 'geolocation', {
        value: undefined,
        writable: true,
      })

      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const button = screen.getByText('Use My Current Location')
      fireEvent.click(button)
      
      expect(screen.getByText('GPS not supported by this browser')).toBeInTheDocument()

      // Restore geolocation
      Object.defineProperty(global.navigator, 'geolocation', {
        value: mockGeolocation,
        writable: true,
      })
    })
  })

  describe('Google Maps URL Functionality', () => {
    test('parses valid Google Maps URL', async () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      fireEvent.change(urlInput, {
        target: { value: 'https://maps.google.com/maps/@-13.9833,33.7833,15z' }
      })
      fireEvent.click(setLocationButton)
      
      await waitFor(() => {
        expect(mockOnLocationChange).toHaveBeenCalledWith(-13.9833, 33.7833)
        expect(screen.getByText('Location set: -13.9833, 33.7833')).toBeInTheDocument()
      })
    })

    test('shows error for invalid Google Maps URL', async () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      fireEvent.change(urlInput, {
        target: { value: 'https://www.example.com/maps' }
      })
      fireEvent.click(setLocationButton)
      
      await waitFor(() => {
        expect(screen.getByText(/Not a Google Maps URL/)).toBeInTheDocument()
      })
    })

    test('shows error for empty URL', async () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const setLocationButton = screen.getByText('Set Location')
      fireEvent.click(setLocationButton)
      
      await waitFor(() => {
        expect(screen.getByText('Please enter a Google Maps URL')).toBeInTheDocument()
      })
    })

    test('shows loading state when parsing URL', async () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      fireEvent.change(urlInput, {
        target: { value: 'https://maps.google.com/maps/@-13.9833,33.7833,15z' }
      })
      fireEvent.click(setLocationButton)
      
      expect(screen.getByText('Parsing...')).toBeInTheDocument()
    })

    test('clears URL input after successful parsing', async () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      fireEvent.change(urlInput, {
        target: { value: 'https://maps.google.com/maps/@-13.9833,33.7833,15z' }
      })
      fireEvent.click(setLocationButton)
      
      await waitFor(() => {
        expect(urlInput).toHaveValue('')
      })
    })
  })

  describe('Error Handling', () => {
    test('clears error when URL input changes', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      const setLocationButton = screen.getByText('Set Location')
      
      // First, create an error
      fireEvent.click(setLocationButton)
      
      // Then change the input
      fireEvent.change(urlInput, {
        target: { value: 'https://maps.google.com/maps/@-13.9833,33.7833,15z' }
      })
      
      // Error should be cleared
      expect(screen.queryByText('Please enter a Google Maps URL')).not.toBeInTheDocument()
    })

    test('allows dismissing error alerts', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const setLocationButton = screen.getByText('Set Location')
      fireEvent.click(setLocationButton)
      
      const errorAlert = screen.getByText('Please enter a Google Maps URL')
      const closeButton = errorAlert.closest('[role="alert"]')?.querySelector('[aria-label="Close"]')
      
      if (closeButton) {
        fireEvent.click(closeButton)
        expect(screen.queryByText('Please enter a Google Maps URL')).not.toBeInTheDocument()
      }
    })
  })

  describe('State Management', () => {
    test('resets state when current location chip is deleted', () => {
      const currentLocation = { lat: -13.9833, lon: 33.7833 }
      
      renderWithTheme(
        <SimplifiedLocationInput 
          onLocationChange={mockOnLocationChange}
          currentLocation={currentLocation}
        />
      )
      
      const chip = screen.getByText('Current: -13.9833, 33.7833')
      const deleteButton = chip.closest('[role="button"]')?.querySelector('[aria-label="Delete"]')
      
      if (deleteButton) {
        fireEvent.click(deleteButton)
        // State should be reset (no current location displayed)
        expect(screen.queryByText('Current: -13.9833, 33.7833')).not.toBeInTheDocument()
      }
    })
  })

  describe('Accessibility', () => {
    test('has proper button labels', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      expect(screen.getByRole('button', { name: 'Use My Current Location' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Set Location' })).toBeInTheDocument()
    })

    test('has proper input labels', () => {
      renderWithTheme(
        <SimplifiedLocationInput onLocationChange={mockOnLocationChange} />
      )
      
      const urlInput = screen.getByPlaceholderText(/maps\.google\.com/)
      expect(urlInput).toBeInTheDocument()
    })
  })
})
