/**
 * Tests for SearchModeToggle Component
 * Tests search mode toggle functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SearchModeToggle, { SearchMode } from '../SearchModeToggle'

describe('SearchModeToggle', () => {
  const defaultProps = {
    searchMode: { type: 'all_crops' as const },
    onSearchModeChange: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render with default all crops mode', () => {
    render(<SearchModeToggle {...defaultProps} />)
    
    expect(screen.getByText('Search Mode')).toBeInTheDocument()
    expect(screen.getByText('All Crops')).toBeInTheDocument()
    expect(screen.getByText('Specific Crop')).toBeInTheDocument()
  })

  it('should switch to specific crop mode when clicked', () => {
    const onSearchModeChange = jest.fn()
    render(<SearchModeToggle {...defaultProps} onSearchModeChange={onSearchModeChange} />)
    
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    fireEvent.click(specificCropButton)
    
    expect(onSearchModeChange).toHaveBeenCalledWith({
      type: 'specific_crop',
      cropName: undefined
    })
  })

  it('should switch to all crops mode when clicked', () => {
    const onSearchModeChange = jest.fn()
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const },
      onSearchModeChange
    }
    render(<SearchModeToggle {...props} />)
    
    const allCropsButton = screen.getByRole('button', { name: /all crops/i })
    fireEvent.click(allCropsButton)
    
    expect(onSearchModeChange).toHaveBeenCalledWith({
      type: 'all_crops',
      cropName: undefined
    })
  })

  it('should show crop name input when specific crop mode is selected', async () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const }
    }
    render(<SearchModeToggle {...props} />)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/enter crop name/i)).toBeInTheDocument()
    })
  })

  it('should hide crop name input when all crops mode is selected', () => {
    render(<SearchModeToggle {...defaultProps} />)
    
    expect(screen.queryByPlaceholderText(/enter crop name/i)).not.toBeInTheDocument()
  })

  it('should display available crops as chips', () => {
    const availableCrops = ['maize', 'beans', 'groundnuts']
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const },
      availableCrops
    }
    render(<SearchModeToggle {...props} />)
    
    expect(screen.getByText('Popular crops:')).toBeInTheDocument()
    expect(screen.getByText('maize')).toBeInTheDocument()
    expect(screen.getByText('beans')).toBeInTheDocument()
    expect(screen.getByText('groundnuts')).toBeInTheDocument()
  })

  it('should select crop when chip is clicked', () => {
    const onSearchModeChange = jest.fn()
    const availableCrops = ['maize', 'beans', 'groundnuts']
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const },
      onSearchModeChange,
      availableCrops
    }
    render(<SearchModeToggle {...props} />)
    
    const maizeChip = screen.getByText('maize')
    fireEvent.click(maizeChip)
    
    expect(onSearchModeChange).toHaveBeenCalledWith({
      type: 'specific_crop',
      cropName: 'maize'
    })
  })

  it('should update crop name when input is changed', () => {
    const onSearchModeChange = jest.fn()
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const },
      onSearchModeChange
    }
    render(<SearchModeToggle {...props} />)
    
    const cropInput = screen.getByPlaceholderText(/enter crop name/i)
    fireEvent.change(cropInput, { target: { value: 'tomato' } })
    
    expect(onSearchModeChange).toHaveBeenCalledWith({
      type: 'specific_crop',
      cropName: 'tomato'
    })
  })

  it('should show validation warning when specific crop mode is selected without crop name', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const }
    }
    render(<SearchModeToggle {...props} />)
    
    expect(screen.getByText(/please enter a crop name/i)).toBeInTheDocument()
  })

  it('should not show validation warning when crop name is provided', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' }
    }
    render(<SearchModeToggle {...props} />)
    
    expect(screen.queryByText(/please enter a crop name/i)).not.toBeInTheDocument()
  })

  it('should show current selection summary', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const, cropName: 'maize' }
    }
    render(<SearchModeToggle {...props} />)
    
    expect(screen.getByText('Current Selection:')).toBeInTheDocument()
    expect(screen.getByText('Specific Crop')).toBeInTheDocument()
    expect(screen.getByText('maize')).toBeInTheDocument()
  })

  it('should expand advanced options when expand button is clicked', async () => {
    render(<SearchModeToggle {...defaultProps} showAdvanced={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more options/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('Advanced Options')).toBeInTheDocument()
    })
  })

  it('should collapse advanced options when expand button is clicked again', async () => {
    render(<SearchModeToggle {...defaultProps} showAdvanced={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more options/i })
    
    // Expand first
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.getByText('Advanced Options')).toBeInTheDocument()
    })
    
    // Collapse
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.queryByText('Advanced Options')).not.toBeInTheDocument()
    })
  })

  it('should be disabled when disabled prop is true', () => {
    render(<SearchModeToggle {...defaultProps} disabled={true} />)
    
    const allCropsButton = screen.getByRole('button', { name: /all crops/i })
    const specificCropButton = screen.getByRole('button', { name: /specific crop/i })
    
    expect(allCropsButton).toBeDisabled()
    expect(specificCropButton).toBeDisabled()
  })

  it('should show mode descriptions', () => {
    render(<SearchModeToggle {...defaultProps} />)
    
    expect(screen.getByText(/get recommendations for all suitable crops/i)).toBeInTheDocument()
  })

  it('should show specific crop description when specific crop mode is selected', () => {
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const }
    }
    render(<SearchModeToggle {...props} />)
    
    expect(screen.getByText(/get detailed analysis for a specific crop/i)).toBeInTheDocument()
  })

  it('should limit displayed crops to 8', () => {
    const availableCrops = ['maize', 'beans', 'groundnuts', 'rice', 'sorghum', 'millet', 'cassava', 'sweet potato', 'tomato', 'onion']
    const props = {
      ...defaultProps,
      searchMode: { type: 'specific_crop' as const },
      availableCrops
    }
    render(<SearchModeToggle {...props} />)
    
    // Should show first 8 crops
    expect(screen.getByText('maize')).toBeInTheDocument()
    expect(screen.getByText('beans')).toBeInTheDocument()
    expect(screen.getByText('groundnuts')).toBeInTheDocument()
    expect(screen.getByText('rice')).toBeInTheDocument()
    expect(screen.getByText('sorghum')).toBeInTheDocument()
    expect(screen.getByText('millet')).toBeInTheDocument()
    expect(screen.getByText('cassava')).toBeInTheDocument()
    expect(screen.getByText('sweet potato')).toBeInTheDocument()
    
    // Should not show the 9th and 10th crops
    expect(screen.queryByText('tomato')).not.toBeInTheDocument()
    expect(screen.queryByText('onion')).not.toBeInTheDocument()
  })
})
