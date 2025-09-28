/**
 * Tests for EnhancedSearchForm Component
 * Tests enhanced search form functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import EnhancedSearchForm, { SearchParams } from '../EnhancedSearchForm'

describe('EnhancedSearchForm', () => {
  const defaultProps = {
    onSearch: jest.fn(),
    availableSeasons: ['current', 'rainy_season', 'dry_season'],
    availableCrops: ['maize', 'beans', 'groundnuts'],
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render with default values', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    expect(screen.getByText('Crop Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Search Mode')).toBeInTheDocument()
    expect(screen.getByText('Location')).toBeInTheDocument()
    expect(screen.getByText('Season')).toBeInTheDocument()
  })

  it('should initialize with current location if provided', () => {
    const currentLocation = { lat: -13.9833, lon: 33.7833, name: 'Lilongwe' }
    render(<EnhancedSearchForm {...defaultProps} currentLocation={currentLocation} />)
    
    expect(screen.getByDisplayValue('Lilongwe')).toBeInTheDocument()
  })

  it('should initialize with last search params if provided', () => {
    const lastSearchParams: SearchParams = {
      location: 'Blantyre',
      season: 'rainy_season',
      searchMode: { type: 'specific_crop', cropName: 'maize' }
    }
    render(<EnhancedSearchForm {...defaultProps} lastSearchParams={lastSearchParams} />)
    
    expect(screen.getByDisplayValue('Blantyre')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Rainy Season')).toBeInTheDocument()
  })

  it('should call onSearch with correct parameters when search button is clicked', () => {
    const onSearch = jest.fn()
    render(<EnhancedSearchForm {...defaultProps} onSearch={onSearch} />)
    
    const searchButton = screen.getByRole('button', { name: /get crop recommendations/i })
    fireEvent.click(searchButton)
    
    expect(onSearch).toHaveBeenCalledWith({
      location: 'Lilongwe',
      season: 'current',
      searchMode: { type: 'all_crops' },
      coordinates: undefined
    })
  })

  it('should call onSearch with specific crop parameters when specific crop mode is selected', async () => {
    const onSearch = jest.fn()
    render(<EnhancedSearchForm {...defaultProps} onSearch={onSearch} />)
    
    // Switch to specific crop mode
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    // Enter crop name
    const cropInput = screen.getByPlaceholderText(/enter crop name/i)
    fireEvent.change(cropInput, { target: { value: 'maize' } })
    
    // Click search
    const searchButton = screen.getByRole('button', { name: /search maize/i })
    fireEvent.click(searchButton)
    
    expect(onSearch).toHaveBeenCalledWith({
      location: 'Lilongwe',
      season: 'current',
      searchMode: { type: 'specific_crop', cropName: 'maize' },
      coordinates: undefined
    })
  })

  it('should handle custom coordinates', async () => {
    const onSearch = jest.fn()
    render(<EnhancedSearchForm {...defaultProps} onSearch={onSearch} />)
    
    // Select custom coordinates
    const locationSelect = screen.getByLabelText('Select Location')
    fireEvent.mouseDown(locationSelect)
    const customOption = screen.getByText('Custom Coordinates')
    fireEvent.click(customOption)
    
    // Enter coordinates
    const coordInput = screen.getByPlaceholderText(/e.g., -13.9833, 33.7833/i)
    fireEvent.change(coordInput, { target: { value: '-13.9833, 33.7833' } })
    
    // Click search
    const searchButton = screen.getByRole('button', { name: /get crop recommendations/i })
    fireEvent.click(searchButton)
    
    expect(onSearch).toHaveBeenCalledWith({
      location: '-13.9833, 33.7833',
      season: 'current',
      searchMode: { type: 'all_crops' },
      coordinates: { lat: -13.9833, lon: 33.7833 }
    })
  })

  it('should show error for invalid coordinates', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    // Select custom coordinates
    const locationSelect = screen.getByLabelText('Select Location')
    fireEvent.mouseDown(locationSelect)
    const customOption = screen.getByText('Custom Coordinates')
    fireEvent.click(customOption)
    
    // Enter invalid coordinates
    const coordInput = screen.getByPlaceholderText(/e.g., -13.9833, 33.7833/i)
    fireEvent.change(coordInput, { target: { value: 'invalid coordinates' } })
    
    expect(screen.getByText('Invalid coordinates format')).toBeInTheDocument()
  })

  it('should disable search button when loading', () => {
    render(<EnhancedSearchForm {...defaultProps} loading={true} />)
    
    const searchButton = screen.getByRole('button', { name: /searching/i })
    expect(searchButton).toBeDisabled()
  })

  it('should disable search button when specific crop mode is selected without crop name', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    // Switch to specific crop mode
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    const searchButton = screen.getByRole('button', { name: /search crop/i })
    expect(searchButton).toBeDisabled()
  })

  it('should show validation warning for specific crop mode without crop name', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    // Switch to specific crop mode
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    expect(screen.getByText(/please select a specific crop/i)).toBeInTheDocument()
  })

  it('should show current location chip when current location is provided', () => {
    const currentLocation = { lat: -13.9833, lon: 33.7833, name: 'Lilongwe' }
    render(<EnhancedSearchForm {...defaultProps} currentLocation={currentLocation} />)
    
    expect(screen.getByText(/current: lilongwe/i)).toBeInTheDocument()
  })

  it('should show search summary with current parameters', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    expect(screen.getByText('Search Summary')).toBeInTheDocument()
    expect(screen.getByText('Lilongwe')).toBeInTheDocument()
    expect(screen.getByText('Current Season')).toBeInTheDocument()
    expect(screen.getByText('All Crops')).toBeInTheDocument()
  })

  it('should update search summary when parameters change', async () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    // Change season
    const seasonSelect = screen.getByLabelText('Select Season')
    fireEvent.mouseDown(seasonSelect)
    const rainySeasonOption = screen.getByText('Rainy Season')
    fireEvent.click(rainySeasonOption)
    
    // Switch to specific crop mode
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    // Enter crop name
    const cropInput = screen.getByPlaceholderText(/enter crop name/i)
    fireEvent.change(cropInput, { target: { value: 'maize' } })
    
    await waitFor(() => {
      expect(screen.getByText('Rainy Season')).toBeInTheDocument()
      expect(screen.getByText('Specific: maize')).toBeInTheDocument()
    })
  })

  it('should handle season change', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    const seasonSelect = screen.getByLabelText('Select Season')
    fireEvent.mouseDown(seasonSelect)
    const rainySeasonOption = screen.getByText('Rainy Season')
    fireEvent.click(rainySeasonOption)
    
    expect(screen.getByDisplayValue('Rainy Season')).toBeInTheDocument()
  })

  it('should show season descriptions', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    expect(screen.getByText(/recommendations based on current weather/i)).toBeInTheDocument()
  })

  it('should handle location change', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    const locationSelect = screen.getByLabelText('Select Location')
    fireEvent.mouseDown(locationSelect)
    const blantyreOption = screen.getByText('Blantyre')
    fireEvent.click(blantyreOption)
    
    expect(screen.getByDisplayValue('Blantyre')).toBeInTheDocument()
  })

  it('should handle custom location input', () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    const customLocationInput = screen.getByLabelText('Custom Location')
    fireEvent.change(customLocationInput, { target: { value: 'Custom City' } })
    
    expect(screen.getByDisplayValue('Custom City')).toBeInTheDocument()
  })

  it('should show loading state on search button when loading', () => {
    render(<EnhancedSearchForm {...defaultProps} loading={true} />)
    
    expect(screen.getByText('Searching...')).toBeInTheDocument()
  })

  it('should show specific crop search button text when specific crop mode is selected', async () => {
    render(<EnhancedSearchForm {...defaultProps} />)
    
    // Switch to specific crop mode
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    // Enter crop name
    const cropInput = screen.getByPlaceholderText(/enter crop name/i)
    fireEvent.change(cropInput, { target: { value: 'maize' } })
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /search maize/i })).toBeInTheDocument()
    })
  })
})
